import random
from pyrogram import Client, filters



def aesthetify(string):
    PRINTABLE_ASCII = range(0x21, 0x7f)
    for c in string:
        c_ord = ord(c)
        if c_ord in PRINTABLE_ASCII:
            c_ord += 0xFF00 - 0x20
        elif c_ord == ord(" "):
            c_ord = 0x3000
        yield chr(c_ord)

# --- AESTHETIC TEXT ---

@Client.on_message(filters.command(["ae"]))
async def aesthetic_cmd(client, message):
    # Fix: Prevent IndexError if no text is provided
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/ae Hello World</code>")
    
    status_message = await message.reply_text("<code>Processing...</code>")
    # Join command arguments into a single string with spaces
    input_text = " ".join(message.command[1:])
    text = "".join(aesthetify(input_text))
    await status_message.edit(text)

# --- GAMES LOGIC ---

async def send_game(client, message, emoji):
    """Universal helper to send animated games"""
    # Fix: use message.id instead of message_id for modern Pyrogram
    rep_id = message.reply_to_message.id if message.reply_to_message else message.id
    try:
        await client.send_dice(
            chat_id=message.chat.id,
            emoji=emoji,
            reply_to_message_id=rep_id
        )
    except Exception as e:
        await message.reply_text(f"<b>Error:</b> <code>{e}</code>")

@Client.on_message(filters.command(["throw", "dart"]))
async def dart_cmd(c, m): 
    await send_game(c, m, "🎯")

@Client.on_message(filters.command(["roll", "dice"]))
async def dice_cmd(c, m): 
    await send_game(c, m, "🎲")

@Client.on_message(filters.command(["luck", "cownd"]))
async def slot_cmd(c, m): 
    await send_game(c, m, "🎰")

@Client.on_message(filters.command(["goal", "shoot"]))
async def goal_cmd(c, m): 
    # Fix: renamed function from 'roll_dice' to 'goal_cmd' to avoid conflict
    await send_game(c, m, "⚽")

# --- RANDOM RUNS ---

RUN_STRINGS = (
    "A broken of a demeanly filled with darkness... Why have you come to remind it?",
    "We have become the lives to be the underwater to the underwater that we do not know.",
    "You want the bad call ... but you need good thunder ....",
    "Oh Bloody Grama Virtues!",
    "Sea MUGGie I Am Going to Pay The Bill.",
    "Want with me!",
    "You are not a male chaff !!",
    "I locked it, and the good beach is done by the good beach.",
    "Kindi ... Kindi ...!",
    "Giving the stems and then showing one and show the ISI Mark",
    "Dayveyeese, Kingfisher ... Childe ...!.",
    "You have made your father for half of the midnight?",
    "This is the King of our work.",
    "I'm fetts to feed ....",
    "Mumak is every Bearby Kachyo ...",
    "Oh it moves it .... When we moves it ...",
    "The self of carpenter is the virtue of a carpenter.",
    "Why not to feel this intelligence in Da Vijaya ...!",
    "Where was this time ....",
    "Save me only ....",
    "I know his father's name is Bhavaniami ....",
    "Da Dasa ...",
    "Uppukam's English Salt Mongo Tree .....",
    "Children ..",
    "Your father to Paul ....",
    "Car Engine Out Completely .....",
    "This is the eye or magnety ...",
    "Before falling in the 4th pegging, I will arrive there.",
    "The drunk rains and wast ....",
    "To tell me I love Yo ....",
    "No, the Meenaka of Verbapur is not ....",
)

@Client.on_message(filters.command("runs"))
async def runs_cmd(_, message):
    effective_string = random.choice(RUN_STRINGS)
    if message.reply_to_message:
        # If replying to someone, reply with the quote
        await message.reply_to_message.reply_text(effective_string)
    else:
        await message.reply_text(effective_string)