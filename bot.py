import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path
from datetime import date, datetime
from aiohttp import web
from pyrogram import idle

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from database.users_chats_db import db
from database.ia_filterdb import create_indexes
from info import *
from utils import temp
from Script import script
from plugins import web_server
from plugins.clone import restart_bots
from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients


def load_plugins():
    for filepath in glob.glob("plugins/*.py"):
        try:
            plugin_name = Path(filepath).stem
            import_path = f"plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(import_path, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[import_path] = module
            print(f"  ✔ {plugin_name}")
        except Exception as e:
            print(f"  ✘ {plugin_name}: {e}")


async def _ping_channel(ch):
    try:
        k = await TechVJBot.send_message(ch, "**Bot Restarted**")
        await k.delete()
    except:
        pass


async def notify_channels():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")
    try:
        await TechVJBot.send_message(LOG_CHANNEL, script.RESTART_TXT.format(date.today(), time_str))
    except Exception as e:
        print(f"  ✘ Log channel: {e}")
    await asyncio.gather(*[_ping_channel(ch) for ch in CHANNELS], return_exceptions=True)


async def start():
    print("\n🚀 Starting Astro Bot...\n")

    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    print(f"✅ Connected: @{me.username} | {me.first_name}\n")

    try:
        await initialize_clients()
    except Exception as e:
        print(f"⚠ Clients: {e}")

    print("📦 Loading plugins...")
    load_plugins()
    print()

    try:
        temp.BANNED_USERS, temp.BANNED_CHATS = await db.get_banned()
    except Exception as e:
        print(f"⚠ Database: {e}")

    # Create DB indexes for faster search
    try:
        await create_indexes()
    except Exception as e:
        print(f"⚠ Indexes: {e}")

    asyncio.create_task(notify_channels())

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    if CLONE_MODE:
        try:
            await restart_bots()
        except Exception as e:
            print(f"⚠ Clone bots: {e}")

    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        print(f"🌐 Web server running on port {PORT}")
    except Exception as e:
        print(f"⚠ Web server: {e}")

    print("\n✅ Bot is ready!\n")
    await idle()


if __name__ == '__main__':
    TechVJBot.start()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")