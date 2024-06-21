#SUNRISES24BOTS
#TG:@SUNRISES_24
from pyrogram import Client
from config import *
import os
import signal
import sys
import time

def graceful_exit(signum, frame):
    print('Received SIGTERM, shutting down gracefully...')
    # Perform cleanup tasks here
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_exit)

# Your rename logic here
while True:
    time.sleep(1)


class Bot(Client):
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

    def __init__(self):
        super().__init__(
            name="INFINITYSTARRENAME24BOT",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=100,
            plugins={"root": "main"},
            sleep_threshold=10,
        )
    async def start(self):
        await super().start()
        me = await self.get_me() 
        GROUP_ID = -1002128043143  # Replace YOUR_GROUP_ID with the actual group ID
        await self.send_message(GROUP_ID, f"{me.first_name} | @{me.username} 𝚂𝚃𝙰𝚁𝚃𝙴𝙳...⚡️")
        
        
    async def stop(self, *args):
       await super().stop()      
       print("Bot Restarting........")

bot = Bot()
bot.run()
