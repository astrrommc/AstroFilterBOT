import logging
import requests
import asyncio
from info import CHNL_LNK
from pyrogram import Client, filters, enums

# Setting up basic logging
logger = logging.getLogger(__name__)

@Client.on_message(filters.command('repo') & filters.incoming)
async def git(bot, message):
    # Fix: Check for arguments before trying to split message.text to avoid IndexError
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Usage:</b> <code>/repo [search_query]</code>\n\n"
            "<i>Please provide a repository name to search.</i>"
        )

    pablo = await message.reply_text("<code>Searching GitHub... 🔍</code>")
    
    # Safely extract the search query
    query = message.text.split(None, 1)[1]

    try:
        # Fetching data from GitHub API
        r = requests.get("https://api.github.com/search/repositories", params={"q": query}, timeout=10)
        
        # Ensure the request was successful
        if r.status_code != 200:
            return await pablo.edit(f"<b>GitHub API Error:</b> <code>{r.status_code}</code>")
            
        lool = r.json()

        # Check if any items were found
        if not lool.get("items") or lool.get("total_count") == 0:
            await pablo.edit("<b>❌ No repository found for your query.</b>")
            return

        # Get the first matching item
        qw = lool.get("items")[0]
        
        # Formatting the response text
        txt = f"<b>🏷 Name:</b> <i>{qw.get('name')}</i>\n"
        txt += f"<b>📛 Full Name:</b> <i>{qw.get('full_name')}</i>\n"
        txt += f"<b>🔗 Link:</b> <a href='{qw.get('html_url')}'>Click Here</a>\n"
        txt += f"<b>🍴 Forks:</b> <i>{qw.get('forks_count', 0)}</i>\n"
        txt += f"<b>❗ Open Issues:</b> <i>{qw.get('open_issues', 0)}</i>\n"

        if qw.get("description"):
            txt += f"<b>📝 Description:</b> <code>{qw.get('description')}</code>\n"

        if qw.get("language"):
            txt += f"<b>💻 Language:</b> <code>{qw.get('language')}</code>\n"

        if qw.get("size"):
            txt += f"<b>📦 Size:</b> <code>{qw.get('size')} KB</code>\n"

        if qw.get("created_at"):
            # Formatting timestamp slightly for readability
            created = qw.get("created_at").replace("T", " ").replace("Z", "")
            txt += f"<b>📅 Created At:</b> <code>{created}</code>\n"

        txt += f"\n<b>📡 Powered by: {CHNL_LNK}</b>"

        if qw.get("archived"):
            txt += "\n\n⚠️ <b>Note:</b> <i>This project is archived by the owner.</i>"

        # Edit the processing message with final results
        await pablo.edit(txt, disable_web_page_preview=False, parse_mode=enums.ParseMode.HTML)

    except requests.exceptions.Timeout:
        await pablo.edit("<b>⌛ Request Timed Out!</b> Please try again later.")
    except Exception as e:
        logger.exception(e)
        await pablo.edit(f"<b>Something went wrong!</b>\n<code>{str(e)}</code>")