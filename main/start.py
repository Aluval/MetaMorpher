#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import asyncio, time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UserNotParticipant, UserBannedInChannel
from config import FSUB_UPDATES, FSUB_GROUP, SUNRISES_PIC

START_TEXT = """
Hᴇʟʟᴏ Mᴀᴡа❤️! I ᴀᴍ ᴛʜᴇ Aᴅᴠᴀɴᴄᴇᴅ Rᴇɴᴀᴍᴇ 𝟸𝟺 Bᴏᴛ [MᴇᴛᴀMᴏʀᴘʜᴇʀ]⚡

Mᴀᴅᴇ ʙʏ <b><a href=https://t.me/Sunrises24botupdates>SUNRISES ™💥</a></b> ᴀɴᴅ <b><a href=https://t.me/Sunrises_24>Sᴜɴʀɪꜱᴇꜱ Hᴀʀꜱʜᴀ 𝟸𝟺❤️</a></b>.

Fᴇᴀᴛᴜʀᴇs:

- Rᴇɴᴀᴍᴇ Fɪʟᴇs
- Mᴀɴᴀɢᴇ Mᴇᴛᴀᴅᴀᴛᴀ
- Gᴇɴᴇʀᴀᴛᴇ Sᴀᴍᴘʟᴇs
- Mᴇʀɢᴇ Vɪᴅᴇᴏs
- Uᴘʟᴏᴀᴅ ᴛᴏ Gᴏғɪʟᴇ
- Sᴄʀᴇᴇɴsʜᴏᴛs & Uɴᴢɪᴘ
- Aᴛᴛᴀᴄʜ Pʜᴏᴛᴏs
- Mɪʀʀᴏʀ ᴛᴏ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ
- Cʟᴏɴᴇ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ Lɪɴᴋs
- Lɪsᴛ Fɪʟᴇs ɪɴ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ
- Cʟᴇᴀɴ Fɪʟᴇs ɪɴ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ
- Exᴛʀᴀᴄᴛ Aᴜᴅɪᴏs, Sᴜʙᴛɪᴛʟᴇs, Vɪᴅᴇᴏs
- Lᴇᴇᴄʜ: Wᴏʀᴋᴇʀs & Sᴇᴇᴅʀ Lɪɴᴋs
- Uᴘʟᴏᴀᴅ Lᴀʀɢᴇ Fɪʟᴇs (𝟺GB+) ᴛᴏ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ

Exᴘʟᴏʀᴇ sɪᴍᴘʟɪᴄɪᴛʏ! 💥

#SUNRISES24BOTS #SIMPLERENAME24BOT
"""

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
 
joined_channel_1 = {}
joined_channel_2 = {}

@Client.on_message(filters.command("start"))
async def start(bot, msg: Message):
    user_id = msg.chat.id
    
    # Check for channel 1 (updates channel) membership
    if FSUB_UPDATES:
        try:
            user = await bot.get_chat_member(FSUB_UPDATES, user_id)
            if user.status == "kicked":
                await msg.reply_text("Sorry, you are **banned**.")
                return
        except UserNotParticipant:
            await msg.reply_text(
                text="**Please join my first updates channel before using me.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="Join Updates Channel", url=f"https://t.me/{FSUB_UPDATES}")]
                ])
            )
            joined_channel_1[user_id] = False
            return
        else:
            joined_channel_1[user_id] = True

    # Check for channel 2 (group) membership
    if FSUB_GROUP:
        try:
            user = await bot.get_chat_member(FSUB_GROUP, user_id)
            if user.status == "kicked":
                await msg.reply_text("Sorry, you are **banned**.")
                return
        except UserNotParticipant:
            await msg.reply_text(
                text="**Please join my Group before using me.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="JOIN GROUP", url=f"https://t.me/{FSUB_GROUP}")]
                ])
            )
            joined_channel_2[user_id] = False
            return
        else:
            joined_channel_2[user_id] = True

    # If the user has joined both required channels, send the start message with photo
    start_text = START_TEXT.format(msg.from_user.first_name) if hasattr(msg, "message_id") else START_TEXT
    await bot.send_photo(
        chat_id=user_id,
        photo=SUNRISES_PIC,
        caption=start_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Developer ❤️", url="https://t.me/Sunrises_24"),
             InlineKeyboardButton("Updates 📢", url="https://t.me/Sunrises24botupdates")],
            [InlineKeyboardButton("Help 🌟", callback_data="help"),
             InlineKeyboardButton("About 🧑🏻‍💻", callback_data="about")],
            [InlineKeyboardButton("Support ❤️‍🔥", url="https://t.me/Sunrises24botSupport")]
        ]),
        reply_to_message_id=getattr(msg, "message_id", None)
    )

