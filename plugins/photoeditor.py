# Photo Editor + OCR + QR Scanner — Fully fixed and improved
import os
import tempfile
import aiohttp
import random
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

REMOVE_BG_API = "Qextfp8qdDKoqH2bTdRsPCZ1"
USER_MODE = {}
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- BUTTONS ----------
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

def get_choice_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✒️ 𝗘𝗱𝗶𝘁 𝗣𝗵𝗼𝘁𝗼", callback_data="photo_edit_menu"),
            InlineKeyboardButton("🔍 𝗘𝘅𝘁𝗿𝗮𝗰𝘁 𝗧𝗲𝘅𝘁", callback_data="photo_ocr"),
        ],
        [
            InlineKeyboardButton("📱 𝗦𝗰𝗮𝗻 𝗤𝗥 𝗖𝗼𝗱𝗲", callback_data="photo_scanqr"),
        ]
    ])

# ---------- SAFE EDIT ----------
async def safe_edit(target_msg, text, reply_markup=None):
    try:
        try:
            return await target_msg.edit_text(text, reply_markup=reply_markup)
        except Exception:
            try:
                return await target_msg.reply(text, reply_markup=reply_markup)
            except Exception:
                return None
    except Exception:
        return None

# ---------- COMMANDS ----------
@Client.on_message(filters.command("photoeditor"))
async def photoeditor_cmd(client: Client, message: Message):
    USER_MODE[message.from_user.id] = "edit"
    await message.reply("✒️ 𝗣𝗵𝗼𝘁𝗼 𝗘𝗱𝗶𝘁𝗼𝗿\n\nSᴇɴᴅ A Pʜᴏᴛᴏ Tᴏ Mᴀᴋᴇ Eᴅɪᴛs.", quote=True)

@Client.on_message(filters.command("ocr"))
async def ocr_cmd(client: Client, message: Message):
    USER_MODE[message.from_user.id] = "ocr"
    await message.reply("🔍 𝗢𝗖𝗥\n\nSᴇɴᴅ A Pʜᴏᴛᴏ Tᴏ Exᴛʀᴀᴄᴛ Tᴇxᴛ.", quote=True)



# ---------- PHOTO HANDLER ----------
@Client.on_message(filters.photo & filters.private)
async def photo_handler(client: Client, message: Message):
    mode = USER_MODE.pop(message.from_user.id, None)

    if mode == "edit":
        await message.reply(
            "✒️ 𝗣𝗵𝗼𝘁𝗼 𝗘𝗱𝗶𝘁𝗼𝗿\n\nSᴇʟᴇᴄᴛ ᴀɴ ᴇғғᴇᴄᴛ:",
            reply_markup=get_buttons(),
            quote=True
        )
        return

    if mode == "ocr":
        status = await message.reply("🔍 Exᴛʀᴀᴄᴛɪɴɢ ᴛᴇxᴛ...", quote=True)
        await run_ocr(client, message, status)
        return

    if mode == "scanqr":
        status = await message.reply("📱 Sᴄᴀɴɴɪɴɢ QR Cᴏᴅᴇ...", quote=True)
        await run_scanqr(client, message, status)
        return

    # default — show choice
    await message.reply(
        "📸 Wʜᴀᴛ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏ ᴡɪᴛʜ ᴛʜɪs ᴘʜᴏᴛᴏ?",
        reply_markup=get_choice_buttons(),
        quote=True
    )

# ---------- MENU CALLBACKS ----------
@Client.on_callback_query(filters.regex(r"^photo_edit_menu$"))
async def show_edit_menu(client: Client, query: CallbackQuery):
    original = query.message.reply_to_message
    if not original or not original.photo:
        return await query.answer("Original photo not found!", show_alert=True)
    await query.answer()
    try:
        await query.message.edit("✒️ 𝗣𝗵𝗼𝘁𝗼 𝗘𝗱𝗶𝘁𝗼𝗿\n\nSᴇʟᴇᴄᴛ ᴀɴ ᴇғғᴇᴄᴛ:", reply_markup=get_buttons())
    except Exception:
        await query.message.reply("✒️ 𝗣𝗵𝗼𝘁𝗼 𝗘𝗱𝗶𝘁𝗼𝗿\n\nSᴇʟᴇᴄᴛ ᴀɴ ᴇғғᴇᴄᴛ:", reply_markup=get_buttons(), quote=True)

