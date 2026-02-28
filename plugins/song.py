import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command(["song"]))
async def download_song(client, message):
    # Check if a song name was provided
    if len(message.command) < 2:
        return await message.reply_text("<b>Please give me a song name! 🎶</b>\n\nExample: <code>/song Blinding Lights</code>")
    
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>Searching your song... 🔎</b>")
    
    # Configuration for yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search and download the first result
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"
            
        await m.edit("<b>Uploading song... 📤</b>")
        
        # Send the file to the user
        await message.reply_audio(
            audio=file_path,
            caption=f"<b>Song:</b> <code>{info['title']}</code>\n<b>Requested by:</b> {message.from_user.mention}",
            title=info['title'],
            performer="YouTube Search"
        )
        
        await m.delete()
        os.remove(file_path) # Clean up the server storage
        
    except Exception as e:
        await m.edit(f"<b>❌ Error:</b> <code>{str(e)}</code>")
