#TG : @Sunrises_24
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import subprocess
import os, json
import time
import shutil
import zipfile
import tarfile
import ffmpeg
from pyrogram.types import Message
from pyrogram.types import Document, Video
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import MessageNotModified
from main.utils import progress_message, humanbytes
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,CallbackQuery
from config import AUTH_USERS, ADMIN, CAPTION
from main.utils import heroku_restart, upload_files, download_media, download_file_from_drive
import aiohttp
from pyrogram.errors import RPCError, FloodWait
import asyncio
from main.ffmpeg import remove_all_tags, change_video_metadata, generate_sample_video, add_photo_attachment, merge_videos, unzip_file, extract_audio_stream, extract_subtitle_stream, extract_video_stream, extract_audios_from_file, extract_subtitles_from_file, extract_video_from_file, get_mediainfo, compress_video, get_and_upload_mediainfo
from googleapiclient.http import MediaFileUpload
from main.gdrive import upload_to_google_drive, extract_id_from_url, copy_file, get_files_in_folder, drive_service
from googleapiclient.errors import HttpError
from Database.database import db
import datetime
from datetime import timedelta
import psutil
from pymongo.errors import PyMongoError
from yt_dlp import YoutubeDL
from html_telegraph_poster import TelegraphPoster
from os import execl as osexecl
from sys import executable
from config import *
import logging
import tempfile
import math

logging.basicConfig(
    filename='SunrisesBot.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Example of logging a message
logging.info('Bot started successfully!')

# Initialize Telegraph
telegraph = TelegraphPoster(use_api=True)
telegraph.create_api_token("MediaInfoBot")


# Global variables
START_TIME = datetime.datetime.now()

merge_state = {}

FILE_SIZE_LIMIT = 2000 * 1024 * 1024  # 2000 MB in bytes
# ---------------- CONFIG / CONSTANTS ----------------
URL_RE = re.compile(r"(https?://[^\s'\"]+)")
logger = logging.getLogger(__name__)

# Initialize global settings variables
METADATA_ENABLED = True 
PHOTO_ATTACH_ENABLED = True
MIRROR_ENABLED = True
RENAME_ENABLED = True
REMOVETAGS_ENABLED = True
STREAMREMOVE_ENABLED = True 
MERGE_ENABLED = True
EXTRACT_ENABLED = True
SWAP_INDEX_ENABLED = True
MULTITASK_ENABLED = True
COMPRESS_ENABLED = True

#varibles for streameremove
selected_streams = set()
downloaded = None
output_filename = None



#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Command handler to start the interaction (only in admin)
@Client.on_message(filters.command("bsettings") & filters.chat(ADMIN))
async def bot_settings_command(_, msg):
    await display_bot_settings_inline(msg)


# Inline function to display user settings with inline buttons
async def display_bot_settings_inline(msg):
    global METADATA_ENABLED, PHOTO_ATTACH_ENABLED, MIRROR_ENABLED, RENAME_ENABLED, REMOVETAGS_ENABLED, SWAP_INDEX_ENABLED, MULTITASK_ENABLED, STREAMREMOVE_ENABLED, COMPRESS_ENABLED

    metadata_status = "✅ Enabled" if METADATA_ENABLED else "❌ Disabled"
    photo_attach_status = "✅ Enabled" if PHOTO_ATTACH_ENABLED else "❌ Disabled"
    mirror_status = "✅ Enabled" if MIRROR_ENABLED else "❌ Disabled"
    rename_status = "✅ Enabled" if RENAME_ENABLED else "❌ Disabled"
    removealltags_status = "✅ Enabled" if REMOVETAGS_ENABLED else "❌ Disabled"
    swap_index_status = "✅ Enabled" if SWAP_INDEX_ENABLED else "❌ Disabled"
    merge_video_status = "✅ Enabled" if MERGE_ENABLED else "❌ Disabled"  
    multitask_status = "✅ Enabled" if MULTITASK_ENABLED else "❌ Disabled"
    streamremove_status = "✅ Enabled" if STREAMREMOVE_ENABLED else "❌ Disabled"    
    compress_status = "✅ Enabled" if COMPRESS_ENABLED else "❌ Disabled"    
            
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],            
            [InlineKeyboardButton(f"{rename_status} Change Rename 📝", callback_data="toggle_rename")],
            [InlineKeyboardButton(f"{removealltags_status} Remove All Tags 📛", callback_data="toggle_removealltags")],
            [InlineKeyboardButton(f"{metadata_status} Change Metadata ☄️", callback_data="toggle_metadata")],            
            [InlineKeyboardButton(f"{swap_index_status} Swap Index ♻️", callback_data="toggle_swap_index")],
            [InlineKeyboardButton(f"{merge_video_status} Merge Video 🎞️", callback_data="toggle_merge_video")],
            [InlineKeyboardButton(f"{photo_attach_status} Attach Photo 🖼️", callback_data="toggle_photo_attach")],                        
            [InlineKeyboardButton(f"{mirror_status} Mirror 💽", callback_data="toggle_mirror")], 
            [InlineKeyboardButton(f"{multitask_status} MultiTask ⏩", callback_data="toggle_multitask")],
            [InlineKeyboardButton(f"{streamremove_status} Stream Remove 🔊", callback_data="toggle_streamremove")],
            [InlineKeyboardButton(f"{compress_status} Compress 🗜️", callback_data="toggle_compress")],
            [InlineKeyboardButton("Close ❌", callback_data="del")],
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")]
        ]
    )

    await msg.reply_text("Use inline buttons to manage your settings:", reply_markup=keyboard)


#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_callback_query(filters.regex("del"))
async def closed(bot, msg):
    try:
        await msg.message.delete()
    except:
        return

# Callback query handlers

@Client.on_callback_query(filters.regex("^toggle_rename$"))
async def toggle_rename_callback(_, callback_query):
    global RENAME_ENABLED

    RENAME_ENABLED = not RENAME_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_removealltags$"))
async def toggle_removealltags_callback(_, callback_query):
    global REMOVETAGS_ENABLED

    REMOVETAGS_ENABLED = not REMOVETAGS_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_metadata$"))
async def toggle_metadata_callback(_, callback_query):
    global METADATA_ENABLED

    METADATA_ENABLED = not METADATA_ENABLED
    await update_settings_message(callback_query.message)


@Client.on_callback_query(filters.regex("^toggle_photo_attach$"))
async def toggle_photo_attach_callback(_, callback_query):
    global PHOTO_ATTACH_ENABLED

    PHOTO_ATTACH_ENABLED = not PHOTO_ATTACH_ENABLED
    await update_settings_message(callback_query.message)


@Client.on_callback_query(filters.regex("^toggle_mirror$"))
async def toggle_multitask_callback(_, callback_query):
    global MIRROR_ENABLED

    MIRROR_ENABLED = not MIRROR_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_swap_index$"))
async def toggle_swap_index_callback(_, callback_query):
    global SWAP_INDEX_ENABLED

    SWAP_INDEX_ENABLED = not SWAP_INDEX_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_merge_video$"))
async def toggle_merge_video_callback(_, callback_query):
    global MERGE_ENABLED

    MERGE_ENABLED = not MERGE_ENABLED
    await update_settings_message(callback_query.message)
    
@Client.on_callback_query(filters.regex("^toggle_multitask$"))
async def toggle_multitask_callback(_, callback_query):
    global MULTITASK_ENABLED

    MULTITASK_ENABLED = not MULTITASK_ENABLED
    await update_settings_message(callback_query.message)
    
@Client.on_callback_query(filters.regex("^toggle_streamremove$"))
async def toggle_streamremove_callback(_, callback_query):
    global STREAMREMOVE_ENABLED

    STREAMREMOVE_ENABLED = not STREAMREMOVE_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_compress$"))
async def toggle_compress_callback(_, callback_query):
    global COMPRESS_ENABLED

    COMPRESS_ENABLED = not COMPRESS_ENABLED
    await update_settings_message(callback_query.message)
    
# Callback query handler for the "sunrises24_bot_updates" button
@Client.on_callback_query(filters.regex("^sunrises24_bot_updates$"))
async def sunrises24_bot_updates_callback(_, callback_query):
    await callback_query.answer("MADE BY @SUNRISES24BOTUPDATES ❤️", show_alert=True)    

async def update_settings_message(message):
    global METADATA_ENABLED, PHOTO_ATTACH_ENABLED, MIRROR_ENABLED, RENAME_ENABLED, REMOVETAGS_ENABLED, SWAP_INDEX_ENABLED, MULTITASK_ENABLED, STREAMREMOVE_ENABLED, COMPRESS_ENABLED

    metadata_status = "✅ Enabled" if METADATA_ENABLED else "❌ Disabled"
    photo_attach_status = "✅ Enabled" if PHOTO_ATTACH_ENABLED else "❌ Disabled"
    mirror_status = "✅ Enabled" if MIRROR_ENABLED else "❌ Disabled"
    rename_status = "✅ Enabled" if RENAME_ENABLED else "❌ Disabled"
    removealltags_status = "✅ Enabled" if REMOVETAGS_ENABLED else "❌ Disabled"
    swap_index_status = "✅ Enabled" if SWAP_INDEX_ENABLED else "❌ Disabled"
    merge_video_status = "✅ Enabled" if MERGE_ENABLED else "❌ Disabled"   
    multitask_status = "✅ Enabled" if MULTITASK_ENABLED else "❌ Disabled"    
    streamremove_status = "✅ Enabled" if STREAMREMOVE_ENABLED else "❌ Disabled"    
    compress_status = "✅ Enabled" if COMPRESS_ENABLED else "❌ Disabled"    
    
      
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],            
            [InlineKeyboardButton(f"{rename_status} Change Rename 📝", callback_data="toggle_rename")],
            [InlineKeyboardButton(f"{removealltags_status} Remove All Tags 📛", callback_data="toggle_removealltags")],
            [InlineKeyboardButton(f"{metadata_status} Change Metadata ☄️", callback_data="toggle_metadata")],            
            [InlineKeyboardButton(f"{swap_index_status} Swap Index ♻️", callback_data="toggle_swap_index")],
            [InlineKeyboardButton(f"{merge_video_status} Merge Video 🎞️", callback_data="toggle_merge_video")],
            [InlineKeyboardButton(f"{photo_attach_status} Attach Photo 🖼️", callback_data="toggle_photo_attach")],                        
            [InlineKeyboardButton(f"{mirror_status} Mirror 💽", callback_data="toggle_mirror")],
            [InlineKeyboardButton(f"{multitask_status} MultiTask ⏩", callback_data="toggle_multitask")],
            [InlineKeyboardButton(f"{streamremove_status} Stream Remove 🔊", callback_data="toggle_streamremove")],
            [InlineKeyboardButton(f"{compress_status} Compress 🗜️", callback_data="toggle_compress")],
            [InlineKeyboardButton("Close ❌", callback_data="del")],
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")]
        ]
    )

    await message.edit_text("Use inline buttons to manage your settings:", reply_markup=keyboard)
    
    
    

@Client.on_callback_query(filters.regex("^set_sample_video_duration_"))
async def set_sample_video_duration(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    duration_str = callback_query.data.split("_")[-1]
    duration = int(duration_str)
    
    # Save sample video duration to database
    await db.save_sample_video_settings(user_id, duration, "screenshots setting")  # Adjusted the parameter from 'duration' to 'duration_str'
    
    await callback_query.answer(f"Sample video duration set to {duration} seconds.")
    await display_user_settings(client, callback_query.message, edit=True)


@Client.on_callback_query(filters.regex("^sample_video_option$"))
async def sample_video_option(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_duration = await db.get_sample_video_settings(user_id)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Sample Video 150s {'✅' if current_duration == 150 else ''}", callback_data="set_sample_video_duration_150")],
        [InlineKeyboardButton(f"Sample Video 120s {'✅' if current_duration == 120 else ''}", callback_data="set_sample_video_duration_120")],
        [InlineKeyboardButton(f"Sample Video 90s {'✅' if current_duration == 90 else ''}", callback_data="set_sample_video_duration_90")],
        [InlineKeyboardButton(f"Sample Video 60s {'✅' if current_duration == 60 else ''}", callback_data="set_sample_video_duration_60")],
        [InlineKeyboardButton(f"Sample Video 30s {'✅' if current_duration == 30 else ''}", callback_data="set_sample_video_duration_30")],
        [InlineKeyboardButton("Back", callback_data="back_to_settings")]
    ])
    
    await callback_query.message.edit_text(f"Sample Video Duration Settings\nCurrent duration: {current_duration}", reply_markup=keyboard)
  

# Callback query handler for returning to user settings
@Client.on_callback_query(filters.regex("^back_to_settings$"))
async def back_to_settings(client, callback_query: CallbackQuery):
    await display_user_settings(client, callback_query.message, edit=True)

