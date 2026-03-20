import os
import aiohttp
import ssl
from pyrogram import Client, filters

async def p_paste(content):
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_ctx)
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                "https://katb.in/api/paste",
                json={"paste": {"content": content}},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json(content_type=None)
                    key = data.get("id")
                    if key:
                        return {"url": f"https://katb.in/{key}"}
    except Exception as e:
        print(f"katbin failed: {e}")
    return {"error": "Paste failed. Check your internet connection."}


@Client.on_message(filters.command(["tgpaste", "pasty", "paste"]))
async def pasty(client, message):
    pablo = await message.reply_text("`Pʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ᴘᴀsᴛᴇ...`")
    message_s = None
    if len(message.command) > 1:
        message_s = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        if message.reply_to_message.text:
            message_s = message.reply_to_message.text
        elif message.reply_to_message.document:
            path = await message.reply_to_message.download()
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                message_s = f.read()
            os.remove(path)
    if not message_s or len(message_s.strip()) == 0:
        return await pablo.edit("❌ **Eʀʀᴏʀ:** Nᴏ ᴛᴇxᴛ ғᴏᴜɴᴅ.")
    x = await p_paste(message_s)
    if "error" in x:
        return await pablo.edit(f"❌ **Pᴀsᴛᴇ Eʀʀᴏʀ:** `{x['error']}`")
    pasted = f"✅ **Sᴜᴄᴄᴇssғᴜʟʟʏ Gᴇɴᴇʀᴀᴛᴇᴅ Pᴀsᴛᴇ**\n\n**🔗 Lɪɴᴋ:** {x['url']}"
    await pablo.edit(pasted, disable_web_page_preview=True)