@Client.on_callback_query(filters.regex(r"^photo_ocr$"))
async def ocr_button(client: Client, query: CallbackQuery):
    original = query.message.reply_to_message
    if not original or not original.photo:
        return await query.answer("Original photo not found!", show_alert=True)
    await query.answer("Exᴛʀᴀᴄᴛɪɴɢ ᴛᴇxᴛ...")
    await safe_edit(query.message, "🔍 Exᴛʀᴀᴄᴛɪɴɢ ᴛᴇxᴛ...")
    await run_ocr(client, original, query.message)

@Client.on_callback_query(filters.regex(r"^photo_scanqr$"))
async def scanqr_button(client: Client, query: CallbackQuery):
    original = query.message.reply_to_message
    if not original or not original.photo:
        return await query.answer("Original photo not found!", show_alert=True)
    await query.answer("Sᴄᴀɴɴɪɴɢ QR...")
    await safe_edit(query.message, "📱 Sᴄᴀɴɴɪɴɢ QR Cᴏᴅᴇ...")
    await run_scanqr(client, original, query.message)

@Client.on_callback_query(filters.regex(r"^close_data$"))
async def close_menu(client: Client, query: CallbackQuery):
    try:
        await query.message.delete()
    except Exception:
        pass

# ---------- OCR ----------
async def run_ocr(client: Client, photo_message: Message, reply_target):
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    except Exception as e:
        await safe_edit(reply_target, f"❌ Tesseract import error: `{e}`")
        return

    path = None
    try:
        path = await client.download_media(photo_message.photo.file_id)
        img = Image.open(path)
        text = pytesseract.image_to_string(img).strip()
        if not text:
            text = "❌ No text found."
        if len(text) > 4000:
            text = text[:4000] + "\n\n_(Text truncated)_"
        await safe_edit(reply_target, f"🔍 Exᴛʀᴀᴄᴛᴇᴅ Tᴇxᴛ:\n\n`{text}`")
    except Exception as e:
        await safe_edit(reply_target, f"❌ OCR Error: `{e}`")
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

# ---------- QR SCANNER ----------
async def run_scanqr(client: Client, photo_message: Message, reply_target):
    path = None
    try:
        from pyzbar.pyzbar import decode
        path = await client.download_media(photo_message.photo.file_id)
        img = Image.open(path)
        decoded = decode(img)
        if decoded:
            results = "\n\n".join([f"**Result {i+1}:** `{d.data.decode('utf-8')}`" for i, d in enumerate(decoded)])
            await safe_edit(reply_target, f"📱 QR Cᴏᴅᴇ Sᴄᴀɴɴᴇᴅ!\n\n{results}")
        else:
            await safe_edit(reply_target, "❌ No QR code found in this image.")
    except Exception as e:
        await safe_edit(reply_target, f"❌ QR Scan Error: `{e}`")
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

# ---------- EFFECTS ----------
def apply_bright(img): return ImageEnhance.Brightness(img).enhance(1.5)
def apply_mix(img):
    img = img.convert("RGB"); r, g, b = img.split(); return Image.merge("RGB", (b, r, g))
def apply_bw(img): return img.convert("L").convert("RGB")
def apply_circle(img):
    img = img.convert("RGBA"); size = min(img.size)
    mask = Image.new("L", img.size, 0); draw = ImageDraw.Draw(mask)
    x0 = (img.width - size) // 2; y0 = (img.height - size) // 2
    draw.ellipse([x0, y0, x0+size, y0+size], fill=255); img.putalpha(mask)
    bg = Image.new("RGBA", img.size, (255,255,255,255)); bg.paste(img, mask=img.split()[3])
    return bg.convert("RGB")
def apply_blur(img): return img.filter(ImageFilter.GaussianBlur(radius=3))
def apply_border(img):
    b = ImageOps.expand(img.convert("RGB"), border=20, fill=(255,255,255))
    return ImageOps.expand(b, border=5, fill=(0,0,0))
def apply_rotate(img): return img.rotate(90, expand=True)
def apply_contrast(img): return ImageEnhance.Contrast(img).enhance(2.0)
def apply_sepia(img):
    img = img.convert("RGB"); px = img.load()
    for x in range(img.width):
        for y in range(img.height):
            r,g,b = px[x,y]
            px[x,y] = (min(int(0.393*r+0.769*g+0.189*b),255), min(int(0.349*r+0.686*g+0.168*b),255), min(int(0.272*r+0.534*g+0.131*b),255))
    return img
def apply_pencil(img):
    import numpy as np
    g = img.convert("L"); inv = ImageOps.invert(g); bl = inv.filter(ImageFilter.GaussianBlur(10))
    arr = np.array(g, dtype=float); ba = np.array(bl, dtype=float)
    return Image.fromarray((arr/(255-ba+1)*255).clip(0,255).astype('uint8')).convert("RGB")
