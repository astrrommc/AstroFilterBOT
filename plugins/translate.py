from pyrogram import Client, filters
import aiohttp

@Client.on_message(filters.command(["tr", "translate"]))
async def translate_text(bot, message):
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        text_to_translate = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text_to_translate = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("<b>Usage:</b> <code>/tr [lang_code]</code> (as a reply) or <code>/tr [lang_code] [text]</code>")

    args = message.text.split()
    target_lang = "en"
    if len(args) > 1 and len(args[1]) == 2 and args[1].isalpha():
        target_lang = args[1]
        if len(args) > 2 and not message.reply_to_message:
            text_to_translate = message.text.split(None, 2)[2]

    m = await message.reply_text("<i>Translating... Please wait.</i>")

    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text_to_translate
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                result = await resp.json()
                translated = "".join([item[0] for item in result[0] if item[0]])

        reply_text = f"<b>Translated to {target_lang.upper()}:</b>\n\n<code>{translated}</code>"
        await m.edit(reply_text)
    except Exception as e:
        await m.edit(f"<b>❌ Error:</b> <code>{str(e)}</code>")