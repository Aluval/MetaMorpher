#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import re
from os import environ
import os

id_pattern = re.compile(r'^.\d+$')


API_ID = int(os.environ.get("API_ID", "24464839"))
API_HASH = os.environ.get("API_HASH", "c906bdd79dae0c7e6b8446db37128705")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6759334684:AAEzkcL0oBzKJUrm1JLipJNVA3S6TPb5HDw")
ADMIN = int(os.environ.get("ADMIN", '5806876587')) 
FSUB_UPDATES = os.environ.get("FSUB_CHANNEL", "knmoviez")
FSUB_GROUP = os.environ.get("FSUB_GROUP", "logsforkn")
CAPTION = os.environ.get("CAPTION", "")
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
DOWNLOAD_LOCATION = "./DOWNLOADS"
group = environ.get('GROUP', '-1002144228393')
GROUP = int(group) if group and id_pattern.search(group) else None
SUNRISES_PIC= "https://graph.org/file/bd91761f6e938e2e6d23a.jpg"  # Replace with your Telegraph link
AUTH_USERS = int(os.environ.get("AUTH_USERS", ''))



