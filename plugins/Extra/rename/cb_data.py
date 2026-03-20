from plugins.Extra.utils import progress_for_pyrogram, convert, humanbytes
from pyrogram import Client, filters
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ForceReply)
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from database.users_chats_db import db
from TechVJ.bot import multi_clients, work_loads
import os 
import humanize
from PIL import Image
import time
import logging

logger = logging.getLogger(__name__)

def get_fast_client(bot):
    if not multi_clients or len(multi_clients) <= 1:
        return bot
    client_id = min(work_loads, key=work_loads.get)
    work_loads[client_id] += 1
    return multi_clients[client_id]

def release_client(client):
    for client_id, c in multi_clients.items():
        if c == client and work_loads.get(client_id, 0) > 0:
            work_loads[client_id] -= 1
            break

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.edit("✖️ **Cᴀɴᴄᴇʟʟɪɴɢ ᴘʀᴏᴄᴇss...**")
        await update.message.delete()
    except Exception as e:
        logger.error(f"Cancel Error: {e}")

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    try:
        type = update.data.split("_")[1]
        new_name = update.message.text
        new_filename = new_name.split(":-")[1].strip() 
        file = update.message.reply_to_message
        
        if not os.path.isdir("downloads"):
            os.makedirs("downloads")

        ms = await update.message.edit("🗃️__**Pʟᴇᴀsᴇ ᴡᴀɪᴛ...**__\n\n__Dᴏᴡɴʟᴏᴀᴅɪɴɢ Fɪʟᴇ TO Oᴜʀ Sᴇʀᴠᴇʀ...__")
        c_time = time.time()

        try:
            path = await bot.download_media(
                message=file,
                progress=progress_for_pyrogram,
                progress_args=("**📥 Dᴏᴡɴʟᴏᴀᴅɪɴɢ Tᴏ Mʏ Sᴇʀᴠᴇʀ**", ms, c_time))
        except Exception as e:
            return await ms.edit(f"Download Error: {e}")

        file_path = os.path.join("downloads", new_filename)
        os.rename(path, file_path)
        
        duration = 0
        try:
            parser = createParser(file_path)
            if parser:
                with parser:
                    metadata = extractMetadata(parser)
                    if metadata and metadata.has("duration"):
                        duration = metadata.get('duration').seconds
        except Exception as e:
            logger.warning(f"Metadata extraction skipped: {e}")
            
        ph_path = None 
        media = getattr(file, file.media.value)
        c_caption = await db.get_caption(update.message.chat.id)
        c_thumb = await db.get_thumbnail(update.message.chat.id)
        
        if c_caption:
            caption = c_caption.format(filename=new_filename, filesize=humanize.naturalsize(media.file_size), duration=convert(duration))
        else:
            caption = f"**{new_filename}**"
            
        if (media.thumbs or c_thumb):
            ph_path = await bot.download_media(c_thumb) if c_thumb else await bot.download_media(media.thumbs[0].file_id)
            if ph_path:
                Image.open(ph_path).convert("RGB").save(ph_path)
                img = Image.open(ph_path)
                img.resize((320, 320)).save(ph_path, "JPEG")

        await ms.edit("✅ **Renaming Complete!**\n🚀 **Sending File to Telegram...**")
        c_time = time.time()

        ul_client = get_fast_client(bot)
        try:
            if type == "document":
                await ul_client.send_document(
                    update.message.chat.id,
                    document=file_path,
                    thumb=ph_path,
                    caption=caption,
                    reply_markup=None,
                    progress=progress_for_pyrogram,
                    progress_args=("**📤 Uᴘʟᴏᴀᴅɪɴɢ Fɪʟᴇ Tᴏ Tᴇʟᴇɢʀᴀᴍ...**", ms, c_time))
            elif type == "video":
                await ul_client.send_video(
                    update.message.chat.id,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    reply_markup=None,
                    progress=progress_for_pyrogram,
                    progress_args=("**📤 Uᴘʟᴏᴀᴅɪɴɢ Fɪʟᴇ Tᴏ Tᴇʟᴇɢʀᴀᴍ...**", ms, c_time))
            elif type == "audio":
                await ul_client.send_audio(
                    update.message.chat.id,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    reply_markup=None,
                    progress=progress_for_pyrogram,
                    progress_args=("**📤 Uᴘʟᴏᴀᴅɪɴɢ Fɪʟᴇ Tᴏ Tᴇʟᴇɢʀᴀᴍ...**", ms, c_time))
        except Exception as e:
            release_client(ul_client)
            if os.path.exists(file_path): os.remove(file_path)
            if ph_path and os.path.exists(ph_path): os.remove(ph_path)
            return await ms.edit(f"Upload Error: {e}")
        release_client(ul_client)

        await ms.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleanup: Deleted {new_filename}")
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)
           
    except Exception as e:
        logger.error(f"Global Error: {e}")