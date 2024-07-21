#SUNRISES24BOTS
#TG:@SUNRISES_24
from pyrogram import Client
from aiohttp import web
from main.web_support import web_server
from config import *
import os


class Bot(Client):    

    def __init__(self):
        super().__init__(
            name="MetaMorpher",
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
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()        
        await self.send_message(GROUP, f"{me.first_name} | @{me.username} 𝚂𝚃𝙰𝚁𝚃𝙴𝙳...⚡️")
        
                
        
    async def stop(self, *args):
       await super().stop()      
       print("Bot Restarting........")

bot = Bot()
bot.run()
