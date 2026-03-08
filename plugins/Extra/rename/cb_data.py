# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from plugins.Extra.utils import progress_for_pyrogram, convert, humanbytes
from pyrogram import Client, filters
from plugins.Extra.rename.filedetect import refunc
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ForceReply)
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from database.users_chats_db import db
import os 
import humanize
from PIL import Image
import time
import logging

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    try:
        type = update.data.split("_")[1]
        new_name = update.message.text
        new_filename = new_name.split(":-")[1].strip() # Cleaned filename
        file = update.message.reply_to_message
        
        # FIXED: Ensure download directory exists on your SSD
        if not os.path.isdir("downloads"):
            os.makedirs("downloads")
            
        ms = await update.message.edit("⚠️__**Please wait...**__\n\n__Downloading file to my server...__")
        c_time = time.time()
        
        try:
            # Phase 1: Download
            path = await bot.download_media(
                    message=file,
                    progress=progress_for_pyrogram,
                    progress_args=("**📥 Downloading**", ms, c_time))
        except Exception as e:
            return await ms.edit(f"Download Error: {e}")

        # FIXED: Improved file path logic to prevent "File Not Found" errors
        file_path = os.path.join("downloads", new_filename)
        os.rename(path, file_path)
        
        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
               duration = metadata.get('duration').seconds
        except:
            pass
            
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
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320)).save(ph_path, "JPEG")

        # Visual Handover Alert
        await ms.edit("✅ **Download Complete!**\n🚀 **Sending File to Telegram...**")
        
        c_time = time.time() 
        try:
           # Phase 2: Upload using 300 Workers
           if type == "document":
              await bot.send_document(
                    update.message.chat.id,
                    document=file_path,
                    thumb=ph_path, 
                    caption=caption, 
                    progress=progress_for_pyrogram,
                    progress_args=("**📤 Uploading**", ms, c_time)) 
           elif type == "video": 
               await bot.send_video(
                    update.message.chat.id,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**📤 Uploading**", ms, c_time)) 
           elif type == "audio": 
               await bot.send_audio(
                    update.message.chat.id,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**📤 Uploading**", ms, c_time)) 
        except Exception as e: 
            return await ms.edit(f"Upload Error: {e}") 
            
        await ms.delete() 
        if os.path.exists(file_path): os.remove(file_path)
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)
           
    except Exception as e:
        logger.error(f"Global Error: {e}")
