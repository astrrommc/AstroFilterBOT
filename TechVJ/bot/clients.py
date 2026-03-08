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
            
            # OPTIMIZED CLIENT FOR MAXIMUM PC SPEED
            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                # Increased workers to 300 to fully saturate your 48.5 Mbps upload
                workers=300, 
                # Set sleep_threshold to 60 to handle heavy Telegram traffic without hanging
                sleep_threshold=60,
                no_updates=True,
                in_memory=True
            ).start()
            
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
    
    # Using asyncio.gather to start all worker clients in parallel for faster boot-up
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    
    if len(multi_clients) != 1:
        # Global variable updated to enable multi-client load balancing
        global MULTI_CLIENT
        MULTI_CLIENT = True
        print("Multi-Client Mode Enabled (Maximum Speed Mode)")
    else:
        print("No additional clients were initialized, using default client")
        