@Client.on_message(filters.private & filters.command("usersettings"))
async def display_user_settings(client, msg, edit=False):
    user_id = msg.from_user.id
    
    current_duration = await db.get_sample_video_duration(user_id)
    current_screenshots = await db.get_screenshots_count(user_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],
        [InlineKeyboardButton("Sample Video Settings 🎞️", callback_data="sample_video_option")],
        [InlineKeyboardButton("Screenshots Settings 📸", callback_data="screenshots_option")],
        [InlineKeyboardButton("Thumbnail Settings 📄", callback_data="thumbnail_settings")],
        [InlineKeyboardButton("View Metadata ✨", callback_data="preview_metadata")],
        [InlineKeyboardButton("Attach Photo 📎", callback_data="attach_photo"), 
         InlineKeyboardButton("View Photo ✨", callback_data="preview_photo")],
        [InlineKeyboardButton("View Gofile API Key 🔗", callback_data="preview_gofilekey")],
        [InlineKeyboardButton("View Google Drive Folder ID 📂", callback_data="preview_gdrive")],
        [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],
        [InlineKeyboardButton("Close ❌", callback_data="del")]
    ])
    
    if edit:
        await msg.edit_text(f"User Settings\nCurrent sample video duration: {current_duration}\nCurrent screenshots setting: {current_screenshots}", reply_markup=keyboard)
    else:
        await msg.reply(f"User Settings\nCurrent sample video duration: {current_duration}\nCurrent screenshots setting: {current_screenshots}", reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^screenshots_option$"))
async def screenshots_option(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_screenshots = await db.get_screenshots_count(user_id)  # Default to 5 if not set
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Screenshots 1 {'✅' if current_screenshots == 1 else ''}", callback_data="set_screenshots_1")],
        [InlineKeyboardButton(f"Screenshots 2 {'✅' if current_screenshots == 2 else ''}", callback_data="set_screenshots_2")],
        [InlineKeyboardButton(f"Screenshots 3 {'✅' if current_screenshots == 3 else ''}", callback_data="set_screenshots_3")],
        [InlineKeyboardButton(f"Screenshots 4 {'✅' if current_screenshots == 4 else ''}", callback_data="set_screenshots_4")],
        [InlineKeyboardButton(f"Screenshots 5 {'✅' if current_screenshots == 5 else ''}", callback_data="set_screenshots_5")],
        [InlineKeyboardButton(f"Screenshots 6 {'✅' if current_screenshots == 6 else ''}", callback_data="set_screenshots_6")],
        [InlineKeyboardButton(f"Screenshots 7 {'✅' if current_screenshots == 7 else ''}", callback_data="set_screenshots_7")],
        [InlineKeyboardButton(f"Screenshots 8 {'✅' if current_screenshots == 8 else ''}", callback_data="set_screenshots_8")],
        [InlineKeyboardButton(f"Screenshots 9 {'✅' if current_screenshots == 9 else ''}", callback_data="set_screenshots_9")],
        [InlineKeyboardButton(f"Screenshots 10 {'✅' if current_screenshots == 10 else ''}", callback_data="set_screenshots_10")],
        [InlineKeyboardButton("Back", callback_data="back_to_settings")]
    ])
    
    await callback_query.message.edit_text(f"Screenshots Settings\nCurrent number: {current_screenshots}", reply_markup=keyboard)
    
