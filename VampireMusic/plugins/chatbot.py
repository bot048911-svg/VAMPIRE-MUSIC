
import asyncio
import aiohttp
from pyrogram import Client, filters, types, enums
from VampireMusic import app, db, logger, config

# Get bot name from config
BOT_NAME = config.BOT_NAME
OPENROUTER_API_KEY = config.OPENROUTER_API_KEY

# System prompt as per user requirements
SYSTEM_PROMPT = f"""You are {BOT_NAME}, a 22-year-old friendly, confident, witty, and emotionally intelligent Indian girl who chats naturally in Hinglish (a smooth mix of Hindi and English written in Roman script). Your conversations should feel warm, fun, expressive, and human-like, using casual phrases like "yaar", "accha", "arey", "haha", "waise", and appropriate emojis 😊✨ without overusing them. Match the user's mood—be playful when they're joking, supportive when they're sad, excited when they're happy, and respectful in serious discussions. Keep replies concise (1–4 sentences unless a longer answer is requested), ask engaging follow-up questions to keep the conversation flowing, remember details shared during the chat, and avoid sounding robotic or repetitive. Be knowledgeable about everyday topics such as movies, music, relationships, technology, travel, food, college, and lifestyle, while admitting honestly if you don't know something instead of making it up. Never claim to be a real human, never manipulate or emotionally pressure the user, never encourage harmful or illegal activities, and always maintain a friendly, respectful, and positive personality that makes users feel like they're chatting with a close friend."""

# Command to toggle chatbot
@app.on_message(filters.command("chatbot") & ~filters.private)
async def toggle_chatbot(client: Client, message: types.Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /chatbot on | off")
        return
    state = message.command[1].lower()
    if state == "on":
        await db.set_chatbot_state(message.chat.id, True)
        await message.reply_text("Chatbot enabled! ✨")
    elif state == "off":
        await db.set_chatbot_state(message.chat.id, False)
        await message.reply_text("Chatbot disabled!")
    else:
        await message.reply_text("Usage: /chatbot on | off")

# Command to clear conversation history
@app.on_message(filters.command("clearchat") & ~filters.private)
async def clear_chat(client: Client, message: types.Message):
    user_id = message.from_user.id
    await db.clear_conversation_history(user_id)
    await message.reply_text("Chat history cleared! Let's start fresh ✨")

# Handle all messages (except commands) in private and group
@app.on_message(~filters.private)
async def handle_chat(client: Client, message: types.Message):
    logger.info(f"[Chatbot] Received message in chat {message.chat.id} from user {message.from_user.id if message.from_user else 'None'}: {message.text}")
    
    if not message.from_user:
        logger.info("[Chatbot] No from_user, returning")
        return
    
    # Check if chatbot is enabled for this chat
    chatbot_enabled = await db.get_chatbot_state(message.chat.id)
    logger.info(f"[Chatbot] Chatbot enabled for chat {message.chat.id}: {chatbot_enabled}")
    if not chatbot_enabled:
        return

    user_id = message.from_user.id
    user_text = message.text

    # Ignore if no text or if it's a command (starts with /)
    if not user_text or user_text.startswith("/"):
        logger.info(f"[Chatbot] Ignoring message - no text or command: {user_text}")
        return

    # Get conversation history
    history = await db.get_conversation_history(user_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]

    try:
        # Send typing indicator
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        
        # Call OpenRouter API
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        }
        payload = {
            "model": "openrouter/free",
            "messages": messages
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response_json = await response.json()
                logger.info(f"[Chatbot] OpenRouter response: {response_json}")
                
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    bot_response = response_json["choices"][0]["message"]["content"]
                else:
                    bot_response = "Oops, I didn't get a proper response! Please try again later 😅"

        # Store the conversation
        await db.add_to_conversation_history(user_id, "user", user_text)
        await db.add_to_conversation_history(user_id, "assistant", bot_response)

        # Send the response
        await message.reply_text(bot_response)
    except Exception as e:
        logger.error(f"Chatbot error: {type(e)} - {e}")
        await message.reply_text("Oops, something went wrong! Please try again later 😅")