def apply_cartoon(img):
    s = img.filter(ImageFilter.SMOOTH_MORE); e = img.filter(ImageFilter.FIND_EDGES).convert("RGB")
    return Image.blend(s.convert("RGB"), e, alpha=0.3)
def apply_inverted(img): return ImageOps.invert(img.convert("RGB"))
def apply_glitch(img):
    import numpy as np
    arr = np.array(img.convert("RGB")); h = arr.shape[0]
    for _ in range(10):
        y = random.randint(0, max(0,h-1)); arr[y] = np.roll(arr[y], random.randint(-50,50), axis=0)
    return Image.fromarray(arr)

async def apply_removebg(file_path):
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("image_file", f, filename="image.jpg", content_type="image/jpeg")
            data.add_field("size", "auto")
            async with session.post("https://api.remove.bg/v1.0/removebg", data=data,
                headers={"X-Api-Key": REMOVE_BG_API}, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200: return await resp.read()
                raise Exception(f"remove.bg failed ({resp.status}): {await resp.text()}")

def make_sticker_from_image(in_path, out_path):
    img = Image.open(in_path).convert("RGBA"); img.thumbnail((512,512), Image.LANCZOS)
    canvas = Image.new("RGBA", (512,512), (0,0,0,0))
    canvas.paste(img, ((512-img.width)//2, (512-img.height)//2), img)
    canvas.save(out_path, "WEBP")

EFFECTS = {
    "bright": apply_bright, "mix": apply_mix, "b|w": apply_bw,
    "circle": apply_circle, "blur": apply_blur, "border": apply_border,
    "rotate": apply_rotate, "contrast": apply_contrast, "sepia": apply_sepia,
    "pencil": apply_pencil, "cartoon": apply_cartoon, "inverted": apply_inverted,
    "glitch": apply_glitch,
}

# ---------- EFFECT CALLBACK ----------
@Client.on_callback_query(filters.regex(r"^(bright|mix|b\|w|circle|blur|border|stick|rotate|contrast|sepia|pencil|cartoon|inverted|glitch|removebg)$"))
async def photo_edit_callback(client: Client, query: CallbackQuery):
    effect = query.data
    msg = query.message
    original = msg.reply_to_message

    if not original or not original.photo:
        return await query.answer("Original photo not found", show_alert=True)

    await query.answer("⏳ Pʀᴏᴄᴇssɪɴɢ...")
    status_msg = None
    try:
        try:
            status_msg = await msg.edit_text("⏳ Pʀᴏᴄᴇssɪɴɢ...")
        except Exception:
            status_msg = await msg.reply("⏳ Pʀᴏᴄᴇssɪɴɢ...", quote=True)
    except Exception:
        status_msg = None

    src_path = None
    try:
        src_path = await client.download_media(original.photo.file_id)

        if effect == "stick":
            with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                make_sticker_from_image(src_path, tmp_path)
                await original.reply_sticker(tmp_path)
            finally:
                if os.path.exists(tmp_path): os.remove(tmp_path)

        elif effect == "removebg":
            try:
                data = await apply_removebg(src_path)
                with tempfile.NamedTemporaryFile(suffix="_nobg.png", delete=False) as tmp:
                    tmp.write(data); tmp_path = tmp.name
                try:
                    await original.reply_document(tmp_path, caption="✅ Background removed")
                finally:
                    if os.path.exists(tmp_path): os.remove(tmp_path)
            except Exception as e:
                await safe_edit(status_msg or msg, f"❌ Remove.bg error: `{e}`")
        else:
            func = EFFECTS.get(effect)
            if not func:
                await safe_edit(status_msg or msg, "❌ Effect not implemented.")
            else:
                img = Image.open(src_path).convert("RGB")
                result = func(img)
                safe_effect = effect.replace("|", "w")
                with tempfile.NamedTemporaryFile(suffix=f"_{safe_effect}.jpg", delete=False) as tmpf:
                    tmp_path = tmpf.name
                    result.convert("RGB").save(tmp_path, "JPEG", quality=95)
                try:
                    await original.reply_photo(tmp_path, caption=f"✅ Effect: {effect.upper()}", reply_markup=get_buttons())
                finally:
                    if os.path.exists(tmp_path): os.remove(tmp_path)

        if status_msg:
            try: await status_msg.delete()
            except Exception: pass

    except Exception as e:
        try:
            await safe_edit(status_msg or msg, f"❌ Error: `{e}`")
        except Exception:
            pass
    finally:
        if src_path and os.path.exists(src_path):
            try: os.remove(src_path)
            except Exception: pass