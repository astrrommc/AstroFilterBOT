import os
import logging
import time
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import (
    MediaEmpty, 
    PhotoInvalidDimensions, 
    WebpageMediaEmpty,
    UserNotParticipant
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import IMDB_TEMPLATE
from utils import extract_user, get_file_id, get_poster
from datetime import datetime

logger = logging.getLogger(__name__)

# --- COMPATIBILITY LAYER ---
class Sphinx(dict):
    """Handles nested lookups like {message.from_user.mention} and prevents crashes."""
    def __getattr__(self, name):
        return self.get(name, self)
    def __getitem__(self, key):
        return super().get(key, self)
    def __str__(self):
        return "N/A"

# --- ID COMMAND ---
@Client.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        user = message.from_user
        await message.reply_text(
            f"<b>➲ Name:</b> {user.first_name}\n"
            f"<b>➲ ID:</b> <code>{user.id}</code>\n"
            f"<b>➲ DC:</b> <code>{user.dc_id or 'N/A'}</code>", 
            quote=True
        )
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        _id = f"<b>➲ Chat ID</b>: <code>{message.chat.id}</code>\n"
        u_id = message.from_user.id if message.from_user else 'Anonymous'
        _id += f"<b>➲ User ID</b>: <code>{u_id}</code>\n"
        if message.reply_to_message and message.reply_to_message.from_user:
            _id += f"<b>➲ Replied User ID</b>: <code>{message.reply_to_message.from_user.id}</code>\n"
        await message.reply_text(_id, quote=True)

# --- INFO COMMAND ---
@Client.on_message(filters.command(["info"]))
async def who_is(client, message):
    status = await message.reply_text("`Processing...`")
    try:
        user_id, _ = extract_user(message)
        user = await client.get_users(user_id)
    except Exception as e:
        return await status.edit(f"Error: {e}")

    msg = (
        f"<b>➲ Name:</b> {user.first_name} {user.last_name or ''}\n"
        f"<b>➲ ID:</b> <code>{user.id}</code>\n"
        f"<b>➲ Username:</b> @{user.username or 'None'}\n"
        f"<b>➲ DC:</b> {user.dc_id or 'N/A'}\n"
    )
    
    btn = [[InlineKeyboardButton('🔐 Close', callback_data='close_data')]]
    if user.photo:
        upic = await client.download_media(user.photo.big_file_id)
        await message.reply_photo(upic, caption=msg, reply_markup=InlineKeyboardMarkup(btn))
        os.remove(upic)
    else:
        await message.reply_text(msg, reply_markup=InlineKeyboardMarkup(btn))
    await status.delete()

# --- IMDB SEARCH (Fixes "Unknown" Buttons) ---
@Client.on_message(filters.command(["imdb", 'search']))
async def imdb_search(client, message):
    if len(message.command) < 2:
        return await message.reply('**🗂️ Movie Info Extractor**\n\n**Usage**:\n`/imdb` Movie Name')

    query = message.text.split(None, 1)[1]
    start_time = time.time()
    status = await message.reply('🔍 Searching IMDb...')
    
    try:
        movies = await get_poster(query, bulk=True)
    except Exception as e:
        return await status.edit(f"❌ Scraper Error: {e}")

    if not movies:
        return await status.edit("❌ No results found.")

    btn = []
    for movie in movies:
        m_title = "Unknown"
        m_id = None
        m_year = ""

        # Deep search logic to find the title
        if hasattr(movie, 'data') and isinstance(movie.data, dict):
            m_title = movie.data.get('title') or movie.data.get('localized title')
            m_id = getattr(movie, 'movieID', None)
            m_year = movie.data.get('year', '')
        elif isinstance(movie, dict):
            m_title = movie.get('title') or movie.get('name') or movie.get('localized_title')
            m_id = movie.get('movieID') or movie.get('imdb_id') or movie.get('id')
            m_year = movie.get('year', '')
        else:
            m_title = getattr(movie, 'title', getattr(movie, 'name', 'Unknown'))
            m_id = getattr(movie, 'movieID', getattr(movie, 'imdb_id', None))
            m_year = getattr(movie, 'year', '')

        if m_id:
            btn.append([InlineKeyboardButton(
                text=f"{m_title} ({m_year})" if m_year else str(m_title),
                callback_data=f"im#{m_id}#{start_time}"
            )])

    await status.edit('**Select a result from IMDb:**', reply_markup=InlineKeyboardMarkup(btn))

# --- IMDB CALLBACK (Fixes Crashes and Typos) ---
@Client.on_callback_query(filters.regex('^im#'))
async def imdb_callback(bot: Client, query: CallbackQuery):
    await query.answer("Fetching Movie Details...")
    
    data_parts = query.data.split('#')
    movie_id = data_parts[1]
    search_start = float(data_parts[2]) if len(data_parts) > 2 else time.time()
    
    imdb = await get_poster(query=movie_id, id=True)
    if not imdb:
        return await query.message.edit("❌ Metadata not found.")

    # Force to dictionary for Sphinx mapper
    if not isinstance(imdb, dict):
        try: imdb = dict(imdb)
        except: imdb = {}

    # Map data to satisfy Script.py template
    data = Sphinx({
        'title': imdb.get('title') or imdb.get('name', 'N/A'),
        'rating': imdb.get('rating', 'N/A'),
        'votes': imdb.get('votes', 'N/A'),
        'genres': imdb.get('genres', 'N/A'),
        'gen': imdb.get('genres', 'N/A'),
        'plot': imdb.get('plot', 'No plot available.'),
        'year': imdb.get('year', 'N/A'),
        'cast': imdb.get('cast', 'N/A'),
        'director': imdb.get('director', 'N/A'),
        'runtime': imdb.get('runtime', 'N/A'),
        'languages': imdb.get('languages', 'N/A'),
        'release_date': imdb.get('release_date', 'N/A'),
        'countries': imdb.get('countries', 'N/A'),
        'url': imdb.get('url', f"https://www.imdb.com/title/{movie_id}"),
        'poster': imdb.get('poster'),
        # Fixes typos and time tracking
        'qurey': imdb.get('title', 'N/A'),
        'remaining_seconds': round(time.time() - search_start, 1),
        # Fixes the {message.from_user.mention} crash
        'message': Sphinx({
            'from_user': Sphinx({
                'mention': query.from_user.mention,
                'first_name': query.from_user.first_name,
                'id': query.from_user.id
            })
        })
    })

    try:
        caption = IMDB_TEMPLATE.format_map(data)
    except Exception as e:
        logger.error(f"Formatting failed: {e}")
        caption = f"<b>{data['title']}</b>\n\n(Formatting Error: {e})"

    btn = [[InlineKeyboardButton("🔗 View on IMDb", url=data['url'])]]

    if data['poster']:
        try:
            await query.message.reply_photo(photo=data['poster'], caption=caption, reply_markup=InlineKeyboardMarkup(btn))
            await query.message.delete()
        except Exception:
            await query.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn))
    else:
        await query.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn))