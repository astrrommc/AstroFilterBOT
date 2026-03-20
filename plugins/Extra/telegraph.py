import os
import aiohttp
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

async def upload_to_catbox_pc(file_path):
    """Reliable upload for BSNL/Local Host users via Catbox"""
    url = "https://catbox.moe/user/api.php"
    
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                # reqtype 'fileupload' is mandatory for Catbox
                data = aiohttp.FormData()
                data.add_field('reqtype', 'fileupload')
                data.add_field('fileToUpload', f, filename=os.path.basename(file_path))
                
                async with session.post(url, data=data, timeout=60) as response:
                    if response.status == 200:
                        return (await response.text()).strip()
                    
                    err = await response.text()
                    logger.error(f"Network Error: {response.status} | {err}")
                    return None
    except Exception as e:
        logger.exception(f"Connection Failed: {e}")
        return None

@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_bsnl(bot, update):
    try:
        t_msg = await bot.ask(update.from_user.id, "<b>Send Photo/Video (Under 5MB).</b>")
    except: return

    status = await update.reply_text("<code>📥 Uᴘʟᴏᴀᴅɪɴɢ to Sᴇʀᴠᴇʀ...</code>")
    path = await t_msg.download()
    
    await status.edit_text("<code>📤 Pʀᴏᴄᴇssɪɴɢ...</code>")
    image_url = await upload_to_catbox_pc(path)

    if os.path.exists(path):
        os.remove(path) 

    if not image_url:
        return await status.edit_text("<b>⚠️ Sᴏᴍᴇᴛʜɪɴɢ Wᴇɴᴛ Wʀᴏɴɢ\nCᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ:@DevAstrro")

    await status.edit_text(
        text=f"<b>✅ Link Created (Catbox):</b>\n<code>{image_url}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Open Link", url=image_url)]])
    )