# QR Code Generator & Scanner Plugin for AstroFilterBOT
import qrcode
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command(["qr", "qrcode"]), group=-1)
async def generate_qr(client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "**📱 QR Code Generator**\n\n"
            "**Usage:**\n`/qr` your text or link here"
        )

    text = message.text.split(None, 1)[1]
    m = await message.reply("**📱 Generating QR Code...**")

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = BytesIO()
        bio.name = "qrcode.png"
        img.save(bio, "PNG")
        bio.seek(0)

        await message.reply_photo(
            photo=bio,
            caption=f"**📱 QR Code**\n\n**Content:** `{text}`\n\n_Powered by @Astro_AF_bot_"
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"**❌ Error:** `{e}`")
        print(f"QR Error: {e}")


@Client.on_message(filters.command(["readqr", "scanqr", "qrscan"]), group=-1)
async def scan_qr_command(client, message: Message):
    target = message.reply_to_message if message.reply_to_message else None
    if not target or not target.photo:
        return await message.reply(
            "**📷 QR Code Scanner**\n\n"
            "**Usage:**\nSᴇɴᴅ ᴀ Pʜᴏᴛᴏ Wɪᴛʜ QR Cᴏᴅᴇ ᴀɴᴅ Cʜᴏᴏsᴇ **📱Scan QR Code**."
        )
    await do_scan(client, message, target)


@Client.on_message(filters.photo & filters.private, group=-1)
async def auto_scan_qr(client, message: Message):
    # Only scan if caption contains /readqr or /scanqr
    if message.caption and any(cmd in message.caption.lower() for cmd in ["/readqr", "/scanqr", "/qrscan"]):
        await do_scan(client, message, message)


async def do_scan(client, message, photo_message):
    m = await message.reply("**📷 Scanning QR Code...**")
    file_path = None
    try:
        file_path = await client.download_media(photo_message.photo.file_id)
        img = Image.open(file_path)
        decoded = decode(img)

        if decoded:
            results = "\n\n".join([f"**Result {i+1}:** `{d.data.decode('utf-8')}`" for i, d in enumerate(decoded)])
            await m.edit(f"**📷 QR Code Scanned!**\n\n{results}\n\n_Powered by @Astro_AF_bot")
        else:
            await m.edit("**❌ No QR code found in this image.**")
    except Exception as e:
        await m.edit(f"**❌ Error:** `{e}`")
        print(f"QR Scan Error: {e}")
    finally:
        import os
        if file_path and os.path.exists(file_path):
            os.remove(file_path)