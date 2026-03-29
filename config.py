#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import re
from os import environ
import os

id_pattern = re.compile(r'^.\d+$')


API_ID = os.environ.get("API_ID", "23991460")
API_HASH = os.environ.get("API_HASH", "482b9c11ca28fdff8f0d3f9223ef0ac1")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7766638158:AAFKkI3Tm5WDac-1uFDBztMqq1QzRHn64cc")
ADMIN = int(os.environ.get("ADMIN", '2052400282'))
FSUB_UPDATES = os.environ.get("FSUB_CHANNEL", "compressbotlogs1")
FSUB_GROUP = os.environ.get("FSUB_GROUP", "multibotvi")
DATABASE_URI = os.environ.get("DATABASE_URI", "mongodb+srv://chpudas:SPNjedirQ26Nungu@clustercompressbot.qnztune.mongodb.net/?retryWrites=true&w=majority&appName=Clustercompressbot")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "Clustercompressbot")
CAPTION = os.environ.get("CAPTION", "")
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
SUNRISES_PIC= "https://ibb.co/8n4vFcmt"  # Replace with your Telegraph link
AUTH_USERS = int(os.environ.get("AUTH_USERS", '2052400282'))
WEBHOOK = bool(os.environ.get("WEBHOOK", True))
PORT = int(os.environ.get("PORT", "8081"))
LOG_CHANNEL_ID = os.environ.get("LOG_CHANNEL_ID", -1002820046126)
