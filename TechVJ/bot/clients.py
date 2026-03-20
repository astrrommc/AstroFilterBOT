# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
from info import *
from pyrogram import Client
from TechVJ.util.config_parser import TokenParser
from TechVJ.bot import multi_clients, work_loads, TechVJBot


async def initialize_clients():
    multi_clients[0] = TechVJBot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    
    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            
            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                workers=300,
                sleep_threshold=60,
                no_updates=True,
                in_memory=True,
                max_concurrent_transmissions=10,  # parallel connections per client
            ).start()
            
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
    
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    
    if len(multi_clients) != 1:
        global MULTI_CLIENT
        MULTI_CLIENT = True
        print(f"Multi-Client Mode Enabled — {len(multi_clients)} clients active")
    else:
        print("No additional clients were initialized, using default client")