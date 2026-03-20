
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

GROQ_API_KEY = "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"

@Client.on_message(filters.command(["ask", "ai"]))
async def ask_ai(client, message: Message):
    if len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        query = message.reply_to_message.text
    else:
        return await message.reply(
            "**🤖 AI Assistant**\n\n"
            "**Usage:**\n"
            "`/ask` your question here\n"
        )

    m = await message.reply("**🤖 Thinking...**")

    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Keep responses clear and concise."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data["choices"][0]["message"]["content"]
                    await m.edit(f"**🤖 AI Response:**\n\n{answer}\n\n_Powered by @Astro_AF_bot")
                else:
                    error = await resp.text()
                    await m.edit(f"**❌ API Error {resp.status}:** `{error}`")

    except Exception as e:
        await m.edit(f"**❌ Error:** `{e}`")
        print(f"AI Error: {e}")