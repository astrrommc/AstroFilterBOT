from pyrogram import Client, filters
from pyrogram.types import *
from aiohttp import ClientSession
from io import BytesIO

ai_client = ClientSession()

async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"
    async with ai_client.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image

@Client.on_message(filters.command("carbon"))
async def carbon_func(b, message):
    # Check if text was provided with command e.g. /carbon some text
    if len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    # Check if replying to a message
    elif message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    # Nothing provided
    else:
        return await message.reply_text(
            "**How to use /carbon:**\n\n"
            "1. Reply to any text message and send /carbon\n"
            "2. Or send /carbon followed by your text\n\n"
            "**Example:** `/carbon print('Hello World')`"
        )

    m = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    try:
        carbon = await make_carbon(text)
        await m.edit("ᴜᴘʟᴏᴀᴅɪɴɢ...")
        await message.reply_photo(
            photo=carbon,
            caption="**ᴍᴀᴅᴇ ʙʏ: @Astro_AF_bot**",
        )
        carbon.close()
    except Exception as e:
        await m.edit(f"**Error:** `{e}`")
        return
    await m.delete()
