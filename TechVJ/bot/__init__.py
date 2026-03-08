# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, types
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from aiohttp import web


class TechVJXBot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            # MAXIMIZED: 300 workers allow your PC to fully saturate your 48.5 Mbps upload
            workers=300, 
            plugins={"root": "plugins"},
            # STABILITY: Higher threshold prevents the bot from hanging during heavy traffic
            sleep_threshold=60,
        )

    async def set_self(self):
        temp.BOT = self
    
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
      
TechVJBot = TechVJXBot()

multi_clients = {}
work_loads = {}
