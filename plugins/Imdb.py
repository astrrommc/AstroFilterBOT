from pyrogram import Client, filters
from imdb import IMDb
from Script import script
import time

# Initialize IMDb instance
ia = IMDb()

@Client.on_message(filters.command("imdb"))
async def imdb_search(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/imdb [movie_name]</code>")

    # Start timing for the 'remaining_seconds' variable
    start_time = time.time()
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("<i>🔍 Searching IMDb... Please wait.</i>")

    try:
        # Search for the movie
        search_results = ia.search_movie(query)
        if not search_results:
            return await m.edit(f"<b>❌ No IMDb results found for:</b> <code>{query}</code>")

        # Get detailed information for the first result
        movie_id = search_results[0].movieID
        movie = ia.get_movie(movie_id)

        # Extract details for the template in Script.py
        title = movie.get('title', 'N/A')
        year = movie.get('year', 'N/A')
        rating = movie.get('rating', 'N/A')
        votes = movie.get('votes', 'N/A')
        genres = ", ".join(movie.get('genres', [])) or 'N/A'
        runtime = movie.get('runtimes', ['N/A'])[0]
        languages = ", ".join(movie.get('languages', [])) or 'N/A'
        countries = ", ".join(movie.get('countries', [])) or 'N/A'
        release_date = movie.get('original air date', 'N/A')
        url = f"https://www.imdb.com/title/tt{movie_id}"
        
        # Calculate time taken for search
        end_time = time.time()
        remaining_seconds = "{:.2f}".format(end_time - start_time)

        # Format and send the response using your existing template
        cap = script.IMDB_TEMPLATE_TXT.format(
            qurey=query,
            title=title,
            genres=genres,
            year=year,
            rating=rating,
            votes=votes,
            languages=languages,
            runtime=runtime,
            release_date=release_date,
            countries=countries,
            url=url,
            remaining_seconds=remaining_seconds,
            message=message
        )

        # Check for poster image and reply
        poster_url = movie.get('full-size cover url')
        if poster_url:
            await message.reply_photo(photo=poster_url, caption=cap)
            await m.delete()
        else:
            await m.edit(cap, disable_web_page_preview=False)

    except Exception as e:
        await m.edit(f"<b>❌ IMDb Error:</b> <code>{str(e)}</code>")
