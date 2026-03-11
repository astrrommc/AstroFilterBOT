# Photo Editor Plugin for AstroFilterBOT
import os, io, aiohttp
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

REMOVE_BG_API = "Qextfp8qdDKoqH2bTdRsPCZ1"

def get_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝖡𝗋𝗂𝗀𝗁𝗍", callback_data="bright"),
            InlineKeyboardButton("𝖬𝗂𝗑𝖾𝖽", callback_data="mix"),
            InlineKeyboardButton("𝖡 & 𝖶", callback_data="b|w"),
        ],[
            InlineKeyboardButton("𝖢𝗂𝗋𝖼𝗅𝖾", callback_data="circle"),
            InlineKeyboardButton("𝖡𝗅𝗎𝗋", callback_data="blur"),
            InlineKeyboardButton("𝖡𝗈𝗋𝖽𝖾𝗋", callback_data="border"),
        ],[
            InlineKeyboardButton("𝖲𝗍𝗂𝖼𝗄𝖾𝗋", callback_data="stick"),
            InlineKeyboardButton("𝖱𝗈𝗍𝖺𝗍𝖾", callback_data="rotate"),
            InlineKeyboardButton("𝖢𝗈𝗇𝗍𝗋𝖺𝗌𝗍", callback_data="contrast"),
        ],[
            InlineKeyboardButton("𝖲𝖾𝗉𝗂𝖺", callback_data="sepia"),
            InlineKeyboardButton("𝖯𝖾𝗇𝖼𝗂𝗅", callback_data="pencil"),
            InlineKeyboardButton("𝖢𝖺𝗋𝗍𝗈𝗈𝗇", callback_data="cartoon"),
        ],[
            InlineKeyboardButton("𝖨𝗇𝗏𝖾𝗋𝗍", callback_data="inverted"),
            InlineKeyboardButton("𝖦𝗅𝗂𝗍𝖼𝗁", callback_data="glitch"),
            InlineKeyboardButton("𝖱𝖾𝗆𝗈𝗏𝖾 𝖡𝖦", callback_data="removebg"),
        ],[
            InlineKeyboardButton("𝖢𝗅𝗈𝗌𝖾", callback_data="close_data"),
        ]
    ])

@Client.on_message(filters.photo & filters.private)
async def photo_handler(client, message):
    try:
        await message.reply(
            text="**🖼 Photo Editor**\n\nSelect an effect to apply:",
            quote=True,
            reply_markup=get_buttons()
        )
    except Exception as e:
        print(e)

def apply_bright(img):
    return ImageEnhance.Brightness(img).enhance(1.5)

def apply_mix(img):
    r, g, b = img.split() if img.mode == 'RGB' else img.convert('RGB').split()
    return Image.merge('RGB', (b, r, g))

def apply_bw(img):
    return img.convert('L').convert('RGB')

def apply_circle(img):
    img = img.convert('RGBA')
    size = min(img.size)
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    x0 = (img.width - size) // 2
    y0 = (img.height - size) // 2
    draw.ellipse([x0, y0, x0 + size, y0 + size], fill=255)
    img.putalpha(mask)
    result = Image.new('RGBA', img.size, (255, 255, 255, 255))
    result.paste(img, mask=img.split()[3])
    return result.convert('RGB')

def apply_blur(img):
    return img.filter(ImageFilter.GaussianBlur(radius=3))

def apply_border(img):
    bordered = ImageOps.expand(img.convert('RGB'), border=20, fill=(255, 255, 255))
    return ImageOps.expand(bordered, border=5, fill=(0, 0, 0))

def apply_rotate(img):
    return img.rotate(90, expand=True)

def apply_contrast(img):
    return ImageEnhance.Contrast(img).enhance(2.0)

def apply_sepia(img):
    img = img.convert('RGB')
    w, h = img.size
    pixels = img.load()
    for i in range(w):
        for j in range(h):
            r, g, b = pixels[i, j]
            tr = int(0.393*r + 0.769*g + 0.189*b)
            tg = int(0.349*r + 0.686*g + 0.168*b)
            tb = int(0.272*r + 0.534*g + 0.131*b)
            pixels[i, j] = (min(tr,255), min(tg,255), min(tb,255))
    return img

