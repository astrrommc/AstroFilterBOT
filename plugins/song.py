from __future__ import unicode_literals
import os, requests
from pyrogram import filters, Client
from yt_dlp import YoutubeDL


@Client.on_message(filters.command(['song', 'mp3']))
async def song(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Please give me a song name! 🎶**\n\nExample: `/song Blinding Lights`"
        )

    query = " ".join(message.command[1:])
    m = await message.reply(f"**ѕєαrchíng чσur ѕσng...!\n{query}**")

    audio_file = None
    thumb_name = None

    try:
        # Step 1: Search only, get video ID
        search_opts = {
            'quiet': True,
            'noplaylist': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        with YoutubeDL(search_opts) as ydl:
            r = ydl.extract_info(f"ytsearch1:{query}", download=False)
            video = r['entries'][0]
            video_id = video['id']
            title = video.get('title', query)[:40]
            duration = int(video.get('duration') or 0)
            thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        # Clean direct URL - NO playlist params
        clean_url = f"https://www.youtube.com/watch?v={video_id}"

        # Download thumbnail
        thumb_name = f"{video_id}.jpg"
        thumb_data = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb_data.content)

        await m.edit("**dσwnlσαdíng чσur ѕσng...!**")

        # Step 2: Download audio from clean URL only
        download_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': f'{video_id}.%(ext)s',
            'quiet': True,
            'noplaylist': True,
        }
        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            audio_file = ydl.prepare_filename(info)

        cap = f"🎵 **{title}**\n\nRequested by: {message.from_user.mention}\n\n@Astro_AF_bot"
        await message.reply_audio(
            audio_file,
            caption=cap,
            quote=False,
            title=title,
            duration=duration,
            performer="@Astro_AF_bot",
            thumb=thumb_name
        )
        await m.delete()

    except Exception as e:
        await m.edit(f"**🚫 Error:** `{e}`")
        print(e)
    finally:
        for f in [audio_file, thumb_name]:
            if f and os.path.exists(f):
                os.remove(f)