async def check_membership(bot, msg: Message, fsub, joined_channel_dict, prompt_text, join_url):
    user_id = msg.chat.id
    if user_id in joined_channel_dict and not joined_channel_dict[user_id]:
        await msg.reply_text(
            text=prompt_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Join Now", url=join_url)]
            ])
        )
        return False
    return True

@Client.on_message(filters.private & ~filters.command("start"))
async def handle_private_message(bot, msg: Message):
    user_id = msg.chat.id
    
    # Check membership for updates channel
    if FSUB_UPDATES and not await check_membership(bot, msg, FSUB_UPDATES, joined_channel_1, "Please join my first updates channel before using me.", f"https://t.me/{FSUB_UPDATES}"):
        return
    
    # Check membership for group channel
    if FSUB_GROUP and not await check_membership(bot, msg, FSUB_GROUP, joined_channel_2, "Please join my Group before using me.", f"https://t.me/{FSUB_GROUP}"):
        return
    

                          
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#FUNCTION ABOUT HANDLER
@Client.on_message(filters.command("about"))
async def about_command(bot, msg):
    about_text = """
<b>✯ Mʏ Nᴀᴍᴇ : <a href=https://t.me/MetaMorpher24Bot>𝐌𝐞𝐭𝐚𝐌𝐨𝐫𝐩𝐡𝐞𝐫 🌟</a></b>
<b>✯ Dᴇᴠᴇʟᴏᴘᴇʀ 🧑🏻‍💻 : <a href=https://t.me/Sunrises_24>𝐒𝐔𝐍𝐑𝐈𝐒𝐄𝐒™ ⚡</a></b>
<b>✯ Uᴘᴅᴀᴛᴇs 📢 : <a href=https://t.me/Sunrises24BotUpdates>𝐔𝐏𝐃𝐀𝐓𝐄𝐒 📢</a></b>
<b>✯ Sᴜᴘᴘᴏʀᴛ ✨ : <a href=https://t.me/Sunrises24BotUpdates>𝐒𝐔𝐏𝐏𝐎𝐑𝐓 ✨</a></b>
<b>✯ Bᴜɪʟᴅ Sᴛᴀᴛᴜs 📊 : ᴠ2.4 [Sᴛᴀʙʟᴇ]</b>
    """
    await msg.reply_text(about_text)

