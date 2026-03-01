from pyrogram import Client, filters
from imdb import IMDb
from Script import script

# Initialize IMDb instance
ia = IMDb()

@Client.on_message(filters.command("imdb"))
async def imdb_search(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/imdb [movie_name]</code>")

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("<i>Searching IMDb... Please wait.</i>")

    try:
        # Search for the movie
        search = ia.search_movie(query)
        if not search:
            return await m.edit("<b>❌ No results found on IMDb!</b>")

        # Get detailed information for the first result
        movie_id = search[0].movieID
        movie = ia.get_movie(movie_id)

        # Extract details for the template in Script.py
        title = movie.get('title', 'N/A')
        year = movie.get('year', 'N/A')
        rating = movie.get('rating', 'N/A')
        votes = movie.get('votes', 'N/A')
        genres = ", ".join(movie.get('genres', []))
        runtime = movie.get('runtimes', ['N/A'])[0]
        languages = ", ".join(movie.get('languages', []))
        countries = ", ".join(movie.get('countries', []))
        release_date = movie.get('original air date', 'N/A')
        url = f"https://www.imdb.com/title/tt{movie_id}"

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
            remaining_seconds="0.00", # Placeholder as calculations happen locally
            message=message
        )

        # Check for poster image
        if movie.get('full-size cover url'):
            await message.reply_photo(photo=movie.get('full-size cover url'), caption=cap)
            await m.delete()
        else:
            await m.edit(cap)

    except Exception as e:
        await m.edit(f"<b>❌ Error:</b> <code>{str(e)}</code>")
