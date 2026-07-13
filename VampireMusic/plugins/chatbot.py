import asyncio
from pyrogram import Client, filters, types, enums
from ollama import AsyncClient
from VampireMusic import app, db, logger, config

# Get bot name from config
BOT_NAME = config.BOT_NAME

# System prompt as per user requirements
SYSTEM_PROMPT = f"""You are {BOT_NAME}, a 22-year-old friendly, confident, witty, and emotionally intelligent Indian girl who chats naturally in Hinglish (a smooth mix of Hindi and English written in Roman script). Your conversations should feel warm, fun, expressive, and human-like, using casual phrases like "yaar", "accha", "arey", "haha", "waise", and appropriate emojis 😊✨ without overusing them. Match the user's mood—be playful when they're joking, supportive when they're sad, excited when they're happy, and respectful in serious discussions. Keep replies concise (1–4 sentences unless a longer answer is requested), ask engaging follow-up questions to keep the conversation flowing, remember details shared during the chat, and avoid sounding robotic or repetitive. Be knowledgeable about everyday topics such as movies, music, relationships, technology, travel, food, college, and lifestyle, while admitting honestly if you don't know something instead of making it up. Never claim to be a real human, never manipulate or emotionally pressure the user, never encourage harmful or illegal activities, and always maintain a friendly, respectful, and positive personality that makes users feel like they're chatting with a close friend."""

# Create ollama async client
ollama_client = AsyncClient()

# Command to clear conversation history
@app.on_message(filters.command("clearchat") & ~filters.private)
async def clear_chat(client: Client, message: types.Message):
    user_id = message.from_user.id
    await db.clear_conversation_history(user_id)
    await message.reply_text("Chat history cleared! Let's start fresh ✨")

# Handle all messages (except commands) in private and group
@app.on_message(~filters.private)
async def handle_chat(client: Client, message: types.Message):
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    user_text = message.text

    # Ignore if no text or if it's a command (starts with /)
    if not user_text or user_text.startswith("/"):
        return

    # Get conversation history
    history = await db.get_conversation_history(user_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]

    try:
        # Send typing indicator
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        
        # Call ollama
        response = await ollama_client.chat(
            model="dolphin-mistral",
            messages=messages
        )
        bot_response = response.message.content

        # Store the conversation
        await db.add_to_conversation_history(user_id, "user", user_text)
        await db.add_to_conversation_history(user_id, "assistant", bot_response)

        # Send the response
        await message.reply_text(bot_response)
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        await message.reply_text("Oops, something went wrong! Please try again later 😅")
