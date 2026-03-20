import math
import time 
from Script import script
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import enums

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    
    # FIXED: Update every 5 seconds (instead of 10) for a smoother Kochi fiber reading
    # This prevents the "stuttering" progress bar on 100 Mbps lines
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        
        # SPEED CALCULATION
        speed = current / diff
        
        # ETA CALCULATION FIX: 
        # We only care about how many milliseconds are LEFT (time_to_completion)
        if speed > 0:
            time_to_completion = round((total - current) / speed) * 1000
        else:
            time_to_completion = 0

        # Formatter for the remaining time only
        eta_time = TimeFormatter(milliseconds=time_to_completion)

        progress = "{0}{1}".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]))
            
        # script.PROGRESS_BAR usually expects: percentage, current, total, speed, eta
        tmp = progress + script.PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            eta_time if eta_time != '' else "0s" # Now shows time REMAINING
        )
        
        try:
            await message.edit(
                text="{}\n\n{}".format(ud_type, tmp),               
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="cancel")
                ]])
            )
        except Exception as e:
            pass # Ignore "Message is not modified" errors during high-speed bursts

def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    # Optimized to show a clean, short ETA for renaming
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s") if seconds else "")
    return tmp if tmp else "0s"

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)