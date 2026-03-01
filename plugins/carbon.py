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
    if not message.reply_to_message:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴀᴋᴇ ᴄᴀʀʙᴏɴ.")
    if not message.reply_to_message.text:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴀᴋᴇ ᴄᴀʀʙᴏɴ.")
    m = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    try:
        carbon = await make_carbon(message.reply_to_message.text)
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