# Function to handle /help command
@Client.on_message(filters.command("help"))
async def help_command(bot, msg):
    help_text = """
    <b>Hᴇʟʟᴏ Mᴀᴡᴀ ❤️
Hᴇʀᴇ Is Tʜᴇ Hᴇʟᴘ Fᴏʀ Mʏ Cᴏᴍᴍᴀɴᴅs.

🦋 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ
◉ Reply To Any Video/File 🖼️

/start - 𝐵𝑜𝑡 𝑎𝑙𝑖𝑣𝑒 𝑜𝑟 𝑁𝑜𝑡 🚶🏻
/usersettings - 𝑂𝑝𝑒𝑛 𝑡ℎ𝑒 𝑈𝑠𝑒𝑟𝑠𝑒𝑡𝑡𝑖𝑛𝑔𝑠 𝐹𝑜𝑟 𝐵𝑜𝑡 𝐼𝑛𝑓𝑜
/bsettings - 𝐵𝑜𝑡 𝑆𝑒𝑡𝑡𝑖𝑛𝑔𝑠 𝐸𝑛𝑎𝑏𝑙𝑒𝑑 𝑜𝑟 𝐷𝑖𝑠𝑎𝑏𝑙𝑒𝑑 [𝐴𝐷𝑀𝐼𝑁]
/setmetadata - 𝑆𝑒𝑡 𝑀𝑒𝑡𝑎𝑑𝑎𝑡𝑎 𝐼𝑛𝑑𝑖𝑣𝑖𝑑𝑢𝑎𝑙 𝑇𝑖𝑡𝑙𝑒𝑠
/gofilesetup - 𝑆𝑒𝑡𝑢𝑝 𝑇ℎ𝑒 𝐺𝑜𝑓𝑖𝑙𝑒 𝐴𝑃𝐼 𝐾𝐸𝑌 𝑓𝑟𝑜𝑚 𝐺𝑜𝑓𝑖𝑙𝑒.𝑖𝑜 ⚙️[𝑃𝑟𝑖𝑣𝑎𝑡𝑒]
/gdriveid - 𝑇ℎ𝑒 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝐹𝑜𝑙𝑑𝑒𝑟 𝐼𝐷 𝑆𝑒𝑡𝑢𝑝 📁[𝑃𝑟𝑖𝑣𝑎𝑡𝑒]
/mirror - 𝑀𝑖𝑟𝑟𝑜𝑟 𝑓𝑖𝑙𝑒𝑠 𝑡𝑜 𝑎 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑙𝑖𝑛𝑘.
/clone -  𝐶𝑙𝑜𝑛𝑒 𝑎 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑙𝑖𝑛𝑘.
/list - 𝐶ℎ𝑒𝑐𝑘 𝑡ℎ𝑒 𝑓𝑖𝑙𝑒𝑠 𝑖𝑛 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑣𝑖𝑎 𝑡ℎ𝑒 𝑏𝑜𝑡.
/clean - 𝐷𝑒𝑙𝑒𝑡𝑒 𝑓𝑖𝑙𝑒𝑠 𝑖𝑛 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑏𝑦 𝑓𝑖𝑙𝑒 𝑛𝑎𝑚𝑒.
/leech - 𝑙𝑒𝑒𝑐ℎ 𝑡ℎ𝑒 𝑆𝑒𝑒𝑑𝑟 & 𝑊𝑜𝑟𝑘𝑒𝑟𝑠 𝐿𝑖𝑛𝑘𝑠 𝑡𝑜 𝐹𝑖𝑙𝑒 𝑜𝑟 𝐺𝑑𝑟𝑖𝑣𝑒 [𝐴𝑈𝑇𝐻_𝑈𝑆𝐸𝑅𝑆].
/extractaudios - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑎𝑢𝑑𝑖𝑜 𝑓𝑟𝑜𝑚 𝑓𝑖𝑙𝑒𝑠.
/extractsubtitles - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑠𝑢𝑏𝑡𝑖𝑡𝑙𝑒𝑠 𝑓𝑟𝑜𝑚 𝑓𝑖𝑙𝑒𝑠.
/extractvideo - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑣𝑖𝑑𝑒𝑜 𝑓𝑟𝑜𝑚 𝑓𝑖𝑙𝑒𝑠.
/rename - 𝑟𝑒𝑝𝑙𝑎𝑦 𝑤𝑖𝑡ℎ 𝑓𝑖𝑙𝑒 𝑡𝑜 𝑅𝑒𝑛𝑎𝑚𝑒📝
/gofile - 𝑇ℎ𝑒 𝐹𝑖𝑙𝑒𝑠 𝑈𝑝𝑙𝑜𝑎𝑑 𝑇𝑜 𝐺𝑜𝑓𝑖𝑙𝑒 𝐿𝑖𝑛𝑘 🔗
/changeindexaudio - 𝑅𝑒𝑜𝑟𝑑𝑒𝑟 𝑡ℎ𝑒 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒 [a-1  𝑓𝑜𝑟 𝑟𝑒𝑚𝑜𝑣𝑒 𝑎𝑢𝑑𝑖𝑜 , a-2-1-3-4  𝑓𝑜𝑟 𝑠𝑤𝑎𝑝 𝑎𝑢𝑑𝑖𝑜]
/changeindexsub - 𝑅𝑒𝑜𝑟𝑑𝑒𝑟 𝑡ℎ𝑒 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒 [s-1  𝑓𝑜𝑟 𝑟𝑒𝑚𝑜𝑣𝑒 𝑠𝑢𝑏𝑡𝑖𝑡𝑙𝑒 , s-2-1-3-4  𝑓𝑜𝑟 𝑠𝑤𝑎𝑝 𝑠𝑢𝑏𝑡𝑖𝑡𝑙𝑒]
/changemetadata - 𝑇𝑟𝑎𝑛𝑠𝑓𝑜𝑟𝑚 𝑡ℎ𝑒 𝑚𝑒𝑡𝑎𝑑𝑎𝑡𝑎
/removetags - 𝑇𝑜 𝑅𝑒𝑚𝑜𝑣𝑒 𝐴𝑙𝑙 𝑀𝑒𝑡𝑎𝑑𝑎𝑡𝑎 𝑇𝑎𝑔𝑠
/merge - 𝑆𝑒𝑛𝑑 𝑢𝑝 𝑡𝑜 10 𝑣𝑖𝑑𝑒𝑜/𝑑𝑜𝑐𝑢𝑚𝑒𝑛𝑡 𝑓𝑖𝑙𝑒𝑠 𝑜𝑛𝑒 𝑏𝑦 𝑜𝑛𝑒.
/videomerge - 𝑉𝑖𝑑𝑒𝑜𝑚𝑒𝑟𝑔𝑒 𝑤𝑖𝑡ℎ 𝑓𝑖𝑙𝑒𝑛𝑎𝑚𝑒.𝑚𝑘𝑣 𝑡𝑜 𝑠𝑡𝑎𝑟𝑡 𝑚𝑒𝑟𝑔𝑖𝑛𝑔
/multitask - 𝑚𝑢𝑙𝑡𝑖𝑡𝑎𝑠𝑘 𝑖𝑠 𝐶ℎ𝑎𝑛𝑔𝑒𝑚𝑒𝑡𝑑𝑎𝑡𝑎 + 𝑅𝑒𝑚𝑜𝑣𝑒 𝑇𝑎𝑔𝑠 + 𝑇ℎ𝑢𝑚𝑏𝑛𝑎𝑖𝑙
/samplevideo - 𝐶𝑟𝑒𝑎𝑡𝑒 𝐴 𝑆𝑎𝑚𝑝𝑙𝑒 𝑉𝑖𝑑𝑒𝑜 🎞️
/screenshots - 𝐶𝑎𝑝𝑡𝑢𝑟𝑒 𝑠𝑜𝑚𝑒 𝑚𝑒𝑚𝑜𝑟𝑎𝑏𝑙𝑒 𝑠ℎ𝑜𝑡𝑠 📸
/unzip - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑓𝑖𝑙𝑒𝑠 (𝑍𝐼𝑃 𝑓𝑜𝑟𝑚𝑎𝑡 𝑜𝑛𝑙𝑦)
/setphoto  -  𝑇𝑜 𝑎𝑑𝑑 𝑎 𝑝ℎ𝑜𝑡𝑜 𝑡𝑜 𝑎 𝑓𝑖𝑙𝑒  𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.𝑗𝑝𝑔 𝑓𝑜𝑟 𝑠𝑒𝑛𝑑𝑖𝑛𝑔 𝑡ℎ𝑒 𝑝ℎ𝑜𝑡𝑜 𝑎𝑠 𝑎𝑛 𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.
/attachphoto - 𝑇ℎ𝑖𝑠 𝑐𝑜𝑚𝑚𝑎𝑛𝑑 𝑖𝑠 𝑢𝑠𝑒𝑑 𝑡𝑜 𝑎𝑑𝑑 𝑎 𝑝ℎ𝑜𝑡𝑜 𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.𝑗𝑝𝑔 𝑡𝑜 𝑎 𝑓𝑖𝑙𝑒
/help - 𝐺𝑒𝑡 𝑑𝑒𝑡𝑎𝑖𝑙𝑒𝑑 𝑜𝑓 𝑏𝑜𝑡 𝑐𝑜𝑚𝑚𝑎𝑛𝑑𝑠 📝
/about - 𝐿𝑒𝑎𝑟𝑛 𝑚𝑜𝑟𝑒 𝑎𝑏𝑜𝑢𝑡 𝑡ℎ𝑖𝑠 𝑏𝑜𝑡 🧑🏻‍💻
/ping - 𝑇𝑜 𝐶ℎ𝑒𝑐𝑘 𝑇ℎ𝑒 𝑃𝑖𝑛𝑔 𝑂𝑓 𝑇ℎ𝑒 𝐵𝑜𝑡 📍

 💭• Tʜɪs Bᴏᴛ Is Fᴏʟʟᴏᴡs ᴛʜᴇ 𝟸GB Bᴇʟᴏᴡ Fɪʟᴇs Tᴏ Tᴇʟᴇɢʀᴀᴍ.\n• 𝟸GB Aʙᴏᴠᴇ Fɪʟᴇs Tᴏ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ.
 
🔱 𝐌𝐚𝐢𝐧𝐭𝐚𝐢𝐧𝐞𝐝 𝐁𝐲 : <a href='https://t.me/Sunrises_24'>𝐒𝐔𝐍𝐑𝐈𝐒𝐄𝐒™</a></b>
    
   """
    await msg.reply_text(help_text)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#FUNCTION CALLBACK HELP
