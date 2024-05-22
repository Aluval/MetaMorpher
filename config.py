#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import re
from os import environ
import os
id_pattern = re.compile(r'^.\d+$')


API_ID = int(os.environ.get("API_ID", "10811400"))
API_HASH = os.environ.get("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6487202001:AAEHi58S7R8wVf99IaTqBVlmQo-lzyn7QsU")
ADMIN = int(os.environ.get("ADMIN", "6469754522")) 
FSUB_CHANNEL = os.environ.get("FSUB_CHANNEL", "Sunrises24BotUpdates")
FSUB_GROUP = os.environ.get("FSUB_GROUP", "INFINITYRENAME24GROUP")
CAPTION = os.environ.get("CAPTION", "")
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
DOWNLOAD_LOCATION = "./DOWNLOADS"
group = environ.get('GROUP', '-1002128043143')
GROUP = int(group) if group and id_pattern.search(group) else None
SUNRISES_PIC= "https://graph.org/file/5966e801852b2bba18afb.jpg"  # Replace with your Telegraph link

