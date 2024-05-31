#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
from pyrogram import Client, filters 
from config import DOWNLOAD_LOCATION
import os
from config import GROUP

dir = os.listdir(DOWNLOAD_LOCATION)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_message(filters.photo & filters.chat(GROUP))                            
async def set_tumb(bot, msg):       
    if len(dir) == 0:
        await bot.download_media(message=msg.photo.file_id, file_name=f"{DOWNLOAD_LOCATION}/thumbnail.jpg")
        return await msg.reply(f"Your permanent thumbnail is saved ✅️ \nIf Bot is restarted the thumbnail will delete⚠️")            
    else:    
        os.remove(f"{DOWNLOAD_LOCATION}/thumbnail.jpg")
        await bot.download_media(message=msg.photo.file_id, file_name=f"{DOWNLOAD_LOCATION}/thumbnail.jpg")               
        return await msg.reply(f"Your permanent thumbnail is saved ✅️ \nIf Bot is restarted the thumbnail will delete⚠️")            

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_message(filters.command("view")  & filters.chat(GROUP))                            
async def view_tumb(bot, msg):
    try:
        await msg.reply_photo(photo=f"{DOWNLOAD_LOCATION}/thumbnail.jpg", caption="this is your current thumbnail")
    except Exception as e:
        print(e)
        return await msg.reply_text(text="you don't have any thumbnail")

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_message(filters.command(["del", "del_thumb"]) & filters.chat(GROUP))                         
async def del_tumb(bot, msg):
    try:
        os.remove(f"{DOWNLOAD_LOCATION}/thumbnail.jpg")
        await msg.reply_text("your thumbnail was removed❌")
    except Exception as e:
        print(e)
        return await msg.reply_text(text="you don't have any thumbnail‼️")

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
    