@Client.on_callback_query(filters.regex("help"))
async def help(bot, msg):
    txt1 = "Sᴇɴᴅ ᴀ ғɪʟᴇ ᴀɴᴅ /rename <new name> ᴡɪᴛʜ ʀᴇᴘʟᴀʏᴇᴅ ʏᴏᴜʀ ғɪʟᴇ\n\n"
    txt1 += "Rᴇɴᴀᴍᴇ [#2GB] - Rᴇɴᴀᴍᴇ ғɪʟᴇꜱ\n\n"
    txt1 += "Mᴇᴛᴀᴅᴀᴛᴀ - Mᴏᴅɪғʏ ᴍᴇᴛᴀᴅᴀᴛᴀ\n\nFᴏʀᴍᴀᴛ: ᴄʜᴀɴɢᴇᴍᴇᴛᴀᴅᴀᴛᴀ ᴠɪᴅᴇᴏ_ᴛɪᴛʟᴇ | ᴀᴜᴅɪᴏ_ᴛɪᴛʟᴇ | ꜱᴜʙᴛɪᴛʟᴇ_ᴛɪᴛʟᴇ\n\n"
    txt1 += "Gᴏғɪʟᴇ - Tʜᴇ Fɪʟᴇs Uᴘʟᴏᴀᴅ Tᴏ Gᴏғɪʟᴇ Lɪɴᴋ 🔗\n\n"
    txt1 += "ɢᴏғɪʟᴇsᴇᴛᴜᴘ - Sᴇᴛᴜᴘ Tʜᴇ Gᴏғɪʟᴇ API KEY ғʀᴏᴍ Gᴏғɪʟᴇ.ɪᴏ ⚙️\n\n"
    txt1 += "ɢᴅʀɪᴠᴇɪᴅ - Tʜᴇ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ Fᴏʟᴅᴇʀ ID Sᴇᴛᴜᴘ 📁.\n\n"
    txt2 += "Mɪʀʀᴏʀ - Mɪʀʀᴏʀ ғɪʟᴇs ᴛᴏ ᴀ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ ʟɪɴᴋ.\n\n"
    txt2 += "Cʟᴏɴᴇ -  Cʟᴏɴᴇ ᴀ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ ʟɪɴᴋ.\n\n"
    txt2 += "Lɪsᴛ - Cʜᴇᴄᴋ ᴛʜᴇ ғɪʟᴇs ɪɴ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ ᴠɪᴀ ᴛʜᴇ ʙᴏᴛ.\n\n"
    txt2 += "Cʟᴇᴀɴ - Dᴇʟᴇᴛᴇ ғɪʟᴇs ɪɴ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ ʙʏ ғɪʟᴇ ɴᴀᴍᴇ.\n\n"
    txt2 += "ʟᴇᴇᴄʜ - ʟᴇᴇᴄʜ ᴛʜᴇ Sᴇᴇᴅʀ & Wᴏʀᴋᴇʀs' Lɪɴᴋs ᴛᴏ Fɪʟᴇ ᴏʀ Gᴅʀɪᴠᴇ.\n\n"
    txt2 += "Exᴛʀᴀᴄᴛ Aᴜᴅɪᴏs - Exᴛʀᴀᴄᴛ ᴀᴜᴅɪᴏ ғʀᴏᴍ ғɪʟᴇs.\n\n"
    txt2 += "Exᴛʀᴀᴄᴛ Sᴜʙᴛɪᴛʟᴇs - Exᴛʀᴀᴄᴛ sᴜʙᴛɪᴛʟᴇs ғʀᴏᴍ ғɪʟᴇs.\n\n"
    txt2 += "Exᴛʀᴀᴄᴛ Vɪᴅᴇᴏs - Exᴛʀᴀᴄᴛ ᴠɪᴅᴇᴏ ғʀᴏᴍ ғɪʟᴇs.\n\n"
    txt3 += "Cʜᴀɴɢᴇɪɴᴅᴇxᴀᴜᴅɪᴏ - Rᴇᴀʀʀᴀɴɢᴇ ᴛʜᴇ ɪɴᴅᴇx\n\nFᴏʀᴍᴀᴛ:1)a-𝟷 ғᴏʀ ʀᴇᴍᴏᴠᴇ ᴀᴜᴅɪᴏ\n2)a-𝟸-𝟷-𝟹-𝟺 ғᴏʀ ꜱᴡᴀᴘ ᴀᴜᴅɪᴏ\n\n"
    txt3 += "Cʜᴀɴɢᴇɪɴᴅᴇxsᴜʙ - Rᴇᴏʀᴅᴇʀ ᴛʜᴇ sᴇǫᴜᴇɴᴄᴇ [s-𝟷  ғᴏʀ ʀᴇᴍᴏᴠᴇ sᴜʙᴛɪᴛʟᴇ, s-𝟸-𝟷-𝟹-𝟺 ғᴏʀ sᴡᴀᴘ sᴜʙᴛɪᴛʟᴇ]\n\n"
    txt3 += "Gᴇɴᴇʀᴀᴛᴇ Sᴀᴍᴘʟᴇ Vɪᴅᴇᴏ - Cʀᴇᴀᴛᴇ ꜱᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏꜱ (𝟹𝟶ꜱ, 𝟼𝟶ꜱ, 𝟿𝟶ꜱ, 𝟷𝟸𝟶ꜱ, 𝟷𝟻𝟶ꜱ)\n\n"
    txt3 += "Sᴄʀᴇᴇɴꜱʜᴏᴛꜱ - Tᴀᴋᴇ ꜱᴄʀᴇᴇɴꜱʜᴏᴛꜱ (ᴇxᴀᴍᴘʟᴇ: /ꜱᴄʀᴇᴇɴꜱʜᴏᴛꜱ 𝟷𝟶)\n\n"
    txt3 += "Uɴᴢɪᴘ ᴛʜᴇ Fɪʟᴇꜱ ᴏɴʟʏ ᴢɪᴘ Fᴏʀᴍᴀᴛ ᴏɴʟʏ - Exᴛʀᴀᴄᴛ ZIP ғɪʟᴇꜱ ᴏɴʟʏ\n\n"
    txt3 += "Aᴛᴛᴀᴄʜ Pʜᴏᴛᴏ ɪꜱ ᴜꜱᴇᴅ ᴀᴛᴛᴀᴄʜᴍᴇɴᴛ.ɪᴘɢ ᴛᴏ ᴀ ғɪʟᴇ\n\n"
    txt3 += "ꜱᴇᴛᴘʜᴏᴛᴏ -  Tᴏ ᴀᴅᴅ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ ᴀ ғɪʟᴇ  ᴀᴛᴛᴀᴄʜᴍᴇɴᴛ.ɪᴘɢ ғᴏʀ ꜱᴇɴᴅɪɴɢ ᴛʜᴇ ᴘʜᴏᴛᴏ ᴀꜱ ᴀɴ ᴀᴛᴛᴀᴄʜᴍᴇɴᴛ.\n\n"
    txt4 += "ᴍᴇʀɢᴇ  - Sᴇɴᴅ ᴜᴘ ᴛᴏ 𝟷𝟶 ᴠɪᴅᴇᴏ/ᴅᴏᴄᴜᴍᴇɴᴛ ғɪʟᴇs ᴏɴᴇ ʙʏ ᴏɴᴇ.\n\n"
    txt4 += "ᴠɪᴅᴇᴏᴍᴇʀɢᴇ - Vɪᴅᴇᴏᴍᴇʀɢᴇ ᴡɪᴛʜ ғɪʟᴇɴᴀᴍᴇ.ᴍᴋᴠ ᴛᴏ sᴛᴀʀᴛ ᴍᴇʀɢɪɴɢ\n\n"   
    txt4 += "RᴇᴍᴏᴠᴇTᴀɢs - Tᴏ Rᴇᴍᴏᴠᴇ Aʟʟ Mᴇᴛᴀᴅᴀᴛᴀ Tᴀɢs\n\n"
    txt4 += "ꜱᴇɴᴅ ᴘʜᴏᴛᴏ ᴛᴏ ꜱᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄ🌟\n\n"
    txt4 += "/view ᴛᴏ ꜱᴇᴇ ʏᴏᴜʀ ᴛʜᴜᴍʙɴᴀɪʟ 👀\n\n"
    txt4 += "/del ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴛʜᴜᴍʙɴᴀɪʟ❌\n\n"
    txt4 += "Jᴏɪɴ : @Sunrises24BotUpdates"
    button= [[        
        InlineKeyboardButton("Cʟᴏꜱᴇ ❌", callback_data="del")   
    ]] 
    await msg.message.edit(text=txt, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview = True)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#FUNCTION CALL BACK ABOUT