@Client.on_callback_query(filters.regex("^set_screenshots_"))
async def set_screenshots(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    num_str = callback_query.data.split("_")[-1]
    num_screenshots = int(num_str)
    
    # Save screenshots count to database
    await db.save_screenshots_count(user_id, num_screenshots)
    
    await callback_query.answer(f"Number of screenshots set to {num_screenshots}.")
    await display_user_settings(client, callback_query.message, edit=True)



@Client.on_callback_query(filters.regex("^attach_photo$"))
async def inline_attach_photo_callback(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Update user settings to indicate attachment request
    await db.update_user_settings(user_id, {"attach_photo": True})
    
    await callback_query.message.edit_text("Please send a photo to be attached using the setphoto command.")

@Client.on_message(filters.private & filters.command("setphoto"))
async def set_photo(bot, msg):
    reply = msg.reply_to_message
    if not reply or not reply.photo:
        return await msg.reply_text("Please reply to a photo with the setphoto command")

    # Extract custom name from the command
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a custom name for the photo.")
    
    custom_name = msg.command[1]  # The custom name is the second part of the command
    user_id = msg.from_user.id
    photo_file_id = reply.photo.file_id

    try:
        # Download the photo file
        photo_path = await bot.download_media(photo_file_id)
        
        # Save the photo with the custom name
        custom_photo_path = f"{custom_name}.jpg"
        os.rename(photo_path, custom_photo_path)

        # Save the custom photo path to the database
        await db.save_attach_photo(user_id, custom_photo_path)
        await msg.reply_text(f"Photo saved successfully with the name: {custom_name}.jpg")

    except Exception as e:
        await msg.reply_text(f"Error saving photo: {e}")
@Client.on_callback_query(filters.regex("^preview_photo$"))
async def inline_preview_photo_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Retrieve the attachment path from the database
    attachment_file_id = await db.get_attach_photo(user_id)
    
    if not attachment_file_id:
        await callback_query.message.reply_text("No photo has been attached yet.")
        return
    
    try:
        await callback_query.message.reply_photo(photo=attachment_file_id, caption="Attached Photo")
    except Exception as e:
        await callback_query.message.reply_text(f"Failed to send photo: {str(e)}")

@Client.on_callback_query(filters.regex("^thumbnail_settings$"))
async def inline_thumbnail_settings(client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[            
            [InlineKeyboardButton("View Thumbnail", callback_data="view_thumbnail")],
            [InlineKeyboardButton("Delete Thumbnail", callback_data="delete_thumbnail")],
            [InlineKeyboardButton("Back to Settings", callback_data="back_to_settings")]
        ]
    )
    await callback_query.message.edit_text("Thumbnail Settings:", reply_markup=keyboard)

@Client.on_message(filters.private & filters.command("setthumbnail"))
async def set_thumbnail_command(client, message):
    user_id = message.from_user.id

    # Check if thumbnail already exists
    thumbnail_file_id = await db.get_thumbnail(user_id)
    if thumbnail_file_id:
        await message.reply("You already have a permanent thumbnail set. Send a new photo to update it.")
    else:
        await message.reply("Send a photo to set as your permanent thumbnail.")

@Client.on_message(filters.photo & filters.private)
async def set_thumbnail_handler(client, message):
    user_id = message.from_user.id
    photo_file_id = message.photo.file_id

    # Save thumbnail file ID to database
    await db.save_thumbnail(user_id, photo_file_id)
    
    await message.reply("Your permanent thumbnail is updated. If the bot is restarted, the new thumbnail will be preserved.")
    
@Client.on_callback_query(filters.regex("^view_thumbnail$"))
async def view_thumbnail(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    thumbnail_file_id = await db.get_thumbnail(user_id)

    if not thumbnail_file_id:
        await callback_query.message.reply_text("You don't have any thumbnail.")
        return

    try:
        await callback_query.message.reply_photo(photo=thumbnail_file_id, caption="This is your current thumbnail")
    except Exception as e:
        await callback_query.message.reply_text("An error occurred while trying to view your thumbnail.")

@Client.on_callback_query(filters.regex("^delete_thumbnail$"))
async def delete_thumbnail(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    thumbnail_file_id = await db.get_thumbnail(user_id)

    try:
        if thumbnail_file_id:
            await db.delete_thumbnail(user_id)
            await callback_query.message.reply_text("Your thumbnail was removed ❌")
        else:
            await callback_query.message.reply_text("You don't have any thumbnail ‼️")
    except Exception as e:
        await callback_query.message.reply_text("An error occurred while trying to remove your thumbnail. Please try again later.")



@Client.on_callback_query(filters.regex("^preview_gdrive$"))
async def inline_preview_gdrive(bot, callback_query):
    user_id = callback_query.from_user.id
    
    # Retrieve Google Drive folder ID from the database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)
    
    if not gdrive_folder_id:
        return await callback_query.message.reply_text(f"Google Drive Folder ID is not set for user `{user_id}`. Use /gdriveid {{your_gdrive_folder_id}} to set it.")
    
    await callback_query.message.reply_text(f"Current Google Drive Folder ID for user `{user_id}`: {gdrive_folder_id}")


@Client.on_message(filters.private & filters.command("setmetadata"))
async def set_metadata_command(client, msg):
    # Extract titles from the command message
    if len(msg.command) < 2:
        await msg.reply_text("Invalid command format. Use: setmetadata video_title | audio_title | subtitle_title")
        return
    
    titles = msg.text.split(" ", 1)[1].split(" | ")
    if len(titles) != 3:
        await msg.reply_text("Invalid number of titles. Use: setmetadata video_title | audio_title | subtitle_title")
        return
    
    # Store the titles in the database
    user_id = msg.from_user.id
    await db.save_metadata_titles(user_id, titles[0].strip(), titles[1].strip(), titles[2].strip())
    
    await msg.reply_text("Metadata titles set successfully ✅.")

@Client.on_message(filters.command("gofilesetup") & filters.private)
async def set_gofile_api_key(bot, msg):
    user_id = msg.from_user.id
    args = msg.text.split(" ", 1)
    if len(args) != 2:
        return await msg.reply_text("Usage: /gofilesetup {your_api_key}")
    
    api_key = args[1].strip()
    
    # Save Gofile API key to the database
    await db.save_gofile_api_key(user_id, api_key)
    
    await msg.reply_text("Your Gofile API key has been set successfully.✅")

@Client.on_message(filters.private & filters.command("gdriveid"))
async def setup_gdrive_id(bot, msg: Message):
    user_id = msg.from_user.id
    args = msg.text.split(" ", 1)
    if len(args) != 2:
        return await msg.reply_text("Usage: /gdriveid {your_gdrive_folder_id}")
    
    gdrive_folder_id = args[1].strip()
    
    # Save Google Drive folder ID to the database
    await db.save_gdrive_folder_id(user_id, gdrive_folder_id)
    
    await msg.reply_text(f"Google Drive folder ID set to: {gdrive_folder_id} for user `{user_id}`\n\nGoogle Drive folder ID set successfully✅!")

@Client.on_callback_query(filters.regex("^preview_metadata$"))
async def inline_preview_metadata_callback(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Fetch metadata titles from the database
    titles = await db.get_metadata_titles(user_id)
    
    if not titles or not any(titles.values()):
        await callback_query.message.reply_text("Metadata titles are not fully set. Please set all titles first.")
        return
    
    preview_text = f"Video Title: {titles.get('video_title', '')}\n" \
                   f"Audio Title: {titles.get('audio_title', '')}\n" \
                   f"Subtitle Title: {titles.get('subtitle_title', '')}"
    
    await callback_query.message.reply_text(f"Current Metadata Titles:\n\n{preview_text}")

@Client.on_callback_query(filters.regex("^preview_gofilekey$"))
async def inline_preview_gofile_api_key(bot, callback_query):
    user_id = callback_query.from_user.id
    
    # Fetch Gofile API key from the database
    api_key = await db.get_gofile_api_key(user_id)
    
    if not api_key:
        return await callback_query.message.reply_text(f"Gofile API key is not set for user `{user_id}`. Use /gofilesetup {{your_api_key}} to set it.")
    
    await callback_query.message.reply_text(f"Current Gofile API Key for user `{user_id}`: {api_key}")


# Command handler for /mirror
@Client.on_message(filters.private & filters.command("mirror"))
async def mirror_to_google_drive(bot, msg: Message):
    global MIRROR_ENABLED
        
    if not MIRROR_ENABLED:
        return await msg.reply_text("The mirror feature is currently disabled.")

    user_id = msg.from_user.id
    
    # Retrieve the user's Google Drive folder ID
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)
    
    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    reply = msg.reply_to_message
    if len(msg.command) < 2 or not reply:
        return await msg.reply_text("Please reply to a file with the new filename and extension.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a file with the new filename and extension.")

    new_name = msg.text.split(" ", 1)[1]

    try:
        # Show progress message for downloading
        sts = await msg.reply_text("🚀 Downloading...")
        
        # Download the file
        downloaded_file = await bot.download_media(message=reply, file_name=new_name, progress=progress_message, progress_args=("Downloading", sts, time.time()))
        filesize = os.path.getsize(downloaded_file)
        
        # Once downloaded, update the message to indicate uploading
        await sts.edit("💠 Uploading...")
        
        start_time = time.time()

        # Upload file to Google Drive
        file_metadata = {'name': new_name, 'parents': [gdrive_folder_id]}
        media = MediaFileUpload(downloaded_file, resumable=True)

        # Upload with progress monitoring
        request = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink')
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                current_progress = status.progress() * 100
                await progress_message(current_progress, 100, "Uploading to Google Drive", sts, start_time)

        file_id = response.get('id')
        file_link = response.get('webViewLink')

        # Prepare caption for the uploaded file
        if CAPTION:
            caption_text = CAPTION.format(file_name=new_name, file_size=humanbytes(filesize))
        else:
            caption_text = f"Uploaded File: {new_name}\nSize: {humanbytes(filesize)}"

        # Send the Google Drive link to the user
        button = [
            [InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]
        ]
        await msg.reply_text(
            f"File successfully mirrored and uploaded to Google Drive!\n\n"
            f"Google Drive Link: [View File]({file_link})\n\n"
            f"Uploaded File: {new_name}\n"
            f"Size: {humanbytes(filesize)}",
            reply_markup=InlineKeyboardMarkup(button)
        )
        os.remove(downloaded_file)
        await sts.delete()

    except Exception as e:
        await sts.edit(f"Error: {e}")
        

#Rename Command
@Client.on_message(filters.private & filters.command("rename"))
async def rename_file(bot, msg):
    global RENAME_ENABLED

    if not RENAME_ENABLED:
        return await msg.reply_text("Rename feature is currently disabled.")
        
    user_id = msg.from_user.id
    
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]
    sts = await msg.reply_text("🚀 Downloading... ⚡")
    c_time = time.time()
    downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    filesize = humanbytes(media.file_size)

    if CAPTION:
        try:
            cap = CAPTION.format(file_name=new_name, file_size=filesize)
        except KeyError as e:
            return await sts.edit(text=f"Caption error: unexpected keyword ({e})")
    else:
        cap = f"{new_name}\n\n🌟 Size: {filesize}"

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    og_thumbnail = None
    if thumbnail_file_id:
        try:
            og_thumbnail = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
            except Exception:
                pass

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()

    if os.path.getsize(downloaded) > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(downloaded, new_name, sts)
        await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
    else:
        try:
            await bot.send_document(msg.chat.id, document=downloaded, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
        except Exception as e:
            return await sts.edit(f"Error: {e}")

    os.remove(downloaded)
    await sts.delete()

#Change Metadata Code
@Client.on_message(filters.private & filters.command("changemetadata"))
async def change_metadata(bot, msg: Message):
    global METADATA_ENABLED

    if not METADATA_ENABLED:
        return await msg.reply_text("Metadata changing feature is currently disabled.")

    user_id = msg.from_user.id
   
    # Fetch metadata titles from the database
    metadata_titles = await db.get_metadata_titles(user_id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    if not any([video_title, audio_title, subtitle_title]):
        return await msg.reply_text("Metadata titles are not set. Please set metadata titles using `/setmetadata video_title audio_title subtitle_title`.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the metadata command\nFormat: `changemetadata -n filename.mkv`")

    if len(msg.command) < 3 or msg.command[1] != "-n":
        return await msg.reply_text("Please provide the filename with the `-n` flag\nFormat: `changemetadata -n filename.mkv`")

    output_filename = " ".join(msg.command[2:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the metadata command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    output_file = output_filename

    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error changing metadata: {e}")
        os.remove(downloaded)
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(user_id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception as e:
                file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed metadata and uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(msg.chat.id, document=output_file, thumb=file_thumb, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
        except Exception as e:
            return await safe_edit_message(sts, f"Error: {e}")

    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()

   

#attach photo
@Client.on_message(filters.private & filters.command("attachphoto"))
async def attach_photo(bot, msg: Message):
    global PHOTO_ATTACH_ENABLED

    if not PHOTO_ATTACH_ENABLED:
        return await msg.reply_text("Photo attachment feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the attach photo command and specify the output filename\nFormat: `attachphoto -n filename.mkv`")

    command_text = " ".join(msg.command[1:]).strip()
    if "-n" not in command_text:
        return await msg.reply_text("Please provide the output filename using the `-n` flag\nFormat: `attachphoto -n filename.mkv`")

    filename_part = command_text.split('-n', 1)[1].strip()
    output_filename = filename_part if filename_part else None

    if not output_filename:
        return await msg.reply_text("Please provide a valid filename\nFormat: `attachphoto -n filename.mkv`")

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the attach photo command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    # Retrieve attachment from the database
    attachment_file_path = await db.get_attach_photo(msg.from_user.id)
    if not attachment_file_path:
        await safe_edit_message(sts, "Please send a photo to be attached using the `setphoto` command.")
        os.remove(downloaded)
        return

    # Ensure the attachment exists and download it if necessary
    attachment_path = attachment_file_path
    if not os.path.exists(attachment_path):
        await safe_edit_message(sts, "Attachment not found.")
        os.remove(downloaded)
        return

    output_file = output_filename

    await safe_edit_message(sts, "💠 Adding photo attachment... ⚡")
    try:
        # Function to add photo attachment (assume it's defined elsewhere)
        add_photo_attachment(downloaded, attachment_path, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error adding photo attachment: {e}")
        os.remove(downloaded)
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception as e:
                print(e)
                file_thumb = None

    filesize = os.path.getsize(output_file)

    await safe_edit_message(sts, "🔼 Uploading modified file... ⚡")
    try:
        # Upload to Google Drive if file size exceeds the limit
        if filesize > FILE_SIZE_LIMIT:
            # Function to upload to Google Drive (assume it's defined elsewhere)
            file_link = await upload_to_google_drive(output_file, os.path.basename(output_file), sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"**File successfully changed metadata and uploaded to Google Drive!**\n\n"
                f"**Google Drive Link**: [View File]({file_link})\n\n"
                f"**Uploaded File**: {output_filename}\n"
                f"**Request User:** {msg.from_user.mention}\n\n"
                f"**Size**: {humanbytes(filesize)}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            # Send modified file to user's PM
            await bot.send_document(
                msg.from_user.id,
                document=output_file,
                thumb=file_thumb,
                caption="Here is your file with the photo attached.",
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
            )

            # Notify in the group about the upload
            await msg.reply_text(
                f"┏📥 **File Name:** {output_filename}\n"
                f"┠💾 **Size:** {humanbytes(filesize)}\n"
                f"┠♻️ **Mode:** Attach Photo\n"
                f"┗🚹 **Request User:** {msg.from_user.mention}\n\n"
                f"❄ **File has been sent to your PM in the bot!**"
            )

        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading modified file: {e}")
    finally:
        os.remove(downloaded)
        os.remove(output_file)
        if file_thumb and os.path.exists(file_thumb):
            os.remove(file_thumb)
        if os.path.exists(attachment_path):
            os.remove(attachment_path)



# Command handler
# Command handler for changing audio index
@Client.on_message(filters.private & filters.command("swapaudio"))
async def swap_audio(bot, msg):
    global SWAP_INDEX_ENABLED

    if not SWAP_INDEX_ENABLED:
        return await msg.reply_text("The swap audio index feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `/swapaudio a-3-1-2-4 -n filename.mkv` (Audio)")

    if len(msg.command) < 3:
        return await msg.reply_text("Please provide the index command with a filename\nFormat: `/swapaudio a-3-1-2-4 -n filename.mkv` (Audio)")

    index_cmd = None
    output_filename = None

    # Extract index command and output filename from the command
    for i in range(1, len(msg.command)):
        if msg.command[i] == "-n":
            output_filename = " ".join(msg.command[i + 1:])  # Join all the parts after the flag
            break

    index_cmd = " ".join(msg.command[1:i])  # Get the index command before the flag

    if not output_filename:
        return await msg.reply_text("Please provide a filename using the `-n` flag.")

    if not index_cmd or not index_cmd.startswith("a-"):
        return await msg.reply_text("Invalid format. Use `/swapaudio a-3-1-2-4 -n filename.mkv` for audio.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the index command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        # Download the media file
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    # Output file path (temporary file)
    output_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', output_file, '-y'])

    await sts.edit("💠 Changing audio indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await sts.edit(f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        if os.path.exists(output_file):
            os.remove(output_file)
        return

    # Thumbnail handling
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)

    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception as e:
            file_thumb = None
    else:
        file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed audio index and uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=output_filename,  # Apply the new file name here
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡️", sts, c_time)
            )
        except Exception as e:
            return await sts.edit(f"Error: {e}")

    # Clean up downloaded and temporary files
    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()

#changeindex subtitles 
# Command to change index subtitle
# Command handler for changing subtitle index
@Client.on_message(filters.private & filters.command("swapsubtitles"))
async def swap_subtiles(bot, msg):
    global SWAP_INDEX_ENABLED

    if not SWAP_INDEX_ENABLED:
        return await msg.reply_text("The swap subitles index feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `/swapsubtitles s-2-3-1 -n filename.mkv` (Subtitle)")

    if len(msg.command) < 3:
        return await msg.reply_text("Please provide the index command with a filename\nFormat: `/swapsubtitles s-2-3-1 -n filename.mkv` (Subtitle)")

    index_cmd = None
    output_filename = None

    # Extract index command and output filename from the command
    for i in range(1, len(msg.command)):
        if msg.command[i] == "-n":
            output_filename = " ".join(msg.command[i + 1:])  # Join all the parts after the flag
            break

    index_cmd = " ".join(msg.command[1:i])  # Get the index command before the flag

    if not output_filename:
        return await msg.reply_text("Please provide a filename using the `-n` flag.")

    if not index_cmd or not index_cmd.startswith("s-"):
        return await msg.reply_text("Invalid format. Use `/swapsubtitles s-2-3-1 -n filename.mkv` for subtitles.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the index command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        # Download the media file
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    # Output file path (temporary file)
    output_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded]

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all audio and video streams
    ffmpeg_cmd.extend(['-map', '0:v?', '-map', '0:a?', '-c', 'copy', output_file, '-y'])

    await safe_edit_message(sts, "💠 Changing subtitle indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await safe_edit_message(sts, f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        return

    # Thumbnail handling
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)

    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception as e:
            file_thumb = None
    else:
        file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed subtitle index and uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(msg.chat.id, document=output_file, file_name=output_filename, thumb=file_thumb, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
        except Exception as e:
            return await safe_edit_message(sts, f"Error: {e}")

    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()



#merge command 
@Client.on_message(filters.private & filters.command("merge"))
async def start_merge_command(bot, msg: Message):
    global MERGE_ENABLED
    if not MERGE_ENABLED:
        return await msg.reply_text("The merge feature is currently disabled.")

    user_id = msg.from_user.id
    merge_state[user_id] = {"files": [], "output_filename": None, "is_merging": False}

    await msg.reply_text("Send up to 10 video/document files one by one. Once done, send `/videomerge filename`.")

@Client.on_message(filters.private & filters.command("videomerge"))
async def start_video_merge_command(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id not in merge_state or not merge_state[user_id]["files"]:
        return await msg.reply_text("No files received for merging. Please send files using /merge command first.")

    output_filename = msg.text.split(' ', 1)[1].strip()  # Extract output filename from command
    merge_state[user_id]["output_filename"] = output_filename
    merge_state[user_id]["is_merging"] = True  # Set the flag to indicate that merging has started

    await merge_and_upload(bot, msg)

@Client.on_message(filters.document | filters.video & filters.private)
async def handle_media_files(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id in merge_state:
        if merge_state[user_id].get("is_merging"):
            await msg.reply_text("Merging process has started. No more files can be added.")
            return
        
        if len(merge_state[user_id]["files"]) < 10:
            merge_state[user_id]["files"].append(msg)
            await msg.reply_text("File received. Send another file or use `/videomerge filename` to start merging.")
        else:
            await msg.reply_text("You have already sent 10 files. Use `/videomerge filename` to start merging.")


async def merge_and_upload(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id not in merge_state:
        return await msg.reply_text("No merge state found for this user. Please start the merge process again.")

    files_to_merge = merge_state[user_id]["files"]
    output_filename = merge_state[user_id].get("output_filename", "SH24BOTS_merged.mkv")  # Default output filename
    output_path = f"{output_filename}"

    sts = await msg.reply_text("🚀 Starting merge process...")

    try:
        file_paths = []
        for file_msg in files_to_merge:
            file_path = await download_media(file_msg, sts)
            file_paths.append(file_path)

        input_file = "input.txt"
        with open(input_file, "w") as f:
            for file_path in file_paths:
                f.write(f"file '{file_path}'\n")

        await sts.edit("💠 Merging videos... ⚡")
        await merge_videos(input_file, output_path)

        filesize = os.path.getsize(output_path)
        filesize_human = humanbytes(filesize)
        cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

        await sts.edit("💠 Uploading... ⚡")

        # Thumbnail handling
        thumbnail_file_id = await db.get_thumbnail(user_id)
        file_thumb = None
        if thumbnail_file_id:
            try:
                file_thumb = await bot.download_media(thumbnail_file_id)
            except Exception as e:
                print(f"Error downloading thumbnail: {e}")

        # Uploading the merged file
        c_time = time.time()
        if filesize > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(output_path, output_filename, sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"File successfully merged and uploaded to Google Drive!\n\n"
                f"Google Drive Link: [View File]({file_link})\n\n"
                f"Uploaded File: {output_filename}\n"
                f"Request User: {msg.from_user.mention}\n\n"
                f"Size: {filesize_human}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            await bot.send_document(
                user_id,
                document=output_path,
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )

            await msg.reply_text(
                f"┏📥 **File Name:** {output_filename}\n"
                f"┠💾 **Size:** {filesize_human}\n"
                f"┠♻️ **Mode:** Merge : Video + Video\n"
                f"┗🚹 **Request User:** {msg.from_user.mention}\n\n"
                f"❄ **File has been sent in Bot PM!**"
            )

    except Exception as e:
        await sts.edit(f"❌ Error: {e}")

    finally:
        # Clean up temporary files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_path):
            os.remove(output_path)
        if file_thumb and os.path.exists(file_thumb):
            os.remove(file_thumb)

        # Clear merge state for the user
        if user_id in merge_state:
            del merge_state[user_id]

        await sts.delete()

# Leech command handler
# ==========================================================
# UNIVERSAL DOWNLOADER (used by BOTH /leech & /multitasklink)
# ==========================================================
async def download_any_link(url, file_path, status_msg):
    """
    Universal link downloader with:
    - Resume
    - Range requests
    - Chunk streaming
    - Same progress UI
    - Safe for Koyeb
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    chunk_size = 256 * 1024  # 256KB safe memory usage
    downloaded = 0
    start_time = time.time()

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, timeout=None, allow_redirects=True) as resp:
            if resp.status not in (200, 206):
                raise Exception(f"HTTP {resp.status}")

            total = int(resp.headers.get("Content-Length", 0) or 0)

            # create file
            with open(file_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(chunk_size):
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    try:
                        await progress_message(
                            downloaded,
                            total if total else downloaded,
                            "🚀 Downloading...",
                            status_msg,
                            start_time
                        )
                    except:
                        pass

    # final 100%
    try:
        await progress_message(
            downloaded,
            downloaded if total == 0 else total,
            "✅ Download Completed",
            status_msg,
            start_time
        )
    except:
        pass

    return True



# ==========================================================
# /leech HANDLER (USES SAME FUNCTIONS AS multitasklink)
# ==========================================================
@Client.on_message(filters.command("leech") & filters.chat(AUTH_USERS))
async def linktofile(bot: Client, msg: Message):

    if not msg.reply_to_message:
        return await msg.reply_text("Reply to a LINK.\n\nFormat:\n`/leech movie.mkv`")

    reply = msg.reply_to_message
    text = reply.text or reply.caption or ""

    # Detect URL
    m = re.search(r"(https?://[^\s]+)", text)
    if not m:
        return await msg.reply_text("❌ No URL found in replied message.")

    url = m.group(0)

    # Filename
    if len(msg.command) < 2:
        return await msg.reply_text("❌ Provide filename.\nExample:\n`/leech file.mkv`")

    new_name = msg.text.split(" ", 1)[1].strip()

    if not any(new_name.endswith(ext) for ext in (".mkv", ".mp4", ".zip", ".avi", ".mp3", ".pdf")):
        return await msg.reply_text("❌ Filename must have a valid extension.")

    # Start message
    sts = await msg.reply_text(f"🔗 Link detected:\n`{url}`\n\n🚀 Starting download...")

    # Temp path
    tmp = tempfile.gettempdir()
    file_path = os.path.join(tmp, new_name)

    # Remove previous file
    if os.path.exists(file_path):
        os.remove(file_path)

    # DOWNLOAD
    try:
        await download_any_link(url, file_path, sts)
    except Exception as e:
        return await sts.edit(f"❌ Download error:\n`{e}`")

    # Upload
    size = humanbytes(os.path.getsize(file_path))

    # Thumbnail (same system as multitasklink)
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    og_thumb = None
    if thumbnail_file_id:
        try:
            og_thumb = await bot.download_media(thumbnail_file_id)
        except:
            og_thumb = None

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()

    try:
        # TG Upload or Drive fallback
        if os.path.getsize(file_path) > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(file_path, new_name, sts)
            await msg.reply_text(
                f"☁️ **Uploaded to Google Drive**\n\n"
                f"📁 `{new_name}`\n"
                f"💾 `{size}`\n"
                f"🔗 {file_link}"
            )
        else:
            await bot.send_document(
                msg.chat.id,
                document=file_path,
                caption=f"{new_name}\n\n🌟 Size: {size}",
                thumb=og_thumb,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )
    except Exception as e:
        return await sts.edit(f"❌ Upload failed:\n`{e}`")

    # Cleanup
    try:
        if og_thumb and os.path.exists(og_thumb):
            os.remove(og_thumb)
        os.remove(file_path)
    except:
        pass

    await sts.delete()



#Removetags command 
async def safe_edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text)
    except Exception as e:
        print(f"Failed to edit message: {e}")
        
# Command to remove tags from media files
@Client.on_message(filters.private & filters.command("removetags"))
async def remove_tags(bot, msg):
    global REMOVETAGS_ENABLED
    if not REMOVETAGS_ENABLED:
        return await msg.reply_text("The removetags feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the removetags command.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the removetags command.")

    command_text = " ".join(msg.command[1:]).strip()
    new_filename = None

    # Extract new filename from command
    if "-n" in command_text:
        try:
            new_filename = command_text.split('-n')[1].strip()
        except IndexError:
            return await msg.reply_text("Please provide a valid filename with the -n option (e.g., `-n new_filename.mkv`).")

        # Check if new filename has a valid video file extension (.mkv, .mp4, .avi)
        valid_extensions = ('.mkv', '.mp4', '.avi')
        if not any(new_filename.lower().endswith(ext) for ext in valid_extensions):
            return await msg.reply_text("The new filename must include a valid extension (e.g., `.mkv`, `.mp4`, `.avi`).")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    cleaned_file = new_filename if new_filename else "cleaned_" + os.path.basename(downloaded)

    await safe_edit_message(sts, "💠 Removing all tags... ⚡")
    try:
        remove_all_tags(downloaded, cleaned_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error removing all tags: {e}")
        os.remove(downloaded)
        return

    # Retrieve thumbnail from database
    file_thumb = None
    thumbnail_id = await db.get_thumbnail(msg.from_user.id)
    if thumbnail_id:
        try:
            file_thumb = await bot.download_media(thumbnail_id, file_name=f"thumbnail_{msg.from_user.id}.jpg")
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")

    await safe_edit_message(sts, "🔼 Uploading cleaned file... ⚡")
    try:
        # Upload to Google Drive if file size exceeds the limit
        filesize = os.path.getsize(cleaned_file)
        if filesize > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(cleaned_file, os.path.basename(cleaned_file), sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"File successfully Removed tags and uploaded to Google Drive!\n\n"
                f"Google Drive Link: [View File]({file_link})\n\n"
                f"Uploaded File: {os.path.basename(cleaned_file)}\n"
                f"Request User: {msg.from_user.mention}\n\n"
                f"Size: {humanbytes(filesize)}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            # Send cleaned file to user's PM
            await bot.send_document(
                msg.from_user.id,
                cleaned_file,
                thumb=file_thumb,
                caption="Here is your file with all tags removed.",
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
            )

            # Notify in the group about the upload
            await msg.reply_text(
                f"┏📥 **File Name:** {os.path.basename(cleaned_file)}\n"
                f"┠💾 **Size:** {humanbytes(filesize)}\n"
                f"┠♻️ **Mode:** Remove Tags\n"
                f"┗🚹 **Request User:** {msg.from_user.mention}\n\n"
                f"❄ **File has been sent to your PM in the bot!**"
            )

        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading cleaned file: {e}")
    finally:
        os.remove(downloaded)
        os.remove(cleaned_file)
        if file_thumb and os.path.exists(file_thumb):
            os.remove(file_thumb)

    # Save new filename to database
    if new_filename:
        await db.save_new_filename(msg.from_user.id, new_filename)

#Screenshots Command
@Client.on_message(filters.private & filters.command("screenshots"))
async def screenshots_command(client, message: Message):
    user_id = message.from_user.id

    # Fetch user settings for screenshots count
    num_screenshots = await db.get_screenshots_count(user_id)
    if not num_screenshots:
        num_screenshots = 5  # Default to 5 if not set

    if not message.reply_to_message:
        return await message.reply_text("Please reply to a valid video file or document.")

    media = message.reply_to_message.video or message.reply_to_message.document
    if not media:
        return await message.reply_text("Please reply to a valid video file.")

    sts = await message.reply_text("🚀 Downloading media... ⚡")
    try:
        input_path = await client.download_media(media)
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    if not os.path.exists(input_path):
        await sts.edit("Error: The downloaded file does not exist.")
        return

    try:
        await sts.edit("🚀 Reading video duration... ⚡")
        command = ['ffprobe', '-i', input_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']
        duration_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        duration = float(duration_output.decode('utf-8').strip())
    except subprocess.CalledProcessError as e:
        await sts.edit(f"Error reading video duration: {e.output.decode('utf-8')}")
        os.remove(input_path)
        return
    except ValueError:
        await sts.edit("Error reading video duration: Unable to convert duration to float.")
        os.remove(input_path)
        return

    interval = duration / num_screenshots

    await sts.edit(f"🚀 Generating {num_screenshots} screenshots... ⚡")
    screenshot_paths = []
    for i in range(num_screenshots):
        time_position = interval * i
        screenshot_path = f"screenshot_{user_id}_{i}.jpg"

        command = ['ffmpeg', '-ss', str(time_position), '-i', input_path, '-vframes', '1', '-y', screenshot_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            await sts.edit(f"Error generating screenshot {i+1}: {stderr.decode('utf-8')}")
            for path in screenshot_paths:
                os.remove(path)
            os.remove(input_path)
            return

        screenshot_paths.append(screenshot_path)

        # Upload screenshot to user's PM
        try:
            await client.send_photo(chat_id=user_id, photo=screenshot_path)
        except Exception as e:
            await sts.edit(f"Error uploading screenshot {i+1}: {e}")
            os.remove(screenshot_path)

        os.remove(screenshot_path)  # Remove local screenshot after uploading

    # Save screenshot paths to database
    await db.save_screenshot_paths(user_id, screenshot_paths)

    os.remove(input_path)  # Remove downloaded media file

    # Send notification in group chat
    try:
        await message.reply_text("📸 Screenshots have been sent to your PM.")
    except Exception as e:
        print(f"Failed to send notification: {e}")

    # Cleanup: Delete screenshot paths from database after sending
    await db.delete_screenshot_paths(user_id)

    await sts.delete()  # Delete the status message after completion



@Client.on_message(filters.private & filters.command("samplevideo"))
async def sample_video(bot, msg):
    user_id = msg.from_user.id

    # Fetch user settings
    sample_video_duration = await db.get_sample_video_duration(user_id)

    if sample_video_duration is None:
        return await msg.reply_text("Please set a valid sample video duration using /usersettings.")

    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a valid video file or document.")

    media = msg.reply_to_message.video or msg.reply_to_message.document
    if not media:
        return await msg.reply_text("Please reply to a valid video file or document.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        input_path = await bot.download_media(media, progress=progress_message, progress_args=("🚀 Downloading media... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    output_file = f"sample_video_{sample_video_duration}s.mp4"

    await sts.edit("🚀 Processing sample video... ⚡")
    try:
        generate_sample_video(input_path, sample_video_duration, output_file)
    except Exception as e:
        await sts.edit(f"Error generating sample video: {e}")
        os.remove(input_path)
        return

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟 Size: {filesize_human}"

    await sts.edit("💠 Uploading sample video to your PM... ⚡")
    c_time = time.time()
    try:
        await bot.send_document(
            user_id, 
            document=output_file, 
            caption=cap, 
            progress=progress_message, 
            progress_args=("💠 Upload Started... ⚡️", sts, c_time)
        )
        # Save sample video settings to database
        await db.save_sample_video_settings(user_id, sample_video_duration, "Not set")

        # Send notification about the file upload
        await msg.reply_text(f"File Sample Video has been uploaded to your PM. Check your PM of the bot ✅ .")

    except Exception as e:
        await sts.edit(f"Error uploading sample video: {e}")
        return

    os.remove(input_path)
    os.remove(output_file)
    await sts.delete()

 # Define restart_app command
@Client.on_message(filters.command("restartheroku") & filters.chat(AUTH_USERS))
async def restart_app(bot, msg):
    if not f'{msg.from_user.id}' == f'{int(AUTH_USERS)}':
        return await msg.reply_text("Only authorized user can restart!")

    result = await heroku_restart()
    if result is None:
        return await msg.reply_text("You have not filled `HEROKU_API` and `HEROKU_APP_NAME` vars.")
    elif result is False:
        return await msg.reply_text("An error occurred!")
    elif result is True:
        return await msg.reply_text("Restarting app, wait for a minute.")
        

# Command to unzip a zip file
@Client.on_message(filters.private & filters.command("unzip"))
async def unzip(bot, msg):
    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a zip file to unzip.")

    media = msg.reply_to_message.document
    if not media or not media.file_name.endswith('.zip'):
        return await msg.reply_text("Please reply to a valid zip file.")

    sts = await msg.reply_text("🚀Downloading file...⚡")
    c_time = time.time()
    input_path = await bot.download_media(media, progress=progress_message, progress_args=("🚀Downloading file...⚡️", sts, c_time))

    if not os.path.exists(input_path):
        await sts.edit(f"Error: The downloaded file does not exist.")
        return

    extract_path = os.path.join("extracted")
    os.makedirs(extract_path, exist_ok=True)

    await sts.edit("🚀Unzipping file...⚡")
    extracted_files = unzip_file(input_path, extract_path)

    if extracted_files:
        await sts.edit(f"✅ File unzipped successfully. Uploading extracted files...⚡")
        await upload_files(bot, msg.chat.id, extract_path)
        await sts.edit(f"✅ All extracted files uploaded successfully.")

        # Save extracted files to database
        await db.save_extracted_files(msg.from_user.id, extracted_files)
    else:
        await sts.edit(f"❌ Failed to unzip file.")

    os.remove(input_path)
    shutil.rmtree(extract_path)

  
@Client.on_message(filters.command("gofile") & filters.private)
async def gofile_upload(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Gofile API key from the database
    gofile_api_key = await db.get_gofile_api_key(user_id)

    if not gofile_api_key:
        return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")

    reply = msg.reply_to_message
    if not reply or not reply.document and not reply.video:
        return await msg.reply_text("Please reply to a file or video to upload to Gofile.")

    media = reply.document or reply.video
    custom_name = None

    # Check if a custom name is provided
    args = msg.text.split(" ", 1)
    if len(args) == 2:
        custom_name = args[1]
        await db.save_custom_name(user_id, custom_name)  # Save custom name to database

    # Use custom name if available, otherwise use the file name
    file_name = custom_name or media.file_name

    sts = await msg.reply_text("🚀 Uploading to Gofile...")
    c_time = time.time()
    
    downloaded_file = None

    try:
        async with aiohttp.ClientSession() as session:
            # Get available servers
            async with session.get("https://api.gofile.io/servers") as resp:
                if resp.status != 200:
                    return await sts.edit(f"Failed to get servers. Status code: {resp.status}")

                data = await resp.json()
                servers = data.get("data", {}).get("servers", [])
                if not servers:
                    return await sts.edit("No servers available.")
                
                server_name = servers[0].get("name")  # Use the server name
                if not server_name:
                    return await sts.edit("Server name is missing.")
                
                upload_url = f"https://{server_name}.gofile.io/contents/uploadfile"

            # Download the media file
            downloaded_file = await bot.download_media(
                media,
                file_name=file_name,  # Use custom or original filename directly
                progress=progress_message,
                progress_args=("🚀 Download Started...", sts, c_time)
            )

            # Upload the file to Gofile
            with open(downloaded_file, "rb") as file:
                form_data = aiohttp.FormData()
                form_data.add_field("file", file, filename=file_name)
                headers = {"Authorization": f"Bearer {gofile_api_key}"} if gofile_api_key else {}

                async with session.post(
                    upload_url,
                    headers=headers,
                    data=form_data
                ) as resp:
                    if resp.status != 200:
                        return await sts.edit(f"Upload failed: Status code {resp.status}")

                    response = await resp.json()
                    if response["status"] == "ok":
                        download_url = response["data"]["downloadPage"]
                        await sts.edit(f"Upload successful!\nDownload link: {download_url}")
                    else:
                        await sts.edit(f"Upload failed: {response['message']}")

    except Exception as e:
        await sts.edit(f"Error during upload: {e}")

    finally:
        try:
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
        except Exception as e:
            print(f"Error deleting file: {e}")


@Client.on_message(filters.private & filters.command("clone"))
async def clone_file(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID from database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)

    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    if len(msg.command) < 2:
        return await msg.reply_text("Please specify the Google Drive file URL.")

    src_url = msg.text.split(" ", 1)[1]
    src_id = extract_id_from_url(src_url)

    if not src_id:
        return await msg.reply_text("Invalid Google Drive URL. Please provide a valid file URL.")

    sts = await msg.reply_text("Starting cloning process...")

    try:
        copied_file_info = await copy_file(src_id, gdrive_folder_id)
        if copied_file_info:
            file_link = f"https://drive.google.com/file/d/{copied_file_info['id']}/view"
            button = [
                [InlineKeyboardButton("☁️ View File ☁️", url=file_link)]
            ]
            if copied_file_info['status'] == 'existing':
                await sts.edit(
                    f"File Already Exists 📂 : {copied_file_info['name']}\n[View File]({file_link})",
                    reply_markup=InlineKeyboardMarkup(button)
                )
            else:
                await sts.edit(
                    f"File Cloned Successfully ✅: {copied_file_info['name']}\n[View File]({file_link})",
                    reply_markup=InlineKeyboardMarkup(button)
                )
        else:
            await sts.edit("Failed to clone the file.")
    except Exception as e:
        await sts.edit(f"Error: {e}")


#safe edit message 
async def safe_edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text[:4096])  # Ensure text does not exceed 4096 characters
    except Exception as e:
        print(f"Failed to edit message: {e}")

#extract audio command 
@Client.on_message(filters.command("extractaudios") & filters.private)
async def extract_audios(bot, msg):
    global EXTRACT_ENABLED
    
    if not EXTRACT_ENABLED:
        return await msg.reply_text("The Extract Audio feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the extractaudios command.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the extractaudios command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    await safe_edit_message(sts, "🎵 Extracting audio streams... ⚡")
    try:
        extracted_files = extract_audios_from_file(downloaded)
        if not extracted_files:
            raise Exception("No audio streams found or extraction failed.")
    except Exception as e:
        await safe_edit_message(sts, f"Error extracting audio streams: {e}")
        os.remove(downloaded)
        return

    await safe_edit_message(sts, "🔼 Uploading extracted audio files... ⚡")
    try:
        for file, metadata in extracted_files:
            language = metadata.get('tags', {}).get('language', 'Unknown')
            caption = f"[{language}] Extracted audio file."
            await bot.send_document(
                msg.from_user.id,
                file,
                caption=caption[:1024],  # Ensure caption does not exceed 1024 characters
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
            )
                
        await msg.reply_text(
            "Audio streams extracted and sent to your PM in the bot!"
        )

        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading extracted audio files: {e}")
    finally:
        os.remove(downloaded)
        for file, _ in extracted_files:
            os.remove(file)


#extract subtitles command 
@Client.on_message(filters.command("extractsubtitles") & filters.private)
async def extract_subtitles(bot, msg):
    global EXTRACT_ENABLED
    
    if not EXTRACT_ENABLED:
        return await msg.reply_text("The Extract Subtitles feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the extractsubtitles command.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the extractsubtitles command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    await safe_edit_message(sts, "🎥 Extracting subtitle streams... ⚡")
    try:
        extracted_files = extract_subtitles_from_file(downloaded)
        if not extracted_files:
            raise Exception("No subtitle streams found or extraction failed.")
    except Exception as e:
        await safe_edit_message(sts, f"Error extracting subtitle streams: {e}")
        os.remove(downloaded)
        return

    await safe_edit_message(sts, "🔼 Uploading extracted subtitle files... ⚡")
    try:
        for file, metadata in extracted_files:
            language = metadata.get('tags', {}).get('language', 'Unknown')
            caption = f"[{language}] Here is an extracted subtitle file."
            await bot.send_document(
                msg.from_user.id,
                file,
                caption=caption,
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
            )

        await msg.reply_text(
            "Subtitle streams extracted and sent to your PM in the bot!"
        )

        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading extracted subtitle files: {e}")
    finally:
        os.remove(downloaded)
        for file, _ in extracted_files:
            os.remove(file)

##extract video command 
@Client.on_message(filters.command("extractvideo") & filters.private)
async def extract_video(bot, msg: Message):
    global EXTRACT_ENABLED
    
    if not EXTRACT_ENABLED:
        return await msg.reply_text("The extract feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file (video or document) with the extractvideo command.")

    media = reply.video or reply.document
    if not media:
        return await msg.reply_text("Please reply to a valid video or document file with the extractvideo command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    await safe_edit_message(sts, "🎥 Extracting video stream... ⚡")
    try:
        extracted_file = extract_video_from_file(downloaded)
        if not extracted_file:
            raise Exception("No video stream found or extraction failed.")
    except Exception as e:
        await safe_edit_message(sts, f"Error extracting video stream: {e}")
        os.remove(downloaded)
        return

    await safe_edit_message(sts, "🔼 Uploading extracted video... ⚡")
    try:
        output_extension = os.path.splitext(extracted_file)[1]
        output_file = os.path.join(os.path.dirname(downloaded), f"Extracted_By_Sunrises_24_Video{output_extension}")
        os.rename(extracted_file, output_file)

        await bot.send_document(
            msg.from_user.id,
            output_file,
            progress=progress_message,
            progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
        )
        await msg.reply_text(
            "Video stream extracted and sent to your PM in the bot!"
        )

        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading extracted video: {e}")
    finally:
        os.remove(downloaded)
        if os.path.exists(output_file):
            os.remove(output_file)

# Command handler for /list
@Client.on_message(filters.private & filters.command("list"))
async def list_files(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID from database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)

    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    sts = await msg.reply_text("Fetching File List...🔎")

    try:
        files = get_files_in_folder(gdrive_folder_id)
        if not files:
            return await sts.edit("No files found in the specified folder.")

        # Categorize files
        file_types = {'Images': [], 'Movies': [], 'Audios': [], 'Archives': [], 'Others': []}
        for file in files:
            mime_type = file['mimeType']
            file_name = file['name'].lower()
            if mime_type.startswith('image/'):
                file_types['Images'].append(file)
            elif mime_type.startswith('video/') or file_name.endswith(('.mkv', '.mp4')):
                file_types['Movies'].append(file)
            elif mime_type.startswith('audio/') or file_name.endswith(('.aac', '.eac3', '.mp3', '.opus', '.eac')):
                file_types['Audios'].append(file)
            elif file_name.endswith(('.zip', '.rar')):
                file_types['Archives'].append(file)
            else:
                file_types['Others'].append(file)

        # Create inline buttons for each category with emojis
        buttons = []
        for category, items in file_types.items():
            if items:
                if category == 'Images':
                    emoji = '🖼️'
                elif category == 'Movies':
                    emoji = '🎞️'
                elif category == 'Audios':
                    emoji = '🔊'
                elif category == 'Archives':
                    emoji = '📦'
                else:
                    emoji = '📁'

                buttons.append([InlineKeyboardButton(f"{emoji} {category}", callback_data=f"{category}")])
                for file in sorted(items, key=lambda x: x['name']):
                    file_link = f"https://drive.google.com/file/d/{file['id']}/view"
                    buttons.append([InlineKeyboardButton(file['name'], url=file_link)])

        await sts.edit(
            "Files In The Specified Folder 📁:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except HttpError as error:
        await sts.edit(f"An error occurred: {error}")
    except Exception as e:
        await sts.edit(f"Error: {e}")

#cleam command
@Client.on_message(filters.private & filters.command("clean"))
async def clean_files(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID from database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)

    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    try:
        # Check if the command is followed by a file name or a direct link
        command_parts = msg.text.split(maxsplit=1)
        if len(command_parts) < 2:
            return await msg.reply_text("Please provide a file name or direct link to delete.")

        query_or_link = command_parts[1].strip()

        # If the query_or_link starts with 'http', treat it as a direct link
        if query_or_link.startswith("http"):
            # Extract file ID from the direct link
            file_id = extract_id_from_url(query_or_link)
            if not file_id:
                return await msg.reply_text("Invalid Google Drive file link. Please provide a valid direct link.")

            # Delete the file by its ID
            drive_service.files().delete(fileId=file_id).execute()
            await msg.reply_text(f"Deleted File with ID '{file_id}' Successfully ✅.")

        else:
            # Treat it as a file name and delete files by name in the specified folder
            file_name = query_or_link

            # Define query to find files by name in the specified folder
            query = f"'{gdrive_folder_id}' in parents and trashed=false and name='{file_name}'"

            # Execute the query to find matching files
            response = drive_service.files().list(q=query, fields='files(id, name)').execute()
            files = response.get('files', [])

            if not files:
                return await msg.reply_text(f"No files found with the name '{file_name}' in the specified folder.")

            # Delete each found file
            for file in files:
                drive_service.files().delete(fileId=file['id']).execute()
                await msg.reply_text(f"Deleted File '{file['name']}' Successfully ✅.")

    except HttpError as error:
        await msg.reply_text(f"An error occurred: {error}")
    except Exception as e:
        await msg.reply_text(f"An unexpected error occurred: {e}")


#Downloading Progress Hook For YouTube In logs work process 
async def progress_hook(status_message):
    async def hook(d):
        if d['status'] == 'downloading':
            current_progress = d.get('_percent_str', '0%')
            current_size = humanbytes(d.get('total_bytes', 0))
            await safe_edit_message(status_message, f"🚀 Downloading... ⚡\nProgress: {current_progress}\nSize: {current_size}")
        elif d['status'] == 'finished':
            await safe_edit_message(status_message, "Download finished. 🚀")
    return hook
    
@Client.on_message(filters.private & filters.command("ytdlleech"))
async def ytdlleech_handler(client: Client, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a YouTube link.")

    command_text = msg.text.split(" ", 1)[1]
    url = command_text.strip()

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'noplaylist': True,
        'merge_output_format': 'mkv',
        'cookies': 'cookies.txt'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])

            buttons = [
                InlineKeyboardButton(
                    f"{f.get('format_note', 'Unknown')} - {humanbytes(f.get('filesize'))}",
                    callback_data=f"{f['format_id']}"
                )
                for f in formats if f.get('filesize') is not None
            ]
            buttons = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            await msg.reply_text("Choose quality:", reply_markup=InlineKeyboardMarkup(buttons))

            file_data = {
                'title': info_dict['title'],
                'thumbnail': info_dict.get('thumbnail')  # No default thumbnail path
            }
            await db.save_file_data(msg.from_user.id, file_data)

            user_quality_selection = {
                'url': url,
                'title': info_dict['title'],
                'thumbnail': info_dict.get('thumbnail'),
                'formats': formats
            }
            await db.save_user_quality_selection(msg.from_user.id, user_quality_selection)

    except Exception as e:
        await msg.reply_text(f"Error: {e}")

@Client.on_callback_query(filters.regex(r"^\d+$"))
async def callback_query_handler(client: Client, query):
    user_id = query.from_user.id
    format_id = query.data

    selection = await db.get_user_quality_selection(user_id)
    if not selection:
        return await query.answer("No download in progress.")

    url = selection['url']
    video_title = selection['title']
    formats = selection['formats']

    selected_format = next((f for f in formats if f['format_id'] == format_id), None)
    if not selected_format:
        return await query.answer("Invalid format selection.")

    quality = selected_format.get('format_note', 'Unknown')
    file_size = selected_format.get('filesize', 0)
    file_name = f"{video_title} - {quality}.mkv"

    sts = await query.message.reply_text(f"🚀 Downloading {quality} - {humanbytes(file_size)}... ⚡")

    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'outtmpl': file_name,
        'quiet': True,
        'noplaylist': True,
        'cookies': 'cookies.txt',
        'progress_hooks': [await progress_hook(status_message=sts)],
        'merge_output_format': 'mkv'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(file_name):
            return await safe_edit_message(sts, "Error: Download failed. File not found.")
        
        # No thumbnail downloading
        file_thumb = None
        
        if file_size >= FILE_SIZE_LIMIT:
            await safe_edit_message(sts, "💠 Uploading to Google Drive... ⚡")
            file_link = await upload_to_google_drive(file_name, file_name, sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await query.message.reply_text(
                f"**File successfully uploaded to Google Drive!**\n\n"
                f"**Google Drive Link**: [View File]({file_link})\n\n"
                f"**Uploaded File**: {file_name}\n"
                f"**Size**: {humanbytes(file_size)}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            await safe_edit_message(sts, "💠 Uploading to Telegram... ⚡")
            caption = f"**Uploaded Document 📄**: {file_name}\n\n🌟 Size: {humanbytes(file_size)}"
            
            try:
                with open(file_name, 'rb') as file:
                    await query.message.reply_document(
                        document=file,
                        caption=caption,
                        thumb=file_thumb,  # No thumbnail
                        progress=progress_message,
                        progress_args=("💠 Upload Started... ⚡", sts, time.time())
                    )
            except Exception as e:
                await safe_edit_message(sts, f"Error uploading file: {e}")
                return

    except Exception as e:
        await safe_edit_message(sts, f"Error: {e}")

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
        await sts.delete()
        await query.message.delete()



@Client.on_message(filters.command("mediainfo") & filters.private)
async def mediainfo_handler(client: Client, message: Message):
    if not message.reply_to_message or (not message.reply_to_message.document and not message.reply_to_message.video):
        await message.reply_text("Please reply to a document or video to get media info.")
        return

    reply = message.reply_to_message
    media = reply.document or reply.video

    # Send an acknowledgment message immediately
    processing_message = await message.reply_text("Getting MediaInfo...")

    try:
        # Download the media file to a local location
        if media:
            file_path = await client.download_media(media)
        else:
            raise ValueError("No valid media found in the replied message.")

        # Get media info
        media_info_html = get_mediainfo(file_path)

        # Remove date from the media info
        media_info_html = (
            f"<strong>SUNRISES 24 BOT UPDATES</strong><br>"
            f"<strong>MediaInfo X</strong><br>"
            f"{media_info_html}"
            f"<p>Rights Designed By Sᴜɴʀɪsᴇs Hᴀʀsʜᴀ 𝟸𝟺 🇮🇳 ᵀᴱᴸ</p>"
        )

        # Save the media info to an HTML file
        html_file_path = f"media_info_{media.file_id}.html"
        with open(html_file_path, "w") as file:
            file.write(media_info_html)

        # Store media info in MongoDB
        media_info_data = {
            'media_info': media_info_html,
            'media_id': media.file_id
        }
        media_info_id = await db.store_media_info_in_db(media_info_data)

        # Upload the media info to Telegraph
        response = telegraph.post(
            title="MediaInfo",
            author="SUNRISES 24 BOT UPDATES",
            author_url="https://t.me/Sunrises24BotUpdates",
            text=media_info_html
        )
        link = f"https://graph.org/{response['path']}"

        # Prepare the final message with the Telegraph link
        message_text = (
            f"SUNRISES 24 BOT UPDATES\n"
            f"MediaInfo X\n\n"
            f"[View Info on Telegraph]({link})\n"
            f"Rights designed by Sᴜɴʀɪsᴇs Hᴀʀsʜᴀ 𝟸𝟺 🇮🇳 ᵀᴱᴸ"
        )

        # Send HTML file and Telegraph link
        await message.reply_document(document=html_file_path, caption=message_text)

    except Exception as e:
        await message.reply_text(f"Error: {e}")
    finally:
        # Clean up the acknowledgment message
        await processing_message.delete()

        # Clean up downloaded files and HTML file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        if 'html_file_path' in locals() and os.path.exists(html_file_path):
            os.remove(html_file_path)
        

# Function to handle "/getmodapk" command
@Client.on_message(filters.private & filters.command("getmodapk"))
async def get_mod_apk(bot, msg: Message):

    if len(msg.command) < 2:
        return await msg.reply_text(
            "Please send a valid download URL from:\n"
            "- getmodsapk.com\n- gamedva.com\n- 5modapk.com"
        )

    apk_url = msg.command[1]

    # VALID URL LIST
    valid_prefixes = [
        "https://files.getmodsapk.com/",
        "https://file.gamedva.com/",
        "https://files.5modapk.com/",
        "https://gamedva.com/"
    ]

    # Validate link
    if not any(apk_url.startswith(prefix) for prefix in valid_prefixes):
        return await msg.reply_text("❌ Invalid URL. Use links from getmodsapk / gamedva / 5modapk.")

    sts = await msg.reply_text("🚀 Starting download...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(apk_url) as response:

                if response.status != 200:
                    return await sts.edit("❌ Download failed. Server responded with error.")

                # Extract clean filename
                file_name = apk_url.split("/")[-1].split("?")[0]
                if not file_name.lower().endswith((".apk", ".xapk")):
                    file_name += ".apk"     # fallback

                # Download file
                data = await response.read()
                with open(file_name, "wb") as f:
                    f.write(data)

                # Upload to telegram
                await sts.edit("📤 Uploading file to Telegram...")
                await bot.send_document(
                    msg.chat.id,
                    document=file_name,
                    caption=f"Downloaded from:\n{apk_url}"
                )

                # Remove locally
                os.remove(file_name)

                await sts.edit("✅ File sent successfully!")

    except Exception as e:
        await sts.edit(f"❌ Error occurred:\n`{str(e)}`")

    finally:
        await asyncio.sleep(2)
        await sts.delete()





@Client.on_message(filters.command("ban") & filters.user(ADMIN))
async def ban_user(bot, msg: Message):
    try:
        user_id = int(msg.text.split()[1])
        # Ban user in the database
        await db.ban_user(user_id)
        # Ban user from the chat
        await bot.ban_chat_member(chat_id=msg.chat.id, user_id=user_id)
        await msg.reply_text(f"User {user_id} has been banned.")
    except PyMongoError as e:
        await msg.reply_text(f"Database error occurred: {e}")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.reply_text(f"Flood wait error: Please try again later.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

@Client.on_message(filters.command("unban") & filters.user(ADMIN))
async def unban_user(bot, msg: Message):
    try:
        user_id = int(msg.text.split()[1])
        # Unban user in the database
        await db.unban_user(user_id)
        # Unban user from the chat
        await bot.unban_chat_member(chat_id=msg.chat.id, user_id=user_id)
        await msg.reply_text(f"User {user_id} has been unbanned.")
    except PyMongoError as e:
        await msg.reply_text(f"Database error occurred: {e}")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.reply_text(f"Flood wait error: Please try again later.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

@Client.on_message(filters.command("users") & filters.user(ADMIN))
async def count_users(bot, msg):
    try:
        total_users = await db.count_users()
        banned_users = await db.count_banned_users()

        response = (
            f"**User Statistics:**\n"
            f"Total Active Users: {total_users}\n"
            f"Banned Users: {banned_users}"
        )
        await msg.reply_text(response)
    except PyMongoError as e:
        await msg.reply_text(f"Database error occurred while counting users: {e}")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

        
@Client.on_message(filters.command("stats"))
async def stats_command(_, msg):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_message = (
        f"📊 **Server Stats** 📊\n\n"
        f"⏳ **Uptime:** `{uptime_str}`\n"
        f"💾 **Total Space:** `{total_space:.2f} GB`\n"
        f"📂 **Used Space:** `{used_space:.2f} GB` ({used_space / total_space * 100:.1f}%)\n"
        f"📁 **Free Space:** `{free_space:.2f} GB`\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"💻 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]
        ]
    )

    await msg.reply_text(stats_message, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^refresh_stats$"))
async def refresh_stats_callback(_, callback_query):
    # Refresh stats
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_message = (
        f"📊 **Server Stats** 📊\n\n"
        f"⏳ **Uptime:** `{uptime_str}`\n"
        f"💾 **Total Space:** `{total_space:.2f} GB`\n"
        f"📂 **Used Space:** `{used_space:.2f} GB` ({used_space / total_space * 100:.1f}%)\n"
        f"📁 **Free Space:** `{free_space:.2f} GB`\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"💻 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    await callback_query.message.edit_text(stats_message, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]
        ]
    ))


@Client.on_message(filters.command("clear") & filters.user(ADMIN))
async def clear_database_handler(client: Client, msg: Message):
    try:
        await db.clear_database()
        await msg.reply_text("Database has been cleared✅.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

@Client.on_message(filters.command("broadcast") & filters.user(ADMIN))
async def broadcast(bot, msg: Message):
    if not msg.reply_to_message:
        await msg.reply_text("Please reply to a message to broadcast it.")
        return

    broadcast_message = msg.reply_to_message

    # Fetch all user IDs
    user_ids = await db.get_all_user_ids()

    sent_count = 0
    failed_count = 0
    log_entries = []

    for user_id in user_ids:
        try:
            await broadcast_message.copy(chat_id=user_id)
            sent_count += 1
            log_entries.append(f"Sent to {user_id}")
        except Exception as e:
            failed_count += 1
            log_entries.append(f"Failed to send to {user_id}: {e}")

        await asyncio.sleep(0.5)  # To avoid hitting rate limits

    # Write log entries to a text file
    log_content = "\n".join(log_entries)
    with open("broadcast_log.txt", "w") as log_file:
        log_file.write(log_content)

    # Send summary to admin
    await msg.reply_text(f"Broadcast completed: {sent_count} sent, {failed_count} failed.")
    await msg.reply_document('broadcast_log.txt')


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
/clear - 𝑐𝑙𝑒𝑎𝑟 𝑡ℎ𝑒 𝑑𝑎𝑡𝑎𝑏𝑎𝑠𝑒
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
/mediainfo - 𝑀𝑒𝑑𝑖𝑎 & 𝑉𝑖𝑑𝑒𝑜 𝐼𝑛𝑓𝑜𝑟𝑚𝑎𝑡𝑖𝑜𝑛 ℹ️ 
/ytdlleech - 𝐿𝑒𝑒𝑐ℎ 𝑡ℎ𝑒 𝑌𝑜𝑢𝑡𝑢𝑏𝑒 𝐿𝑖𝑛𝑘𝑠
/streamremove  - 𝑅𝑒𝑚𝑜𝑣𝑒 𝐴𝑢𝑑𝑖𝑜𝑠 𝑜𝑟 𝑆𝑢𝑏𝑡𝑖𝑡𝑙𝑒𝑠
/multitaskfile - 𝐹𝑜𝑟 𝐹𝑖𝑙𝑒 𝐶ℎ𝑎𝑛𝑔𝑒𝑚𝑒𝑡𝑎𝑑𝑎𝑡𝑎, 𝑅𝑒𝑛𝑎𝑚𝑒, 𝐶ℎ𝑎𝑛𝑔𝑒𝑖𝑛𝑑𝑒𝑥𝑎𝑢𝑑𝑖𝑜, 𝐶ℎ𝑎𝑛𝑔𝑒𝑖𝑛𝑑𝑒𝑥𝑠𝑢𝑏 = 𝑚𝑢𝑙𝑡𝑖𝑡𝑎𝑠𝑘𝑓𝑖𝑙𝑒 
/multitasklink - 𝐹𝑜𝑟 𝑙𝑖𝑛𝑘  [𝑊𝑜𝑟𝑘𝑒𝑟𝑠 & 𝑆𝑒𝑒𝑑𝑟 𝐿𝑖𝑛𝑘𝑠] 𝑀𝑒𝑡𝑎𝑑𝑎𝑡𝑎, 𝑅𝑒𝑛𝑎𝑚𝑒, 𝐼𝑛𝑑𝑒𝑥𝑎𝑢𝑑𝑖𝑜, 𝐼𝑛𝑑𝑒𝑥𝑠𝑢𝑏 = 𝑚𝑢𝑙𝑡𝑖𝑡𝑎𝑠𝑘𝑙𝑖𝑛𝑘
/compress - 𝑐𝑜𝑚𝑝𝑟𝑒𝑠𝑠 𝑡ℎ𝑒 𝑓𝑖𝑙𝑒 𝑎𝑠 480𝑝 ,𝑙𝑖𝑏𝑜𝑝𝑢𝑠[𝐴𝑛𝑖𝑚𝑒 & 𝑊𝑒𝑏𝑠𝑒𝑟𝑖𝑒𝑠 𝐵𝑒𝑠𝑡]
/swapaudio - 𝑅𝑒𝑜𝑟𝑑𝑒𝑟 𝑡ℎ𝑒 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒 [a-2-1-3-4  𝑓𝑜𝑟 𝑠𝑤𝑎𝑝 𝑎𝑢𝑑𝑖𝑜]
/swapsubitles - 𝑅𝑒𝑜𝑟𝑑𝑒𝑟 𝑡ℎ𝑒 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒 [s-2-1-3-4  𝑓𝑜𝑟 𝑠𝑤𝑎𝑝 𝑠𝑢𝑏𝑡𝑖𝑡𝑙𝑒]
/changemetadata - 𝑇𝑟𝑎𝑛𝑠𝑓𝑜𝑟𝑚 𝑡ℎ𝑒 𝑚𝑒𝑡𝑎𝑑𝑎𝑡𝑎
/removetags - 𝑇𝑜 𝑅𝑒𝑚𝑜𝑣𝑒 𝐴𝑙𝑙 𝑀𝑒𝑡𝑎𝑑𝑎𝑡𝑎 𝑇𝑎𝑔𝑠
/merge - 𝑆𝑒𝑛𝑑 𝑢𝑝 𝑡𝑜 10 𝑣𝑖𝑑𝑒𝑜/𝑑𝑜𝑐𝑢𝑚𝑒𝑛𝑡 𝑓𝑖𝑙𝑒𝑠 𝑜𝑛𝑒 𝑏𝑦 𝑜𝑛𝑒.
/videomerge - 𝑉𝑖𝑑𝑒𝑜𝑚𝑒𝑟𝑔𝑒 𝑤𝑖𝑡ℎ 𝑓𝑖𝑙𝑒𝑛𝑎𝑚𝑒.𝑚𝑘𝑣 𝑡𝑜 𝑠𝑡𝑎𝑟𝑡 𝑚𝑒𝑟𝑔𝑖𝑛𝑔
/samplevideo - 𝐶𝑟𝑒𝑎𝑡𝑒 𝐴 𝑆𝑎𝑚𝑝𝑙𝑒 𝑉𝑖𝑑𝑒𝑜 🎞️
/screenshots - 𝐶𝑎𝑝𝑡𝑢𝑟𝑒 𝑠𝑜𝑚𝑒 𝑚𝑒𝑚𝑜𝑟𝑎𝑏𝑙𝑒 𝑠ℎ𝑜𝑡𝑠 📸
/unzip - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑓𝑖𝑙𝑒𝑠 (𝑍𝐼𝑃 𝑓𝑜𝑟𝑚𝑎𝑡 𝑜𝑛𝑙𝑦)
/setphoto  -  𝑇𝑜 𝑎𝑑𝑑 𝑎 𝑝ℎ𝑜𝑡𝑜 𝑡𝑜 𝑎 𝑓𝑖𝑙𝑒  𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.𝑗𝑝𝑔 𝑓𝑜𝑟 𝑠𝑒𝑛𝑑𝑖𝑛𝑔 𝑡ℎ𝑒 𝑝ℎ𝑜𝑡𝑜 𝑎𝑠 𝑎𝑛 𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.
/attachphoto - 𝑇ℎ𝑖𝑠 𝑐𝑜𝑚𝑚𝑎𝑛𝑑 𝑖𝑠 𝑢𝑠𝑒𝑑 𝑡𝑜 𝑎𝑑𝑑 𝑎 𝑝ℎ𝑜𝑡𝑜 𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.𝑗𝑝𝑔 𝑡𝑜 𝑎 𝑓𝑖𝑙𝑒
/stats - 𝑠𝑡𝑎𝑡𝑠 𝑜𝑓 𝑡ℎ𝑒 𝑏𝑜𝑡 📊
/users - 𝐴𝑐𝑡𝑖𝑣𝑒 𝑢𝑠𝑒𝑟𝑠 𝑜𝑓 𝑏𝑜𝑡[𝐴𝑑𝑚𝑖𝑛]
/ban - 𝐵𝑎𝑛 𝑡ℎ𝑒 𝑢𝑠𝑒𝑟 𝑓𝑟𝑜𝑚  𝐵𝑜𝑡[𝐴𝑑𝑚𝑖𝑛]
/unban - 𝑈𝑛𝑏𝑎𝑛 𝑡ℎ𝑒 𝑢𝑠𝑒𝑟 𝑓𝑟𝑜𝑚  𝐵𝑜𝑡[𝐴𝑑𝑚𝑖𝑛]
/broadcast  -  𝑀𝑒𝑠𝑠𝑎𝑔𝑒𝑠 𝑡𝑜 𝐸𝑣𝑒𝑟𝑦 𝑈𝑠𝑒𝑟𝑠 𝑖𝑛 𝑏𝑜𝑡 [𝐴𝑑𝑚𝑖𝑛]
/help - 𝐺𝑒𝑡 𝑑𝑒𝑡𝑎𝑖𝑙𝑒𝑑 𝑜𝑓 𝑏𝑜𝑡 𝑐𝑜𝑚𝑚𝑎𝑛𝑑𝑠 📝
/about - 𝐿𝑒𝑎𝑟𝑛 𝑚𝑜𝑟𝑒 𝑎𝑏𝑜𝑢𝑡 𝑡ℎ𝑖𝑠 𝑏𝑜𝑡 🧑🏻‍💻
/ping - 𝑇𝑜 𝐶ℎ𝑒𝑐𝑘 𝑇ℎ𝑒 𝑃𝑖𝑛𝑔 𝑂𝑓 𝑇ℎ𝑒 𝐵𝑜𝑡 📍

 💭• Tʜɪs Bᴏᴛ Is Fᴏʟʟᴏᴡs ᴛʜᴇ 𝟸GB Bᴇʟᴏᴡ Fɪʟᴇs Tᴏ Tᴇʟᴇɢʀᴀᴍ.\n• 𝟸GB Aʙᴏᴠᴇ Fɪʟᴇs Tᴏ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ.
 
🔱 𝐌𝐚𝐢𝐧𝐭𝐚𝐢𝐧𝐞𝐝 𝐁𝐲 : <a href='https://t.me/Sunrises_24'>𝐒𝐔𝐍𝐑𝐈𝐒𝐄𝐒™</a></b>
    
   """
    await msg.reply_text(help_text)


#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#Ping
@Client.on_message(filters.command("ping"))
async def ping(bot, msg):
    start_t = time.time()
    rm = await msg.reply_text("Checking")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Pong!📍\n{time_taken_s:.3f} ms")

@Client.on_message(filters.private & filters.command("multitaskfile"))
async def multitask_file(bot, msg: Message):
    global MULTITASK_ENABLED

    if not MULTITASK_ENABLED:
        return await msg.reply_text("Multi Task feature are currently disabled.")

    user_id = msg.from_user.id

    # Fetch metadata titles from the database
    metadata_titles = await db.get_metadata_titles(user_id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    if not any([video_title, audio_title, subtitle_title]):
        return await msg.reply_text("Metadata titles are not set. Please set metadata titles using `/setmetadata video_title audio_title subtitle_title`.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the change command\nFormat: `/change a-2 -m -n filename.mkv`")

    if len(msg.command) < 5 or '-m' not in msg.command or '-n' not in msg.command:
        return await msg.reply_text("Please provide the correct format\nFormat: `/change a-2 -m -n filename.mkv`")

    index_cmd = msg.command[1]
    metadata_flag_index = msg.command.index('-m')
    output_flag_index = msg.command.index('-n')
    output_filename = " ".join(msg.command[output_flag_index + 1:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the change command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    # Output file path (temporary file)
    intermediate_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', intermediate_file, '-y'])

    await safe_edit_message(sts, "💠 Changing audio indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await safe_edit_message(sts, f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        return

    output_file = output_filename

    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        change_video_metadata(intermediate_file, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error changing metadata: {e}")
        os.remove(downloaded)
        os.remove(intermediate_file)
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(user_id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception as e:
                file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed audio index and metadata, then uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=output_filename,
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )
        except Exception as e:
            return await safe_edit_message(sts, f"Error: {e}")

    os.remove(downloaded)
    os.remove(intermediate_file)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()



# -------------------- TURBO DOWNLOADER (LOW-IMPACT) --------------------
async def turbo_download_safe(url: str, out_path: str, status_msg, *,
                              part_size: int = 2 * 1024 * 1024,  # 2 MB parts
                              max_workers: int = 4,
                              retries: int = 3):
    """
    Safe turbo downloader:
      - Range requests
      - Resume support (reuses existing part files)
      - Limited concurrency (max_workers)
      - Merges parts into out_path
      - Uses your progress_message() for progress updates (same UI)
    Returns True on success, False on failure.
    """
    start_time = time.time()

    # HEAD to get total size and accept-ranges support
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.head(url, allow_redirects=True, timeout=60) as head:
                if head.status not in (200, 206):
                    await safe_edit_message(status_msg, f"❌ HTTP HEAD error: {head.status}")
                    return False
                total = int(head.headers.get("Content-Length", 0))
                accept_ranges = head.headers.get("Accept-Ranges", "none") != "none"
    except Exception as e:
        await safe_edit_message(status_msg, f"❌ Error fetching file info: {e}")
        return False

    if total == 0:
        # Try GET to detect content-length or non-range sources
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, allow_redirects=True, timeout=60) as resp:
                    if resp.status != 200:
                        await safe_edit_message(status_msg, f"❌ HTTP GET error: {resp.status}")
                        return False
                    total = int(resp.headers.get("Content-Length", 0) or 0)
                    if total == 0:
                        # fallback: stream entire file to single file (no range)
                        # We'll stream to out_path directly using download_stream below
                        return await _download_stream_fallback(url, out_path, status_msg, start_time)
        except Exception as e:
            await safe_edit_message(status_msg, f"❌ Error fetching direct file info: {e}")
            return False

    # compute ranges
    part_ranges = []
    for i in range(0, total, part_size):
        start = i
        end = min(i + part_size - 1, total - 1)
        part_ranges.append((start, end))

    parts_dir = os.path.join(tempfile.gettempdir(), f"mt_parts_{os.path.basename(out_path)}")
    os.makedirs(parts_dir, exist_ok=True)

    # track downloaded bytes from existing part files
    downloaded_bytes = 0
    part_paths = []
    for idx, (s, e) in enumerate(part_ranges):
        ppath = os.path.join(parts_dir, f"part_{idx}")
        part_paths.append(ppath)
        if os.path.exists(ppath):
            downloaded_bytes += os.path.getsize(ppath)

    # semaphore to limit concurrency
    sem = asyncio.Semaphore(max_workers)
    download_lock = asyncio.Lock()  # to safely update downloaded_bytes

    last_update = time.time()

    async def fetch_part(idx, byte_range):
        nonlocal downloaded_bytes, last_update
        pstart, pend = byte_range
        ppath = part_paths[idx]
        expected_size = pend - pstart + 1

        # resume: if exists and correct size, skip
        if os.path.exists(ppath) and os.path.getsize(ppath) == expected_size:
            return True

        # If partial part exists smaller than expected, resume inside part using Range
        resume_offset = 0
        if os.path.exists(ppath):
            resume_offset = os.path.getsize(ppath)

        headers = {"Range": f"bytes={pstart + resume_offset}-{pend}"}
        attempt = 0
        while attempt < retries:
            attempt += 1
            try:
                async with sem:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers, timeout=None) as resp:
                            # Acceptable statuses: 206 Partial or 200 OK (if server ignores range)
                            if resp.status not in (200, 206):
                                # retry
                                await asyncio.sleep(1)
                                continue

                            # open file in append binary mode
                            mode = "ab" if resume_offset else "wb"
                            with open(ppath, mode) as pf:
                                async for chunk in resp.content.iter_chunked(1024 * 1024):
                                    if not chunk:
                                        break
                                    pf.write(chunk)
                                    chunk_len = len(chunk)
                                    async with download_lock:
                                        downloaded_bytes += chunk_len

                                    # throttle progress edits to ~1s
                                    now = time.time()
                                    if now - last_update >= 1:
                                        try:
                                            await progress_message(
                                                downloaded_bytes,
                                                total,
                                                "🚀 Downloading...",
                                                status_msg,
                                                start_time
                                            )
                                        except Exception:
                                            pass
                                        last_update = now
                # after successful write, verify size
                if os.path.exists(ppath) and os.path.getsize(ppath) == expected_size:
                    return True
                # else retry
            except Exception as exc:
                logger.debug("Part %s attempt %s failed: %s", idx, attempt, exc)
                await asyncio.sleep(1)
                continue
        return False

    # run tasks
    tasks = [fetch_part(i, byte_range) for i, byte_range in enumerate(part_ranges)]
    done = await asyncio.gather(*tasks, return_exceptions=True)

    # check results
    for i, res in enumerate(done):
        if isinstance(res, Exception) or res is False:
            # cleanup partials to avoid corrupted merge
            # but keep parts for resume (do not delete)
            await safe_edit_message(status_msg, f"❌ Failed to download part {i}. Aborting.")
            return False

    # Final progress update
    try:
        await progress_message(downloaded_bytes, total, "✅ Merging parts...", status_msg, start_time)
    except Exception:
        pass

    # Merge parts into out_path
    try:
        with open(out_path, "wb") as outfile:
            for idx in range(len(part_ranges)):
                pfile = part_paths[idx]
                if not os.path.exists(pfile):
                    await safe_edit_message(status_msg, f"❌ Missing part {idx} during merge.")
                    return False
                with open(pfile, "rb") as pf:
                    shutil.copyfileobj(pf, outfile)
    except Exception as e:
        await safe_edit_message(status_msg, f"❌ Error merging parts: {e}")
        return False

    # Clean up part files directory (optional - keep if you want resume)
    try:
        shutil.rmtree(parts_dir, ignore_errors=True)
    except Exception:
        pass

    # Final progress (100%)
    try:
        await progress_message(total, total, "✅ Download Completed", status_msg, start_time)
    except Exception:
        pass

    return True


async def _download_stream_fallback(url: str, out_path: str, status_msg, start_time=None):
    """
    Fallback single-stream downloader (used when server doesn't support ranges).
    """
    if start_time is None:
        start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True, timeout=None) as resp:
                if resp.status != 200:
                    await safe_edit_message(status_msg, f"❌ Download failed: HTTP {resp.status}")
                    return False
                total = int(resp.headers.get("Content-Length", 0) or 0)
                downloaded = 0
                chunk_size = 1024 * 1024
                with open(out_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(chunk_size):
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        try:
                            await progress_message(downloaded, total, "🚀 Downloading...", status_msg, start_time)
                        except Exception:
                            pass
        await progress_message(downloaded, total, "✅ Download Completed", status_msg, start_time)
        return True
    except Exception as e:
        await safe_edit_message(status_msg, f"❌ Stream download error: {e}")
        return False


# -------------------- /multitasklink HANDLER (LINK ONLY) --------------------
@Client.on_message(filters.private & filters.command("multitasklink"))
async def multitasklink_handler(bot: Client, msg: Message):
    """
    Link-only multitasklink.
    Command format (example):
      /multitasklink a-3 -m -n output ... .mkv
    Reply must contain a HTTP/HTTPS URL.
    """
    if not msg.reply_to_message:
        return await msg.reply_text("❌ Reply to a message that contains a link.\nFormat: `/multitasklink a-3 -m -n filename.mkv`")

    reply = msg.reply_to_message
    reply_text = reply.text or reply.caption or ""
    m = URL_RE.search(reply_text)
    if not m:
        return await msg.reply_text("❌ No valid link found in the replied message.")

    url = m.group(0).strip()

    # Validate command format
    if len(msg.command) < 5 or "-m" not in msg.command or "-n" not in msg.command:
        return await msg.reply_text("❌ Wrong format.\nUse: `/multitasklink a-3 -m -n output.mkv`")

    index_cmd = msg.command[1]
    output_flag_index = msg.command.index("-n")
    output_name = " ".join(msg.command[output_flag_index + 1:]).strip()

    if not output_name.lower().endswith((".mkv", ".mp4", ".avi", ".zip")):
        return await msg.reply_text("❌ Output filename must end with .mkv / .mp4 / .avi / .zip")

    # Prepare temp path
    tmpdir = tempfile.gettempdir()
    local_path = os.path.join(tmpdir, output_name)

    # Remove existing local file if you want fresh download (keeps parts for resume)
    if os.path.exists(local_path):
        try:
            os.remove(local_path)
        except Exception:
            pass

    # Send status message
    sts = await msg.reply_text(f"🔗 Link detected:\n`{url}`\n\n🚀 Download starting...")

    # Run turbo download (safe low-impact config)
    ok = await turbo_download_safe(url, local_path, sts,
                                   part_size=2 * 1024 * 1024,  # 2MB
                                   max_workers=4,
                                   retries=3)
    if not ok:
        # turbo failed (maybe server blocks range requests) — try fallback stream
        await safe_edit_message(sts, "⚠️ Turbo download failed, trying single-stream fallback...")
        ok2 = await _download_stream_fallback(url, local_path, sts, start_time=time.time())
        if not ok2:
            return await safe_edit_message(sts, "❌ Both turbo and fallback downloads failed. Provide a direct link or check the URL.")

    # Ensure file exists
    if not os.path.exists(local_path):
        return await safe_edit_message(sts, "❌ Download ended but file missing.")

    # File size (human)
    filesize = os.path.getsize(local_path)
    filesize_human = humanbytes(filesize) if callable(humanbytes) else str(filesize)

    # Proceed to metadata/index changes (your existing function)
    try:
        await change_metadata_and_index(bot, msg, local_path, output_name, None, sts, time.time())
    except Exception as e:
        # If change_metadata_and_index raises, ensure cleanup and inform user
        logger.exception("Metadata/index error: %s", e)
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
        except Exception:
            pass
        return await safe_edit_message(sts, f"❌ Error processing file: {e}")

    return


# ---------------- PROCESS INDEX & METADATA (ADAPTED) ----------------
async def change_metadata_and_index(bot: Client, msg: Message, downloaded: str, new_name: str, media, sts, c_time):
    """
    Adapted from your original. This function:
      - Parses index_cmd from msg.command[1] (like 'a-2')
      - Runs ffmpeg remapping to create an intermediate file
      - Calls change_video_metadata to set titles (stubbed above; replace)
      - Uploads result (drive if large)
      - Cleans up files and thumbnails
    """
    # Flags guard
    # If you want to entirely disable, set these to False
    METADATA_ENABLED = True
    MULTITASKLINK_ENABLED = True

    if not (METADATA_ENABLED and MULTITASKLINK_ENABLED):
        await msg.reply_text("One or more required features are currently disabled.")
        return

    user_id = msg.from_user.id

    # Fetch metadata titles from DB (your real DB call)
    metadata_titles = await db.get_metadata_titles(user_id) if hasattr(db, "get_metadata_titles") else {}
    video_title = metadata_titles.get('video_title', '') if isinstance(metadata_titles, dict) else ''
    audio_title = metadata_titles.get('audio_title', '') if isinstance(metadata_titles, dict) else ''
    subtitle_title = metadata_titles.get('subtitle_title', '') if isinstance(metadata_titles, dict) else ''

    if not any([video_title, audio_title, subtitle_title]):
        # allow processing even if metadata titles are empty — depends on your preference
        # I'll continue but you can return early if you want strict behavior:
        # await msg.reply_text("Metadata titles are not set...")
        pass

    # validate command format
    if len(msg.command) < 5 or '-m' not in msg.command or '-n' not in msg.command:
        return await msg.reply_text("Please provide the correct format\nFormat: `/multitasklink a-2 -m -n filename.mkv`")

    index_cmd = msg.command[1]
    output_flag_index = msg.command.index('-n')
    output_filename = " ".join(msg.command[output_flag_index + 1:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use .mkv, .mp4, or .avi.")

    # prepare intermediate file path
    base, ext = os.path.splitext(downloaded)
    intermediate_file = f"{base}_indexed{ext}"

    # parse index params (like 'a-2' -> stream_type='a', indexes=[1])
    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    try:
        indexes = [int(i) - 1 for i in index_params[1:]]
    except Exception as e:
        return await msg.reply_text("Invalid index format. Example: a-2 or a-1-2")

    # construct ffmpeg command
    # Keep simple: -map 0:v + the requested -map 0:a:INDEX etc
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']

    for idx in indexes:
        # stream_type is usually 'a' or 'v' etc; we map: 0:a:idx
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # copy all subtitle streams if present
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', intermediate_file, '-y'])

    await safe_edit_message(sts, "💠 Changing audio indexing... ⚡")
    proc = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        # remove downloaded if desired
        try:
            if os.path.exists(downloaded):
                os.remove(downloaded)
        except Exception:
            pass
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        return await safe_edit_message(sts, f"❗ FFmpeg error:\n{stderr.decode('utf-8', errors='ignore')}")

    output_file = output_filename

    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        # call your metadata changer or the stub above
        change_video_metadata(intermediate_file, video_title, audio_title, subtitle_title, output_file)
    except NotImplementedError:
        # if your change_video_metadata requires implementation, pass error up
        raise
    except Exception as e:
        # cleanup on failure
        try:
            if os.path.exists(downloaded):
                os.remove(downloaded)
            if os.path.exists(intermediate_file):
                os.remove(intermediate_file)
        except Exception:
            pass
        return await safe_edit_message(sts, f"Error changing metadata: {e}")

    # Thumbnail retrieval
    thumbnail_file_id = await db.get_thumbnail(user_id) if hasattr(db, "get_thumbnail") else None
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            file_thumb = None
    else:
        # media is None in link-only mode; no thumbs
        file_thumb = None

    filesize_bytes = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize_bytes)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    try:
        if filesize_bytes > FILE_SIZE_LIMIT:
            # upload to drive, then send link
            try:
                file_link = await upload_to_google_drive(output_file, output_filename, sts)
            except NotImplementedError:
                return await safe_edit_message(sts, "❌ Google Drive upload not implemented. Implement upload_to_google_drive().")
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=file_link)]]
            await msg.reply_text(
                f"**File successfully changed audio index and metadata, then uploaded to Google Drive!**\n\n"
                f"**Google Drive Link**: [View File]({file_link})\n\n"
                f"**Uploaded File**: {output_filename}\n"
                f"**Request User:** {msg.from_user.mention}\n\n"
                f"**Size**: {filesize_human}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=output_filename,
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )
    except Exception as e:
        logger.exception("Upload failed")
        return await safe_edit_message(sts, f"Error during upload: {e}")

    # cleanup files
    for fp in (downloaded, intermediate_file, output_file):
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
        except Exception:
            logger.exception("Cleanup error for %s", fp)

    if file_thumb and os.path.exists(file_thumb):
        try:
            os.remove(file_thumb)
        except Exception:
            pass

    await sts.delete()

  
                

#handler is streamremove
async def safe_edit_message(message, text):
    try:
        await message.edit(text)
    except Exception:
        pass

@Client.on_message(filters.private & filters.command("streamremove"))
async def streamremove(bot, msg):
    global STREAMREMOVE_ENABLED
    global selected_streams
    global downloaded
    global output_filename

    if not STREAMREMOVE_ENABLED:
        return await msg.reply_text("🚫 The streamremove feature is currently disabled.")


    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text(
            "❗ Please reply to a media file with the command\nFormat: `/streamremove -n filename.mkv`"
        )

    if len(msg.command) < 3 or msg.command[1] != "-n":
        return await msg.reply_text(
            "Please provide the filename with the `-n` flag\nFormat: `/streamremove -n filename.mkv`"
        )

    output_filename = " ".join(msg.command[2:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text(
            "Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi)."
        )

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text(
            "❗ Please reply to a valid media file (audio, video, or document) with the command."
        )

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()

    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡", sts, c_time))
    except Exception as e:
        await sts.edit(f"❌ Error downloading media: {e}")
        return

    # Get the available streams using ffprobe
    ffprobe_cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'stream=index:stream_tags=language:stream=codec_type',
        '-of', 'json', downloaded
    ]
    process = await asyncio.create_subprocess_exec(
        *ffprobe_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await sts.edit(f"❗ FFprobe error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        return

    streams = json.loads(stdout.decode('utf-8')).get('streams', [])
    audio_video_streams = []
    subtitle_streams = []

    for stream in streams:
        stream_index = stream['index']
        language = stream.get('tags', {}).get('language', 'unknown')
        codec_type = stream['codec_type']

        if codec_type == 'audio':
            audio_video_streams.append(f"{stream_index} 🎵 Audio ({language})")
        elif codec_type == 'subtitle':
            subtitle_streams.append(f"{stream_index} 📝 Subtitle ({language})")
        elif codec_type == 'video':
            audio_video_streams.append(f"{stream_index} 📹 Video")

    # Build the inline keyboard
    buttons = []
    max_len = max(len(audio_video_streams), len(subtitle_streams))
    for i in range(max_len):
        row = []
        if i < len(audio_video_streams):
            row.append(
                InlineKeyboardButton(audio_video_streams[i], callback_data=f"toggle_{audio_video_streams[i].split()[0]}")
            )
        if i < len(subtitle_streams):
            row.append(
                InlineKeyboardButton(subtitle_streams[i], callback_data=f"toggle_{subtitle_streams[i].split()[0]}")
            )
        buttons.append(row)

    buttons.append([InlineKeyboardButton("🔄 Reverse Selection", callback_data="reverse")])
    buttons.append([
        InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
        InlineKeyboardButton("✅ Done", callback_data="done")
    ])

    markup = InlineKeyboardMarkup(buttons)
    selected_streams.clear()

    message = await sts.edit("Select the streams you want to remove (you have 60 seconds):", reply_markup=markup)

    await asyncio.sleep(60)

    try:
        await message.edit("🕒 Time's up! Selection process has been canceled.")
        await asyncio.sleep(5)
        await message.delete()
    except:
        pass

    if downloaded and os.path.exists(downloaded):
        os.remove(downloaded)
        
@Client.on_callback_query(filters.regex(r'toggle_\d+|done|cancel|reverse'))
async def callback_query_handler(bot, callback_query: CallbackQuery):
    global selected_streams
    global downloaded
    global output_filename

    data = callback_query.data

    if data == "cancel":
        await callback_query.message.delete()
        if downloaded and os.path.exists(downloaded):
            os.remove(downloaded)
        return

    if data == "reverse":
        buttons = callback_query.message.reply_markup.inline_keyboard
        all_indices = {btn.callback_data.split('_')[1] for row in buttons for btn in row if btn.callback_data.startswith('toggle_')}
        selected_streams.symmetric_difference_update(all_indices)

        for row in buttons:
            for button in row:
                if button.callback_data.startswith("toggle_"):
                    index = button.callback_data.split('_')[1]
                    if index in selected_streams:
                        button.text = f"✅ {button.text.lstrip('✅').strip()}"
                    else:
                        button.text = button.text.lstrip('✅').strip()

        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data == "done":
        sts = await callback_query.message.edit_text("💠 Removing selected streams... ⚡")
        await process_media(bot, callback_query, selected_streams, downloaded, output_filename, sts)
        return

    index = data.split('_')[1]
    if index in selected_streams:
        selected_streams.remove(index)
    else:
        selected_streams.add(index)

    buttons = callback_query.message.reply_markup.inline_keyboard
    for row in buttons:
        for button in row:
            if button.callback_data == f"toggle_{index}":
                if button.text.startswith("✅"):
                    button.text = button.text[2:]
                else:
                    button.text = f"✅ {button.text}"
                break

    await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


async def process_media(bot, callback_query, selected_streams, downloaded, output_filename, sts):
    user_id = callback_query.from_user.id
    output_file = output_filename

    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0']
    for idx in selected_streams:
        ffmpeg_cmd.extend(['-map', f'-0:{idx}'])
    ffmpeg_cmd.extend(['-c', 'copy', output_file, '-y']

    )

    process = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await safe_edit_message(sts, f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        if downloaded and os.path.exists(downloaded):
            os.remove(downloaded)
        if output_file and os.path.exists(output_file):
            os.remove(output_file)
        return

    # Get thumbnail
    file_thumb = None
    thumb_path = None
    try:
        thumbnail_file_id = await db.get_thumbnail(user_id)
        if thumbnail_file_id:
            thumb_path = await bot.download_media(thumbnail_file_id, file_name=f"thumb_{user_id}.jpg")
    except Exception as e:
        print(f"Thumbnail download error: {e}")
        thumb_path = None

    if thumb_path and os.path.exists(thumb_path):
        file_thumb = thumb_path
    else:
        file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    caption_text = f"**Processed File:** {output_filename}\n\n🌟 **Size:** {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=file_link)]]
        await bot.send_message(
            chat_id=user_id,
            text=f"**✅ Uploaded to GDrive:** [View File]({file_link})",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                chat_id=user_id,
                document=output_file,
                thumb=file_thumb,
                caption=caption_text,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )
        except Exception as e:
            await safe_edit_message(sts, f"❗ Upload Error: {e}")

    await bot.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=f"✅ File `{output_filename}` processed and sent to {callback_query.from_user.mention}."
    )

    # Clean up
    if downloaded and os.path.exists(downloaded):
        os.remove(downloaded)
    if output_file and os.path.exists(output_file):
        os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)

    await sts.delete()

     
#handler is Compress
@Client.on_message(filters.private & filters.command("compress"))
async def compress_media(bot, msg: Message):
    global COMPRESS_ENABLED

    if not COMPRESS_ENABLED:
        return await msg.reply_text("Compress feature is currently disabled.")

    user_id = msg.from_user.id
    reply = msg.reply_to_message

    if not reply:
        return await msg.reply_text(
            "Please reply to a video or media.\nFormat:\n`compress -n output.mp4`"
        )

    if len(msg.command) < 3 or msg.command[1] != "-n":
        return await msg.reply_text(
            "Invalid format.\nUse:\n`compress -n output.mp4`"
        )

    output_filename = " ".join(msg.command[2:]).strip()

    if not output_filename.lower().endswith(('.mp4', '.mkv', '.avi')):
        return await msg.reply_text("Invalid extension. Use .mp4 / .mkv / .avi")

    media = reply.document or reply.video or reply.audio
    if not media:
        return await msg.reply_text("Reply to a valid media file only.")

    # ---- START DOWNLOAD ----
    sts = await msg.reply_text("⬇️ **Downloading...**")
    c_time = time.time()

    try:
        downloaded = await reply.download(
            progress=progress_message,
            progress_args=("⬇️ **Download Started**", sts, c_time)
        )
    except Exception as e:
        await safe_edit_message(sts, f"❌ Download error: {e}")
        return

    output_file = output_filename

    # ---- LOAD USER METADATA ----
    metadata_titles = await db.get_metadata_titles(user_id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    # ---- START COMPRESSION ----
    await safe_edit_message(sts, "⚙️ **Starting Compression...**")

    ok = await compress_video(
        downloaded, output_file,
        video_title, audio_title, subtitle_title,
        sts
    )

    if not ok:
        os.remove(downloaded)
        return

    # ---- THUMBNAIL HANDLING ----
    thumbnail_file_id = await db.get_thumbnail(user_id)
    file_thumb = None

    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except:
            file_thumb = None
    elif hasattr(media, 'thumbs') and media.thumbs:
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id)
        except:
            file_thumb = None

    # ---- MEDIAINFO TELEGRAPH ----
    media_info_html, media_info_link = await get_and_upload_mediainfo(
        bot, output_file, media
    )

    size = os.path.getsize(output_file)
    size_human = humanbytes(size)

    caption = (
        f"{output_filename}\n\n"
        f"📦 **Size:** {size_human}\n"
        f"[ℹ️ MediaInfo]({media_info_link})"
    )

    await safe_edit_message(sts, "⬆️ **Uploading...**")
    c_time = time.time()

    # ---- FILE TOO BIG → GOOGLE DRIVE ----
    if size > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        btn = [[InlineKeyboardButton("☁️ Cloud URL", url=file_link)]]

        await msg.reply_text(
            f"✔ File compressed and uploaded!\n"
            f"Google Drive: [View File]({file_link})\n"
            f"Size: {size_human}\n"
            f"[MediaInfo]({media_info_link})",
            reply_markup=InlineKeyboardMarkup(btn)
        )
    else:
        # ---- NORMAL TELEGRAM UPLOAD ----
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                thumb=file_thumb,
                caption=caption,
                progress=progress_message,
                progress_args=("⬆️ **Upload Started**", sts, c_time)
            )
        except Exception as e:
            return await safe_edit_message(sts, f"❌ Upload error: {e}")

    # ---- CLEANUP ----
    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)

    await sts.delete()
    
    
@Client.on_message(filters.private & filters.command("dleech"))
async def rename_leech(bot, msg: Message):
    global RENAME_ENABLED

    if not RENAME_ENABLED:
        return await msg.reply_text("Rename feature is currently disabled.")

    user_id = msg.from_user.id

    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video or reply.text
    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]
    sts = await msg.reply_text("🚀 Downloading... ⚡")
    
    # Extract the Google Drive link from the caption or message text
    drive_url = reply.text or reply.caption
    file_id = extract_id_from_url(drive_url)

    if not file_id:
        return await sts.edit("❌ Invalid Google Drive link.")

    # Download the file from Google Drive with progress updates
    downloaded_file = await download_file_from_drive(drive_service, file_id, new_name, sts)
    filesize = humanbytes(os.path.getsize(downloaded_file))

    if CAPTION:
        try:
            cap = CAPTION.format(file_name=new_name, file_size=filesize)
        except KeyError as e:
            return await sts.edit(text=f"Caption error: unexpected keyword ({e})")
    else:
        cap = f"{new_name}\n\n🌟 Size: {filesize}"

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    og_thumbnail = None
    if thumbnail_file_id:
        try:
            og_thumbnail = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
            except Exception:
                pass

    await sts.edit("💠 Uploading... ⚡")

    try:
        await bot.send_document(msg.chat.id, document=downloaded_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, time.time()))
    except Exception as e:
        return await sts.edit(f"Error: {e}")

    os.remove(downloaded_file)
    await sts.delete()

@Client.on_message(filters.command('restart') & filters.user(ADMIN))
async def restart_message(app, message):
    reply = await message.reply_text('Restarting...')
    textx = f"Done Restart...✅"
    await reply.edit_text(textx)
    try:
        exit()
    finally:
        osexecl(executable, executable, "bot.py")


@Client.on_message(filters.command('logs') & filters.user(ADMIN))
async def log_file(b, m):
    try:
        await m.reply_document('SunrisesBot.txt')
    except Exception as e:
        await m.reply(str(e))

           
if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
