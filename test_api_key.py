import asyncio
import aiohttp

API_KEY = "WoIcX7Y4Ww63il66p3uS1EEV26BO3ry9"


async def test_openai():
    print("Testing OpenAI...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hi"}]
                }
            ) as resp:
                if resp.status == 200:
                    print("✅ OpenAI key valid!")
                    return True
                else:
                    print(f"❌ OpenAI failed: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False


async def test_gemini():
    print("Testing Google Gemini...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
                json={
                    "contents": [{"parts": [{"text": "Hi"}]}]
                }
            ) as resp:
                if resp.status == 200:
                    print("✅ Gemini key valid!")
                    return True
                else:
                    print(f"❌ Gemini failed: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return False


async def test_openrouter():
    print("Testing OpenRouter...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hi"}]
                }
            ) as resp:
                if resp.status == 200:
                    print("✅ OpenRouter key valid!")
                    return True
                else:
                    print(f"❌ OpenRouter failed: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ OpenRouter error: {e}")
        return False


async def test_anthropic():
    print("Testing Anthropic Claude...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Hi"}]
                }
            ) as resp:
                if resp.status == 200:
                    print("✅ Anthropic key valid!")
                    return True
                else:
                    print(f"❌ Anthropic failed: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Anthropic error: {e}")
        return False


async def main():
    print("Testing API key...")
    await test_openai()
    await test_gemini()
    await test_openrouter()
    await test_anthropic()


if __name__ == "__main__":
    asyncio.run(main())
