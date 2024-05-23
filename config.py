#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import re
from os import environ
import os
from pyrogram import Client
id_pattern = re.compile(r'^.\d+$')


API_ID = int(os.environ.get("API_ID", "10811400"))
API_HASH = os.environ.get("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6487202001:AAEHi58S7R8wVf99IaTqBVlmQo-lzyn7QsU")
ADMIN = int(os.environ.get("ADMIN", "6469754522")) 
FSUB_UPDATES = os.environ.get("FSUB_CHANNEL", "Sunrises24BotUpdates")
FSUB_GROUP = os.environ.get("FSUB_GROUP", "INFINITYRENAME24GROUP")
CAPTION = os.environ.get("CAPTION", "")
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
DOWNLOAD_LOCATION = "./DOWNLOADS"
group = environ.get('GROUP', '-1002128043143')
GROUP = int(group) if group and id_pattern.search(group) else None
SUNRISES_PIC= "https://graph.org/file/5966e801852b2bba18afb.jpg"  # Replace with your Telegraph link

# Constants
FILE_SIZE_LIMIT = 2 * 1024 * 1024 * 1024  # 2 GB

# Config class to hold your configurations
STRING_SESSION = os.environ.get("STRING_SESSION", "BQCk-AgAXjv-rvP8Q3ZK7uVQ4bc6maTPaqtZ6iFqJDxWELtFu74RHoIvXfn6dLPZ9b1u9fWlV4ZqFJmWKm4jXrbw_LzfAeuYLbiFgdAcZ-mKa22oeHOZuN2iFFYzKCeDBOA4ZgJX74pQo8EliICqLxXI7Jo3gOPElzU3O11CS4kxFMGylSW_vSW9v6lTimUGXz4aW6Te-VkWLUmzQrvOiWaObizOe_y1dK3CXwNfCp0mzh1cDbTmGpAiHG5ShRC4Du2sAPudcnobX9hrPRKp5Ly0M0AOVnpJtKfh1zyOzDWjwoY9qA97hoyd1ITfNg8ZBHHe3a_2gKh2Lj85OWNANgL8doeABAAAAAGBoJ6aAA")


# Initialize the string session client
string_session_client = Client("my_session", api_id="10811400", api_hash="191bf5ae7a6c39771e7b13cf4ffd1279", session_string=STRING_SESSION)