@Client.on_callback_query(filters.regex("about"))
async def about(bot, msg):
    me=await bot.get_me()
    Dᴇᴠᴇʟᴏᴘᴇʀ ="<a href=https://t.me/Sunrises_24>SUNRISES™🧑🏻‍💻</a>"     
    txt="<b>Uᴘᴅᴀᴛᴇs 📢: <a href=https://t.me/Sunrises24botupdates>SUNRISES™</a></b>"
    txt="<b>Sᴜᴘᴘᴏʀᴛ ✨: <a href=https://t.me/Sunrises24botSupport>SUNRISES⚡™</a></b>"
    txt="<b>✯ Bᴜɪʟᴅ Sᴛᴀᴛᴜs 📊 : ᴠ2.4 [Sᴛᴀʙʟᴇ]</b>" 
    button= [[        
        InlineKeyboardButton("Cʟᴏꜱᴇ ❌", callback_data="del")       
    ]]  
    await msg.message.edit(text=txt, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview = True, parse_mode=enums.ParseMode.HTML)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_callback_query(filters.regex("del"))
async def closed(bot, msg):
    try:
        await msg.message.delete()
    except:
        return

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#Ping
@Client.on_message(filters.command("ping"))
async def ping(bot, msg):
    start_t = time.time()
    rm = await msg.reply_text("Checking")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Pong!📍\n{time_taken_s:.3f} ms")
 
