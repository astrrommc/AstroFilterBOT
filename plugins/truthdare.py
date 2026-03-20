import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton 
TRUTHS = [
    "What is the most embarrassing thing you've ever done?",
    "Have you ever lied to your best friend? What was it about?",
    "What is your biggest fear?",
    "Have you ever cheated on a test?",
    "What is the most childish thing you still do?",
    "What is your biggest secret?",
    "Have you ever pretended to be sick to avoid something?",
    "What is the worst gift you've ever received?",
    "Have you ever blamed someone else for something you did?",
    "What is one thing you would change about yourself?",
    "Have you ever stalked someone on social media?",
    "What is your most embarrassing moment in public?",
    "Have you ever said 'I love you' and not meant it?",
    "What is something you've never told your parents?",
    "Have you ever sent a message to the wrong person?",
    "What is the biggest lie you've ever told?",
    "Have you ever laughed at the wrong moment?",
    "What is something you're ashamed of?",
    "Have you ever stolen anything?",
    "Who was your first crush?",
    "What is the most disgusting thing you've ever eaten?",
    "Have you ever cried during a movie? Which one?",
    "What is your most used app and why?",
    "Have you ever ghosted someone?",
    "What is the worst thing you've ever said to someone?",
    "Have you ever fallen asleep in class or at work?",
    "What is something you've always wanted to try but never did?",
    "Have you ever read someone else's messages without permission?",
    "What is the most expensive thing you've ever broken?",
    "Have you ever pretended not to see someone in public to avoid them?",
]

DARES = [
    "Send a voice message singing your favorite song.",
    "Change your profile picture to a funny face for 1 hour.",
    "Send a message to your crush right now.",
    "Do 20 pushups and send a video.",
    "Send the last photo in your gallery.",
    "Text your mom 'I just saw a ghost' and send a screenshot.",
    "Speak in rhymes for the next 5 minutes.",
    "Send a selfie with the most ridiculous face you can make.",
    "Write a poem about the person above you right now.",
    "Send a message to a random contact saying 'I miss you'.",
    "Do your best animal impression in a voice message.",
    "Send a screenshot of your most used emojis.",
    "Change your name in this chat to something funny for 10 minutes.",
    "Send a voice message saying 'I am the best' 5 times.",
    "Share your top 3 most played songs.",
    "Send a screenshot of your search history.",
    "Describe yourself in 3 emojis only.",
    "Send the most cringe thing in your gallery.",
    "Write a 2-line love poem for someone in this chat.",
    "Send a voice message in a funny accent.",
    "Admit the last thing you lied about.",
    "Send a screenshot of your last WhatsApp conversation.",
    "Do a 30 second dance and send a video.",
    "Send a message to your boss/teacher that says 'sup'.",
    "Rate everyone in this chat from 1-10.",
    "Send a voice message of you laughing for 10 seconds.",
    "Text 'I think you're amazing' to the 5th person in your contacts.",
    "Send a picture of your current hairstyle.",
    "Share an embarrassing photo of yourself.",
    "Let someone in this chat post anything on your behalf.",
]

def get_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😇 Truth", callback_data="tod_truth"),
            InlineKeyboardButton("😈 Dare", callback_data="tod_dare"),
        ],
        [
            InlineKeyboardButton("🎲 Random", callback_data="tod_random"),
            InlineKeyboardButton("❌ Close", callback_data="close_data"),
        ]
    ])

@Client.on_message(filters.command(["truth", "dare", "tod", "truthordare"]), group=-1)
async def truth_or_dare(client, message: Message):
    cmd = message.command[0].lower()
    
    if cmd == "truth":
        text = f"😇 **Truth:**\n\n_{random.choice(TRUTHS)}_"
    elif cmd == "dare":
        text = f"😈 **Dare:**\n\n_{random.choice(DARES)}_"
    else:
        await message.reply(
            "🎮 **Truth or Dare**\n\nChoose your fate!",
            reply_markup=get_buttons()
        )
        return

    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😇 New Truth", callback_data="tod_truth"),
                InlineKeyboardButton("😈 New Dare", callback_data="tod_dare"),
            ],
            [
                InlineKeyboardButton("🎲 Random", callback_data="tod_random"),
                InlineKeyboardButton("❌ Close", callback_data="close_data"),
            ]
        ])
    )

@Client.on_callback_query(filters.regex("^tod_"), group=-1)
async def tod_callback(client, query):
    action = query.data.split("_")[1]

    if action == "truth":
        text = f"😇 **Truth:**\n\n_{random.choice(TRUTHS)}_"
    elif action == "dare":
        text = f"😈 **Dare:**\n\n_{random.choice(DARES)}_"
    else:  # random
        if random.choice([True, False]):
            text = f"😇 **Truth:**\n\n_{random.choice(TRUTHS)}_"
        else:
            text = f"😈 **Dare:**\n\n_{random.choice(DARES)}_"

    await query.answer()
    try:
        await query.message.edit(
            text,
            reply_markup=get_buttons()
        )
    except Exception as e:
        print(e)