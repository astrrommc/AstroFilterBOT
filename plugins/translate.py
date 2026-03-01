from pyrogram import Client, filters
from googletrans import Translator
from Script import script

@Client.on_message(filters.command(["tr", "translate"]))
async def translate_text(bot, message):
    # Check if the user replied to a message or provided text
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        text_to_translate = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text_to_translate = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("<b>Usage:</b> <code>/tr [lang_code]</code> (as a reply) or <code>/tr [lang_code] [text]</code>")

    # Determine target language (default is English 'en')
    # If the first word after /tr is a 2-letter code, use it
    args = message.text.split()
    target_lang = "en"
    if len(args) > 1 and len(args[1]) == 2:
        target_lang = args[1]
        # If they provided text after the code, re-extract it
        if len(args) > 2 and not message.reply_to_message:
            text_to_translate = message.text.split(None, 2)[2]

    m = await message.reply_text("<i>Translating... Please wait.</i>")
    
    try:
        translator = Translator()
        translation = translator.translate(text_to_translate, dest=target_lang)
        
        reply_text = f"<b>Translated to {target_lang.upper()}:</b>\n\n<code>{translation.text}</code>"
        await m.edit(reply_text)
    except Exception as e:
        await m.edit(f"<b>❌ Error:</b> <code>{str(e)}</code>\n\n<i>Note: If this persists, the Google API may be temporarily blocking requests.</i>")
