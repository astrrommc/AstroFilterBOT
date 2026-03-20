from __future__ import unicode_literals

import os, requests, asyncio, wget
from pyrogram import filters, Client
from pyrogram.types import Message
from info import CHNL_LNK
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL


def clean_yt_url(url):
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


@Client.on_message(filters.command(['song', 'mp3']))
async def song(client, message):
    if len(message.command) < 2:
        return await message.reply_text("**📥Song Downloader**\n\n**Usage:**\n`/song` Your Song Name or URL")

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    query = " ".join(message.command[1:])

    m = await message.reply(f"**Sᴇᴀʀᴄʜɪɴɢ Yᴏᴜʀ Sᴏɴɢ: {query}**")

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
    }

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        raw_link = f"https://youtube.com{results[0]['url_suffix']}"
        link = clean_yt_url(raw_link)
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        performer = "@Astro_AF_bot"
        duration = results[0]["duration"]
    except Exception as e:
        print(str(e))
        return await m.edit("**📥Song Downloader**\n\n**Usage:**\n`/song` Your Song Name or URL")

    await m.edit("**Dᴏᴡɴʟᴏᴀᴅɪɴɢ Yᴏᴜʀ Sᴏɴɢ...**")
    audio_file = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            # After FFmpeg conversion, file will be .mp3
            base_name = ydl.prepare_filename(info_dict)
            audio_file = os.path.splitext(base_name)[0] + ".mp3"

        cap = f"🎵 **{title}**\n\nRequested by: {rpk}"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60

        await message.reply_audio(
            audio_file,
            caption=cap,
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"**🚫 Error:** `{e}`")
        print(e)
    try:
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
        if os.path.exists(thumb_name):
            os.remove(thumb_name)
    except Exception as e:
        print(e)


def get_text(message: Message):
    if not message.text or " " not in message.text:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None


@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = get_text(message)
    pablo = await message.reply(f"Fɪɴᴅɪɴɢ Aɴᴅ Dᴏᴡɴʟᴏᴀᴅɪɴɢ Yᴏᴜʀ Vɪᴅᴇᴏ: `{urlissed}`")
    if not urlissed:
        return await pablo.edit("**📥Video Downloader**\n\n**Usage:**\n`/video` Your Video Name or URL")

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    sedlyf = wget.download(kekme)

    opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "merge_output_format": "mp4",
        "outtmpl": "%(id)s.mp4",
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(mo, download=True)
    except Exception as e:
        return await pablo.edit(f"**❌ Download Failed:** `{e}`")

    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"**Tɪᴛʟᴇ:** [{thum}]({mo})\nRᴇǫᴜᴇsᴛᴇᴅ Bʏ: {message.from_user.mention}"

    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        reply_to_message_id=message.id
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)