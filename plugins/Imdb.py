from pyrogram import Client, filters
from imdb import Cinemagoer  # Updated library
from Script import script
import time


ia = Cinemagoer()

@Client.on_message(filters.command("imdb"))
async def imdb_search(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/imdb [movie_name]</code>")

    start_time = time.time()
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("<i>🔍 Fetching details from IMDb...</i>")

    try:
        
        search_results = ia.search_movie(query)
        
        
        if not search_results:
            search_results = ia.search_movie(query.split()[0])

        if not search_results:
            return await m.edit(f"<b>❌ No results found for:</b> <code>{query}</code>")

        
        movie = ia.get_movie(search_results[0].movieID)

        
        cap = script.IMDB_TEMPLATE_TXT.format(
            qurey=query,
            title=movie.get('title', 'N/A'),
            genres=", ".join(movie.get('genres', [])) or 'N/A',
            year=movie.get('year', 'N/A'),
            rating=movie.get('rating', 'N/A'),
            votes=movie.get('votes', 'N/A'),
            languages=", ".join(movie.get('languages', [])) or 'N/A',
            runtime=movie.get('runtimes', ['N/A'])[0],
            release_date=movie.get('original air date', 'N/A'),
            countries=", ".join(movie.get('countries', [])) or 'N/A',
            url=f"https://www.imdb.com/title/tt{movie.movieID}",
            remaining_seconds="{:.2f}".format(time.time() - start_time),
            message=message
        )

        poster = movie.get('full-size cover url')
        if poster:
            await message.reply_photo(photo=poster, caption=cap)
            await m.delete()
        else:
            await m.edit(cap)

    except Exception as e:
        await m.edit(f"<b>❌ IMDb Link Error:</b> <code>{str(e)}</code>")
        
