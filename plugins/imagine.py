import aiohttp
import asyncio
import random
import urllib.parse
import hashlib
from io import BytesIO
from collections import OrderedDict
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- Config ---
MODELS = ["flux", "turbo", "gptimage", "kontext", "nanobanana"]
MAX_PROMPT_CACHE = 1024  # keep a bounded in-memory cache for callback prompts
PROMPT_CACHE = OrderedDict()  # short_id -> prompt (insertion-ordered)

# --- Helpers ---
def _make_short_id(prompt: str) -> str:
    # stable, short id from prompt (sha1 hex prefix)
    return hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:12]

def cache_prompt(prompt: str) -> str:
    sid = _make_short_id(prompt)
    # ensure unique key in case different prompts collide (very unlikely)
    if sid in PROMPT_CACHE and PROMPT_CACHE[sid] != prompt:
        # append random suffix if collision (extremely unlikely)
        sid = sid + "-" + hashlib.sha1((prompt + str(random.random())).encode()).hexdigest()[:4]
    PROMPT_CACHE[sid] = prompt
    PROMPT_CACHE.move_to_end(sid)
    # prune oldest
    if len(PROMPT_CACHE) > MAX_PROMPT_CACHE:
        PROMPT_CACHE.popitem(last=False)
    return sid

def get_model_buttons(short_id: str) -> InlineKeyboardMarkup:
    # callback_data format: "img:{model}:{short_id}" -> small & safe < 64 bytes
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎨 Flux", callback_data=f"img:flux:{short_id}"),
            InlineKeyboardButton("📸 Realism", callback_data=f"img:flux-realism:{short_id}"),
            InlineKeyboardButton("🎌 Anime", callback_data=f"img:flux-anime:{short_id}"),
        ],
        [
            InlineKeyboardButton("🧊 3D", callback_data=f"img:flux-3d:{short_id}"),
            InlineKeyboardButton("⚡ Turbo", callback_data=f"img:turbo:{short_id}"),
            InlineKeyboardButton("🎲 Random", callback_data=f"img:random:{short_id}"),
        ]
    ])

async def generate_image(prompt: str, model: str = "flux") -> bytes:
    # Encode prompt for URL path
    encoded = urllib.parse.quote(prompt, safe='')
    # seeds & sizes to try (best -> fallback)
    attempts = [
        (random.randint(1, 9999999), 1024, 1024),
        (random.randint(1, 9999999), 768, 768),
        (random.randint(1, 9999999), 512, 512),
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AstroFilterBOT/1.0)",
        "Accept": "image/*,*/*;q=0.8",
    }

    last_error = None
    timeout = aiohttp.ClientTimeout(total=90)
    async with aiohttp.ClientSession() as session:
        for seed, width, height in attempts:
            try:
                url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model={model}"
                async with session.get(url, headers=headers, timeout=timeout) as resp:
                    if resp.status == 200:
                        content_type = resp.headers.get("Content-Type", "")
                        # ensure we actually received an image
                        if content_type and "image" in content_type.lower():
                            data = await resp.read()
                            if data and len(data) > 1000:  # sanity check size
                                return data
                            else:
                                last_error = "Image too small or empty"
                        else:
                            # sometimes pollinations returns HTML or JSON if busy
                            text = await resp.text()
                            last_error = f"Unexpected content-type: {content_type} / body-start: {text[:200]!r}"
                    else:
                        last_error = f"HTTP {resp.status}"
            except asyncio.TimeoutError:
                last_error = "Timeout"
            except Exception as e:
                last_error = str(e)
            # small delay before next attempt
            await asyncio.sleep(1.5)

    raise Exception(f"All attempts failed: {last_error}")

# --- Command handler ---
@Client.on_message(filters.command(["imagine", "img", "gen"]))
async def imagine(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "**🎨 AI Image Generator**\n\n"
            "**Usage:** `/imagine a dragon flying over a city`\n\n"
            "**Aliases:** `/img`, `/gen`\n\n"
            "**Models:** Flux, Realism, Anime, 3D, Turbo"
        )

    # full prompt
    prompt = message.text.split(None, 1)[1].strip()
    if not prompt:
        return await message.reply("Please provide a prompt. Example: `/imagine a red fox wearing sunglasses`")

    m = await message.reply(f"**🎨 Generating image...**\n⏳ Please wait up to 90 seconds...\n\n**Prompt:** `{prompt}`")
    short_id = cache_prompt(prompt)

    try:
        # attempt with default model "flux"
        image_data = await generate_image(prompt, "turbo")
        # prepare BytesIO for Telegram
        bio = BytesIO(image_data)
        bio.name = "image.png"
        bio.seek(0)

        # reply and provide model buttons (buttons use short_id only)
        await client.send_chat_action(message.chat.id, "upload_photo")
        await message.reply_photo(
            photo=bio,
            caption=f"**🎨 Generated Image**\n\n**Prompt:** {prompt}\n**Model:** flux\n\n_Powered by @Astro_AF_bot_",
            reply_markup=get_model_buttons(short_id)
        )
        await m.delete()
    except Exception as e:
        try:
            await m.edit(f"**❌ Failed:** `{e}`\n\nPollinations may be busy or returned unexpected data. Try again in a moment.")
        except:
            pass
        print(f"Imagine Error: {e}")

# --- Callback handler for model buttons ---
@Client.on_callback_query(filters.regex(r"^img:"))
async def imagine_model_callback(client: Client, query: CallbackQuery):
    # data format: "img:{model}:{short_id}"
    parts = query.data.split(":", 2)
    if len(parts) != 3:
        return await query.answer("Invalid callback data", show_alert=True)

    _, model, short_id = parts
    prompt = PROMPT_CACHE.get(short_id)
    if not prompt:
        # expired or missing prompt
        return await query.answer("Prompt expired or not found. Please run /imagine again.", show_alert=True)

    if model == "random":
        model = random.choice(MODELS)
    # fallback to a known model if something weird arrives
    if model not in MODELS:
        model = "flux"

    await query.answer(f"Generating with {model}...")

    # try to update caption to show progress
    try:
        await query.message.edit_caption(f"**🎨 Generating...**\n⏳ Please wait...\n**Model:** {model}")
    except:
        # some messages can't be edited (e.g., old messages), ignore
        pass

    try:
        image_data = await generate_image(prompt, model)
        bio = BytesIO(image_data)
        bio.name = "image.png"
        bio.seek(0)

        await client.send_chat_action(query.message.chat.id, "upload_photo")
        await query.message.reply_photo(
            photo=bio,
            caption=f"**🎨 Generated Image**\n\n**Prompt:** {prompt}\n**Model:** {model}\n\n_Powered by @Astro_AF_bot_",
            reply_markup=get_model_buttons(short_id)
        )
        # remove the "generating" message
        try:
            await query.message.delete()
        except:
            pass
    except Exception as e:
        try:
            await query.message.edit_caption(f"**❌ Failed:** `{e}`\n\nTry again.")
        except:
            pass
        print(f"Imagine callback error: {e}")