def apply_pencil(img):
    img = img.convert('L')
    inv = ImageOps.invert(img)
    blur = inv.filter(ImageFilter.GaussianBlur(radius=10))
    result = Image.fromarray(
        __import__('numpy').divide(img, 255 - __import__('numpy').array(blur) + 1, dtype='float') * 255
    ).convert('L')
    return result.convert('RGB')

def apply_cartoon(img):
    img = img.convert('RGB')
    edges = img.filter(ImageFilter.FIND_EDGES).convert('L')
    smooth = img.filter(ImageFilter.SMOOTH_MORE)
    edges_rgb = edges.convert('RGB')
    return Image.blend(smooth, edges_rgb, alpha=0.3)

def apply_inverted(img):
    return ImageOps.invert(img.convert('RGB'))

def apply_glitch(img):
    import random
    img = img.convert('RGB')
    arr = __import__('numpy').array(img)
    for _ in range(10):
        y = random.randint(0, arr.shape[0] - 1)
        shift = random.randint(-20, 20)
        arr[y] = __import__('numpy').roll(arr[y], shift, axis=0)
    return Image.fromarray(arr)

async def apply_removebg(img, file_path):
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('image_file', f, filename='image.jpg', content_type='image/jpeg')
            data.add_field('size', 'auto')
            async with session.post(
                'https://api.remove.bg/v1.0/removebg',
                data=data,
                headers={'X-Api-Key': REMOVE_BG_API},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    return await resp.read()
                else:
                    err = await resp.text()
                    raise Exception(f"Remove.bg error: {err}")

EFFECTS = {
    'bright': apply_bright,
    'mix': apply_mix,
    'b|w': apply_bw,
    'circle': apply_circle,
    'blur': apply_blur,
    'border': apply_border,
    'rotate': apply_rotate,
    'contrast': apply_contrast,
    'sepia': apply_sepia,
    'pencil': apply_pencil,
    'cartoon': apply_cartoon,
    'inverted': apply_inverted,
    'glitch': apply_glitch,
}

@Client.on_callback_query(filters.regex('^(bright|mix|b\|w|circle|blur|border|stick|rotate|contrast|sepia|pencil|cartoon|inverted|glitch|removebg)$'))
async def photo_edit_callback(client, query: CallbackQuery):
    effect = query.data
    msg = query.message
    original = msg.reply_to_message

    if not original or not original.photo:
        return await query.answer("Original photo not found!", show_alert=True)

    await query.answer("Processing...")
    status = await msg.edit_text("⏳ **Processing your image...**")

    file_path = await client.download_media(original.photo.file_id)

    try:
        if effect == 'removebg':
            result_bytes = await apply_removebg(None, file_path)
            out_path = file_path + "_nobg.png"
            with open(out_path, 'wb') as f:
                f.write(result_bytes)
            await original.reply_document(
                out_path,
                caption="✅ **Background Removed!**\n\n@Astro_AF_bot"
            )
            os.remove(out_path)
        elif effect == 'stick':
            # Convert to sticker (WebP)
            img = Image.open(file_path).convert('RGBA')
            img.thumbnail((512, 512))
            out_path = file_path + ".webp"
            img.save(out_path, 'WEBP')
            await original.reply_sticker(out_path)
            os.remove(out_path)
        else:
            img = Image.open(file_path).convert('RGB')
            fn = EFFECTS.get(effect)
            if fn:
                result = fn(img)
            else:
                result = img
            out_path = file_path + f"_{effect.replace("|", "_")}.jpg"
            result.convert('RGB').save(out_path, 'JPEG', quality=95)
            await original.reply_photo(
                out_path,
                caption=f"✅ **Effect: {effect.upper()}**\n\n@Astro_AF_bot",
                reply_markup=get_buttons()
            )
            os.remove(out_path)

        await status.delete()

    except Exception as e:
        await status.edit(f"❌ **Error:** `{e}`")
        print(f"Photo editor error: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)