#TG : @Sunrises_24
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import subprocess
import os
import time, datetime
import shutil
import zipfile
import tarfile
import ffmpeg
from pyrogram.types import Message
from pyrogram.types import Document, Video
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import MessageNotModified
from config import DOWNLOAD_LOCATION, CAPTION
from main.utils import progress_message, humanbytes
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,CallbackQuery
from config import GROUP, AUTH_USERS, ADMIN
from main.utils import heroku_restart, upload_files, download_media
import aiohttp
from pyrogram.errors import RPCError, FloodWait
import asyncio
from main.ffmpeg import remove_all_tags, change_video_metadata, generate_sample_video, add_photo_attachment, merge_videos, unzip_file
from googleapiclient.http import MediaFileUpload
from main.gdrive import upload_to_google_drive, extract_id_from_url, copy_file, get_files_in_folder, drive_service
from googleapiclient.errors import HttpError


DOWNLOAD_LOCATION1 = "./screenshots"

# Global dictionary to store user settings
merge_state = {}
user_gofile_api_keys = {}  # Dictionary to store Gofile API keys for each user
user_settings = {}

# Initialize Gofile API key variable
GOFILE_API_KEY = ""

# Dictionary to store user-specific Google Drive folder IDs
user_gdrive_folder_ids = {}

FILE_SIZE_LIMIT = 2000 * 1024 * 1024  # 2000 MB in bytes

# Initialize global settings variables
METADATA_ENABLED = True 
PHOTO_ATTACH_ENABLED = True
MIRROR_ENABLED = True
RENAME_ENABLED = True
REMOVETAGS_ENABLED = True
CHANGE_INDEX_ENABLED = True 
MERGE_ENABLED = True
EXTRACT_ENABLED = True



#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Command handler to start the interaction (only in admin)
@Client.on_message(filters.command("bsettings") & filters.chat(ADMIN))
async def bot_settings_command(_, msg):
    await display_bot_settings_inline(msg)


# Inline function to display user settings with inline buttons
async def display_bot_settings_inline(msg):
    global METADATA_ENABLED, PHOTO_ATTACH_ENABLED, MIRROR_ENABLED, RENAME_ENABLED, REMOVETAGS_ENABLED, CHANGE_INDEX_ENABLED

    metadata_status = "✅ Enabled" if METADATA_ENABLED else "❌ Disabled"
    photo_attach_status = "✅ Enabled" if PHOTO_ATTACH_ENABLED else "❌ Disabled"
    mirror_status = "✅ Enabled" if MIRROR_ENABLED else "❌ Disabled"
    rename_status = "✅ Enabled" if RENAME_ENABLED else "❌ Disabled"
    removealltags_status = "✅ Enabled" if REMOVETAGS_ENABLED else "❌ Disabled"
    change_index_status = "✅ Enabled" if CHANGE_INDEX_ENABLED else "❌ Disabled"
    merge_video_status = "✅ Enabled" if MERGE_ENABLED else "❌ Disabled"    
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],            
            [InlineKeyboardButton(f"{rename_status} Change Rename 📝", callback_data="toggle_rename")],
            [InlineKeyboardButton(f"{removealltags_status} Remove All Tags 📛", callback_data="toggle_removealltags")],
            [InlineKeyboardButton(f"{metadata_status} Change Metadata ☄️", callback_data="toggle_metadata")],            
            [InlineKeyboardButton(f"{change_index_status} Change Index ♻️", callback_data="toggle_change_index")],
            [InlineKeyboardButton(f"{merge_video_status} Merge Video 🎞️", callback_data="toggle_merge_video")],
            [InlineKeyboardButton(f"{photo_attach_status} Attach Photo 🖼️", callback_data="toggle_photo_attach")],                        
            [InlineKeyboardButton(f"{mirror_status} Mirror 💽", callback_data="toggle_mirror")],            
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

@Client.on_callback_query(filters.regex("^toggle_change_index$"))
async def toggle_change_index_callback(_, callback_query):
    global CHANGE_INDEX_ENABLED

    CHANGE_INDEX_ENABLED = not CHANGE_INDEX_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_merge_video$"))
async def toggle_merge_video_callback(_, callback_query):
    global MERGE_ENABLED

    MERGE_ENABLED = not MERGE_ENABLED
    await update_settings_message(callback_query.message)
    
# Callback query handler for the "sunrises24_bot_updates" button
@Client.on_callback_query(filters.regex("^sunrises24_bot_updates$"))
async def sunrises24_bot_updates_callback(_, callback_query):
    await callback_query.answer("MADE BY @SUNRISES24BOTUPDATES ❤️", show_alert=True)    


async def update_settings_message(message):
    global METADATA_ENABLED, PHOTO_ATTACH_ENABLED, MIRROR_ENABLED, RENAME_ENABLED, REMOVETAGS_ENABLED, CHANGE_INDEX_ENABLED

    metadata_status = "✅ Enabled" if METADATA_ENABLED else "❌ Disabled"
    photo_attach_status = "✅ Enabled" if PHOTO_ATTACH_ENABLED else "❌ Disabled"
    mirror_status = "✅ Enabled" if MIRROR_ENABLED else "❌ Disabled"
    rename_status = "✅ Enabled" if RENAME_ENABLED else "❌ Disabled"
    removealltags_status = "✅ Enabled" if REMOVETAGS_ENABLED else "❌ Disabled"
    change_index_status = "✅ Enabled" if CHANGE_INDEX_ENABLED else "❌ Disabled"
    merge_video_status = "✅ Enabled" if MERGE_ENABLED else "❌ Disabled"    
      
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],            
            [InlineKeyboardButton(f"{rename_status} Change Rename 📝", callback_data="toggle_rename")],
            [InlineKeyboardButton(f"{removealltags_status} Remove All Tags 📛", callback_data="toggle_removealltags")],
            [InlineKeyboardButton(f"{metadata_status} Change Metadata ☄️", callback_data="toggle_metadata")],            
            [InlineKeyboardButton(f"{change_index_status} Change Index ♻️", callback_data="toggle_change_index")],
            [InlineKeyboardButton(f"{merge_video_status} Merge Video 🎞️", callback_data="toggle_merge_video")],
            [InlineKeyboardButton(f"{photo_attach_status} Attach Photo 🖼️", callback_data="toggle_photo_attach")],                        
            [InlineKeyboardButton(f"{multitask_status} Mirror 💽", callback_data="toggle_mirror")],            
            [InlineKeyboardButton("Close ❌", callback_data="del")],
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")]
        ]
    )

    await message.edit_text("Use inline buttons to manage your settings:", reply_markup=keyboard)




# Callback query handler for setting sample video duration
@Client.on_callback_query(filters.regex("^set_sample_video_duration_"))
async def set_sample_video_duration(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    duration_str = callback_query.data.split("_")[-1]
    duration = int(duration_str)
    user_settings[user_id] = user_settings.get(user_id, {})
    user_settings[user_id]["sample_video_duration"] = duration
    await callback_query.answer(f"Sample video duration set to {duration} seconds.")
    await display_user_settings(client, callback_query.message, edit=True)
  
# Callback query handler for selecting sample video option
@Client.on_callback_query(filters.regex("^sample_video_option$"))
async def sample_video_option(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_duration = user_settings.get(user_id, {}).get("sample_video_duration", "Not set")
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

@Client.on_message(filters.command("usersettings") & filters.chat(GROUP))
async def display_user_settings(client, msg, edit=False):
    user_id = msg.from_user.id
    current_duration = user_settings.get(user_id, {}).get("sample_video_duration", "Not set")
    current_screenshots = user_settings.get(user_id, {}).get("screenshots", "Not set")

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
    current_screenshots = user_settings.get(user_id, {}).get("screenshots", 5)  # Default to 5 if not set
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
    
    user_settings[user_id] = user_settings.get(user_id, {})
    user_settings[user_id]["screenshots"] = num_screenshots
    
    await callback_query.answer(f"Number of screenshots set to {num_screenshots}.")
    await display_user_settings(client, callback_query.message, edit=True)



# Inline query handler for previewing metadata titles
@Client.on_callback_query(filters.regex("^preview_metadata$"))
async def inline_preview_metadata_callback(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    titles = user_settings.get(user_id, {})
    if not titles or not any(titles.values()):
        await callback_query.message.reply_text("Metadata titles are not fully set. Please set all titles first.")
        return
    
    preview_text = f"Video Title: {titles.get('video_title', '')}\n" \
                   f"Audio Title: {titles.get('audio_title', '')}\n" \
                   f"Subtitle Title: {titles.get('subtitle_title', '')}"
    await callback_query.message.reply_text(f"Current Metadata Titles:\n\n{preview_text}")

# Inline query handler to preview the Gofile API key
@Client.on_callback_query(filters.regex("^preview_gofilekey$"))
async def inline_preview_gofile_api_key(bot, callback_query):
    user_id = callback_query.from_user.id
    
    # Check if the API key is set for the user
    if user_id not in user_gofile_api_keys:
        return await callback_query.message.reply_text(f"Gofile API key is not set for user `{user_id}`. Use /gofilesetup {{your_api_key}} to set it.")
    
    # Reply with the current API key for the user
    await callback_query.message.reply_text(f"Current Gofile API Key for user `{user_id}`: {user_gofile_api_keys[user_id]}")

# Inline query handler to preview the Google Drive folder ID
@Client.on_callback_query(filters.regex("^preview_gdrive$"))
async def inline_preview_gdrive(bot, callback_query):
    user_id = callback_query.from_user.id
    
    # Check if the Google Drive folder ID is set for the user
    if user_id not in user_gdrive_folder_ids:
        return await callback_query.message.reply_text(f"Google Drive Folder ID is not set for user `{user_id}`. Use /gdriveid {{your_gdrive_folder_id}} to set it.")
    
    # Reply with the current Google Drive folder ID for the user
    await callback_query.message.reply_text(f"Current Google Drive Folder ID for user `{user_id}`: {user_gdrive_folder_ids[user_id]}")
    

# Inline query handler for attaching photo
@Client.on_callback_query(filters.regex("^attach_photo$"))
async def inline_attach_photo_callback(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    user_settings[user_id] = user_settings.get(user_id, {})
    user_settings[user_id]["attach_photo"] = True
    await callback_query.message.edit_text("Please send a photo to be attached using the setphoto command.")

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24

# Inline query handler for previewing attached photo
@Client.on_callback_query(filters.regex("^preview_photo$"))
async def inline_preview_photo_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    attachment_path = os.path.join(DOWNLOAD_LOCATION, f"attachment_{user_id}.jpg")
    
    if not os.path.exists(attachment_path):
        await callback_query.message.reply_text("No photo has been attached yet.")
        return
    
    await callback_query.message.reply_photo(photo=attachment_path, caption="Attached Photo")



#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Inline query handler for thumbnail settings
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



# Command to set a permanent thumbnail
@Client.on_message(filters.command("setthumbnail") & filters.chat(GROUP))
async def set_thumbnail_command(client, message):
    user_id = message.from_user.id
    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{user_id}.jpg"

    # Check if thumbnail already exists
    if os.path.isfile(thumbnail_path):
        await message.reply("You already have a permanent thumbnail set. Send a new photo to update it.")
    else:
        await message.reply("Send a photo to set as your permanent thumbnail.")

# Handler for setting the thumbnail
@Client.on_message(filters.photo & filters.chat(GROUP))
async def set_thumbnail_handler(client, message):
    user_id = message.from_user.id
    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{user_id}.jpg"

    # Check if thumbnail already exists
    if os.path.isfile(thumbnail_path):
        # Thumbnail exists, delete the old one
        os.remove(thumbnail_path)

    # Download the photo and save as thumbnail_{user_id}.jpg
    await client.download_media(message=message, file_name=thumbnail_path)
    await message.reply("Your permanent thumbnail is updated. If the bot is restarted, the new thumbnail will be preserved.")

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_callback_query(filters.regex("^view_thumbnail$"))
async def view_thumbnail(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{user_id}.jpg"

    try:
        await callback_query.message.reply_photo(photo=thumbnail_path, caption="This is your current thumbnail")
    except Exception as e:
        await callback_query.message.reply_text("You don't have any thumbnail.")


@Client.on_callback_query(filters.regex("^delete_thumbnail$"))
async def delete_thumbnail(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{user_id}.jpg"

    try:
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            await callback_query.message.reply_text("Your thumbnail was removed ❌")
        else:
            await callback_query.message.reply_text("You don't have any thumbnail ‼️")
    except Exception as e:
        await callback_query.message.reply_text("An error occurred while trying to remove your thumbnail. Please try again later.")
      
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Inline query handler to return to user settings
@Client.on_callback_query(filters.regex("^back_to_settings$"))
async def back_to_settings_callback(client, callback_query: CallbackQuery):
    await display_user_settings(client, callback_query.message)

# Command to set metadata titles
@Client.on_message(filters.command("setmetadata") & filters.chat(GROUP))
async def set_metadata_command(client, msg):
    global user_settings  # Ensure we're modifying the global user_settings

    # Extract titles from the command message
    if len(msg.command) < 2:
        await msg.reply_text("Invalid command format. Use: setmetadata video_title | audio_title | subtitle_title")
        return
    
    titles = msg.text.split(" ", 1)[1].split(" | ")
    if len(titles) != 3:
        await msg.reply_text("Invalid number of titles. Use: setmetadata video_title | audio_title | subtitle_title")
        return
    
    # Store the titles in user_settings
    user_id = msg.from_user.id
    user_settings[user_id] = {
        "video_title": titles[0].strip(),
        "audio_title": titles[1].strip(),
        "subtitle_title": titles[2].strip()
    }
    
    await msg.reply_text("Metadata titles set successfully ✅.")

# Command handler for /gdriveid setup
@Client.on_message(filters.private & filters.command("gdriveid"))
async def setup_gdrive_id(bot, msg: Message):
    user_id = msg.from_user.id
    args = msg.text.split(" ", 1)
    if len(args) != 2:
        return await msg.reply_text("Usage: /gdriveid {your_gdrive_folder_id}")
    
    gdrive_folder_id = args[1].strip()
    user_gdrive_folder_ids[user_id] = gdrive_folder_id
    await msg.reply_text(f"Google Drive folder ID set to: {gdrive_folder_id} for user `{user_id}`\n\nGoogle Drive folder ID set successfully✅!")



# Command to set Gofile API key for a user
@Client.on_message(filters.command("gofilesetup") & filters.private)
async def set_gofile_api_key(bot, msg):
    user_id = msg.from_user.id
    args = msg.text.split(" ", 1)
    if len(args) != 2:
        return await msg.reply_text("Usage: /gofilesetup {your_api_key}")
    
    api_key = args[1].strip()
    user_gofile_api_keys[user_id] = api_key
    await msg.reply_text("Your Gofile API key has been set successfully✅.")


# Command handler for /mirror
@Client.on_message(filters.command("mirror") & filters.chat(GROUP))
async def mirror_to_google_drive(bot, msg: Message):
    global MIRROR_ENABLED
        
    if not MIRROR_ENABLED:
        return await msg.reply_text("The mirror feature is currently disabled.")

    user_id = msg.from_user.id
    
    # Retrieve the user's Google Drive folder ID
    gdrive_folder_id = user_gdrive_folder_ids.get(user_id)
    
    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    reply = msg.reply_to_message
    if len(msg.command) < 2 or not reply:
        return await msg.reply_text("Please reply to a file with the new filename and extension.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a file with the new filename and extension.")

    new_name = msg.text.split(" ", 1)[1]
    download_path = os.path.join(DOWNLOAD_LOCATION, new_name)

    try:
        # Show progress message for downloading
        sts = await msg.reply_text("🚀 Downloading...")
        
        # Download the file
        downloaded_file = await bot.download_media(message=reply, file_name=download_path, progress=progress_message, progress_args=("Downloading", sts, time.time()))
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
            f"File successfully Mirror and Uploaded to Google Drive!\n\n"
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
@Client.on_message(filters.command("rename") & filters.chat(GROUP))
async def rename_file(bot, msg):
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

    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"
    og_thumbnail = None
    if os.path.exists(thumbnail_path):
        og_thumbnail = thumbnail_path
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                og_thumbnail = await bot.download_media(media.thumbs[0].file_id, file_name=thumbnail_path)
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
    if og_thumbnail and os.path.exists(og_thumbnail):
        os.remove(og_thumbnail)
    await sts.delete()

#Change Metadata Code
@Client.on_message(filters.command("changemetadata") & filters.chat(GROUP))
async def change_metadata(bot, msg):
    global METADATA_ENABLED, user_settings

    if not METADATA_ENABLED:
        return await msg.reply_text("Metadata changing feature is currently disabled.")

    user_id = msg.from_user.id
    if user_id not in user_settings or not any(user_settings[user_id].values()):
        return await msg.reply_text("Metadata titles are not set. Please set metadata titles using `/setmetadata video_title audio_title subtitle_title`.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the metadata command\nFormat: `changemetadata -n filename.mkv`")

    if len(msg.command) < 3 or msg.command[1] != "-n":
        return await msg.reply_text("Please provide the filename with the `-n` flag\nFormat: `changemetadata -n filename.mkv`")

    output_filename = " ".join(msg.command[2:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    video_title = user_settings[user_id]['video_title']
    audio_title = user_settings[user_id]['audio_title']
    subtitle_title = user_settings[user_id]['subtitle_title']

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

    output_file = os.path.join(DOWNLOAD_LOCATION, output_filename)

    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error changing metadata: {e}")
        os.remove(downloaded)
        return

    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"
    if not os.path.exists(thumbnail_path):
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=thumbnail_path)
        except Exception as e:
            file_thumb = None
    else:
        file_thumb = thumbnail_path

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
@Client.on_message(filters.command("attachphoto") & filters.chat(GROUP))
async def attach_photo(bot, msg):
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

    attachment_path = f"{DOWNLOAD_LOCATION}/attachment_{msg.from_user.id}.jpg"
    if not os.path.exists(attachment_path):
        await safe_edit_message(sts, "Please send a photo to be attached using the `setphoto` command.")
        os.remove(downloaded)
        return

    output_file = os.path.join(DOWNLOAD_LOCATION, output_filename)

    await safe_edit_message(sts, "💠 Adding photo attachment... ⚡")
    try:
        add_photo_attachment(downloaded, attachment_path, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error adding photo attachment: {e}")
        os.remove(downloaded)
        return

    file_thumb = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"
    if not os.path.exists(file_thumb):
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=file_thumb)
        except Exception as e:
            print(e)
            file_thumb = None

    filesize = os.path.getsize(output_file)

    await safe_edit_message(sts, "🔼 Uploading modified file... ⚡")
    try:
        # Upload to Google Drive if file size exceeds the limit
        if filesize > FILE_SIZE_LIMIT:
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

#changeindexaudio
# Command to change index audio
@Client.on_message(filters.command("changeindexaudio") & filters.chat(GROUP))
async def change_index_audio(bot, msg):
    global CHANGE_INDEX_ENABLED

    if not CHANGE_INDEX_ENABLED:
        return await msg.reply_text("The changeindexaudio feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `/changeindexaudio a-3 -n filename.mkv` (Audio)")

    if len(msg.command) < 3:
        return await msg.reply_text("Please provide the index command with a filename\nFormat: `/changeindexaudio a-3 -n filename.mkv` (Audio)")

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
        return await msg.reply_text("Invalid format. Use `/changeindexaudio a-3 -n filename.mkv` for audio.")

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

    output_file = os.path.join(DOWNLOAD_LOCATION, output_filename)

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
        return

    # Thumbnail handling
    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"

    if os.path.exists(thumbnail_path):
        file_thumb = thumbnail_path
    else:
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=thumbnail_path)
        except Exception as e:
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
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡️", sts, c_time)
            )
        except Exception as e:
            return await sts.edit(f"Error: {e}")

    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()

#changeindex subtitles 
# Command to change index subtitle
@Client.on_message(filters.command("Changeindexsub") & filters.chat(GROUP))
async def change_index_subtitle(bot, msg):
    global CHANGE_INDEX_ENABLED

    if not CHANGE_INDEX_ENABLED:
        return await msg.reply_text("The changeindexsub feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `/changeindexsub s-3 -n filename.mkv` (Subtitle)")

    if len(msg.command) < 3:
        return await msg.reply_text("Please provide the index command with a filename\nFormat: `/changeindexsub s-3 -n filename.mkv` (Subtitle)")

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
        return await msg.reply_text("Invalid format. Use `/changeindexsub s-3 -n filename.mkv` for subtitles.")

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

    output_file = os.path.join(DOWNLOAD_LOCATION, output_filename)

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
    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"

    if os.path.exists(thumbnail_path):
        file_thumb = thumbnail_path
    else:
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=thumbnail_path)
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
            f"**File successfully changed subtitle index and uploaded to Google Drive!**\n\n"
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




#merge command 
# Command to start merging files
@Client.on_message(filters.command("merge") & filters.chat(GROUP))
async def start_merge_command(bot, msg: Message):
    global MERGE_ENABLED
    if not MERGE_ENABLED:
        return await msg.reply_text("The merge feature is currently disabled.")

    user_id = msg.from_user.id
    merge_state[user_id] = {"files": [], "output_filename": None}

    await msg.reply_text("Send up to 10 video/document files one by one. Once done, send `/videomerge filename`.")

# Command to finalize merging and start the process
@Client.on_message(filters.command("videomerge") & filters.chat(GROUP))
async def start_video_merge_command(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id not in merge_state or not merge_state[user_id]["files"]:
        return await msg.reply_text("No files received for merging. Please send files using /merge command first.")

    output_filename = msg.text.split(' ', 1)[1].strip()  # Extract output filename from command
    merge_state[user_id]["output_filename"] = output_filename

    await merge_and_upload(bot, msg)

# Handling media files sent by users
@Client.on_message(filters.document | filters.video & filters.chat(GROUP))
async def handle_media_files(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id in merge_state and len(merge_state[user_id]["files"]) < 10:
        merge_state[user_id]["files"].append(msg)
        await msg.reply_text("File received. Send another file or use `/videomerge filename` to start merging.")


# Function to merge and upload files
async def merge_and_upload(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id not in merge_state:
        return await msg.reply_text("No merge state found for this user. Please start the merge process again.")

    files_to_merge = merge_state[user_id]["files"]
    output_filename = merge_state[user_id].get("output_filename", "merged_output.mp4")  # Default output filename
    output_path = os.path.join(DOWNLOAD_LOCATION, output_filename)

    sts = await msg.reply_text("🚀 Starting merge process...")

    try:
        file_paths = []
        for file_msg in files_to_merge:
            file_path = await download_media(file_msg, sts)
            file_paths.append(file_path)

        input_file = os.path.join(DOWNLOAD_LOCATION, "input.txt")
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
        thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{user_id}.jpg"
        file_thumb = None
        if os.path.exists(thumbnail_path):
            file_thumb = thumbnail_path
        else:
            try:
                if "thumbs" in msg and msg.thumbs:
                    file_thumb = await bot.download_media(msg.thumbs[0].file_id, file_name=thumbnail_path)
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

#leech command 
# Leech Handler Only Auth Users
@Client.on_message(filters.command("leech") & filters.chat(AUTH_USERS))
async def linktofile(bot, msg: Message):
    reply = msg.reply_to_message
    if len(msg.command) < 2 or not reply:
        return await msg.reply_text("Please reply to a file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

    new_name = msg.text.split(" ", 1)[1]
    if not new_name.endswith(".mkv"):
        return await msg.reply_text("Please specify a filename ending with .mkv.")

    media = reply.document or reply.audio or reply.video
    if not media and not reply.text:
        return await msg.reply_text("Please reply to a valid file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

    if reply.text and ("seedr" in reply.text or "workers" in reply.text):
        await handle_link_download(bot, msg, reply.text, new_name, media)
    else:
        if not media:
            return await msg.reply_text("Please reply to a valid file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

        sts = await msg.reply_text("🚀 Downloading...")
        c_time = time.time()
        try:
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started...", sts, c_time))
        except RPCError as e:
            return await sts.edit(f"Download failed: {e}")

        filesize = os.path.getsize(downloaded)
        filesize_human = humanbytes(filesize)

        if CAPTION:
            try:
                cap = CAPTION.format(file_name=new_name, file_size=filesize_human)
            except Exception as e:
                return await sts.edit(text=f"Your caption has an error: unexpected keyword ({e})")
        else:
            cap = f"{new_name}\n\n🌟 Size: {filesize_human}"

        # Thumbnail handling
        thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"
        file_thumb = None
        if media and media.thumbs:
            if not os.path.exists(thumbnail_path):
                try:
                    file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=thumbnail_path)
                except Exception as e:
                    print(f"Error downloading thumbnail: {e}")

        await edit_message(sts, "💠 Uploading...")
        c_time = time.time()

        if filesize > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(downloaded, new_name, sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"**File successfully uploaded to Google Drive!**\n\n"
                f"**Google Drive Link**: [View File]({file_link})\n\n"
                f"**Uploaded File**: {new_name}\n"
                f"**Request User:** {msg.from_user.mention}\n\n"
                f"**Size**: {filesize_human}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            try:
                await bot.send_document(msg.chat.id, document=downloaded, thumb=file_thumb, caption=cap, progress=progress_message, progress_args=("💠 Upload Started...", sts, c_time))
            except ValueError as e:
                return await sts.edit(f"Upload failed: {e}")
            except TimeoutError as e:
                return await sts.edit(f"Upload timed out: {e}")

        try:
            if file_thumb and os.path.exists(file_thumb):
                os.remove(file_thumb)
            if os.path.exists(downloaded):
                os.remove(downloaded)
        except Exception as e:
            print(f"Error deleting files: {e}")
        await sts.delete()

async def handle_link_download(bot, msg: Message, link: str, new_name: str, media):
    sts = await msg.reply_text("🚀 Downloading from link...")
    c_time = time.time()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status == 200:
                    with open(new_name, 'wb') as f:
                        f.write(await resp.read())
                else:
                    await sts.edit(f"Failed to download file from link. Status code: {resp.status}")
                    return
    except Exception as e:
        await sts.edit(f"Error during download: {e}")
        return

    if not os.path.exists(new_name):
        await sts.edit("File not found after download. Please check the link and try again.")
        return

    filesize = os.path.getsize(new_name)
    filesize_human = humanbytes(filesize)
    cap = f"{new_name}\n\n🌟 Size: {filesize_human}"

    # Thumbnail handling
    thumbnail_path = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"
    file_thumb = None
    if media and media.thumbs:
        if not os.path.exists(thumbnail_path):
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=thumbnail_path)
            except Exception as e:
                print(f"Error downloading thumbnail: {e}")

    await edit_message(sts, "💠 Uploading...")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(new_name, new_name, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**Leech File successfully uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {new_name}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(msg.chat.id, document=new_name, thumb=file_thumb, caption=cap, progress=progress_message, progress_args=("💠 Upload Started...", sts, c_time))
        except ValueError as e:
            return await sts.edit(f"Upload failed: {e}")
        except TimeoutError as e:
            return await sts.edit(f"Upload timed out: {e}")

    try:
        if file_thumb:
            os.remove(file_thumb)
        os.remove(new_name)
    except Exception as e:
        print(f"Error deleting file: {e}")
    await sts.delete()

async def edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text)
    except MessageNotModified:
        pass


#Removetags command 
async def safe_edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text)
    except Exception as e:
        print(f"Failed to edit message: {e}")

@Client.on_message(filters.command("removetags") & filters.chat(GROUP))
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

    cleaned_file = os.path.join(DOWNLOAD_LOCATION, new_filename if new_filename else "cleaned_" + os.path.basename(downloaded))

    await safe_edit_message(sts, "💠 Removing all tags... ⚡")
    try:
        remove_all_tags(downloaded, cleaned_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error removing all tags: {e}")
        os.remove(downloaded)
        return

    file_thumb = f"{DOWNLOAD_LOCATION}/thumbnail_{msg.from_user.id}.jpg"
    if not os.path.exists(file_thumb):
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=file_thumb)
        except Exception as e:
            print(e)
            file_thumb = None

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
                f"┏📥 **File Name:** {new_filename if new_filename else os.path.basename(cleaned_file)}\n"
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


#Screenshots Command
@Client.on_message(filters.command("screenshots") & filters.chat(GROUP))
async def screenshots_command(client, message: Message):
    user_id = message.from_user.id
    num_screenshots = user_settings.get(user_id, {}).get("screenshots", 5)  # Default to 5 if not set

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
        screenshot_path = os.path.join(DOWNLOAD_LOCATION1, f"screenshot_{i}.jpg")

        os.makedirs(DOWNLOAD_LOCATION1, exist_ok=True)

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

    await sts.edit(f"💠 Uploading {num_screenshots} screenshots to your PM... ⚡")
    for i, screenshot_path in enumerate(screenshot_paths):
        try:
            await client.send_photo(chat_id=user_id, photo=screenshot_path)
        except Exception as e:
            await sts.edit(f"Error uploading screenshot {i+1}: {e}")
            os.remove(screenshot_path)

    os.remove(input_path)
    for screenshot_path in screenshot_paths:
        os.remove(screenshot_path)

    # Send notification in group chat
    try:
        await message.reply_text("📸 Screenshots have been sent to your PM.")
    except Exception as e:
        print(f"Failed to send notification: {e}")
    await sts.delete()

#Sample Video Command
@Client.on_message(filters.command("samplevideo") & filters.chat(GROUP))
async def sample_video(bot, msg):
    user_id = msg.from_user.id
    duration = user_settings.get(user_id, {}).get("sample_video_duration", 0)
    if duration == 0:
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

    output_file = os.path.join(DOWNLOAD_LOCATION, f"sample_video_{duration}s.mp4")

    await sts.edit("🚀 Processing sample video... ⚡")
    try:
        generate_sample_video(input_path, duration, output_file)
    except Exception as e:
        await sts.edit(f"Error generating sample video: {e}")
        os.remove(input_path)
        return

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟 Size: {filesize_human}"

    user_id = msg.from_user.id  # Get the user ID of the sender
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
        # Send notification about the file upload
        await msg.reply_text(f"File Sample Video has been uploaded to your PM. Check your PM of the bot ✅ .")

    except Exception as e:
        await sts.edit(f"Error uploading sample video: {e}")
        return

    os.remove(input_path)
    os.remove(output_file)
    await sts.delete()



 # Define restart_app command
@Client.on_message(filters.command("restart") & filters.chat(AUTH_USERS))
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
        

# Unzip file command handler
@Client.on_message(filters.command("unzip") & filters.chat(GROUP))
async def unzip(bot, msg):
    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a zip file to unzip.")

    media = msg.reply_to_message.document
    if not media:
        return await msg.reply_text("Please reply to a valid zip file.")

    sts = await msg.reply_text("🚀Downloading file...⚡")
    c_time = time.time()
    input_path = await bot.download_media(media, progress
                                          =progress_message, progress_args=("🚀Downloading file...⚡️", sts, c_time))

    if not os.path.exists(input_path):
        await sts.edit(f"Error: The downloaded file does not exist.")
        return

    extract_path = os.path.join(DOWNLOAD_LOCATION, "extracted")
    os.makedirs(extract_path, exist_ok=True)

    await sts.edit("🚀Unzipping file...⚡")
    extracted_files = unzip_file(input_path, extract_path)

    if extracted_files:
        await sts.edit(f"✅ File unzipped successfully. Uploading extracted files...⚡")
        await upload_files(bot, msg.chat.id, extract_path)
        await sts.edit(f"✅ All extracted files uploaded successfully.")
    else:
        await sts.edit(f"❌ Failed to unzip file.")

    os.remove(input_path)
    shutil.rmtree(extract_path)
  
# Handler for setting the photo with user ID
@Client.on_message(filters.command("setphoto") & filters.chat(GROUP))
async def set_photo(bot, msg):
    reply = msg.reply_to_message
    if not reply or not reply.photo:
        return await msg.reply_text("Please reply to a photo with the set photo command")

    user_id = msg.from_user.id
    photo = reply.photo
    attachment_path = os.path.join(DOWNLOAD_LOCATION, f"attachment_{user_id}.jpg")
    try:
        await bot.download_media(photo, attachment_path)
        await msg.reply_text(f"Photo saved successfully as `{attachment_path}`.")
    except Exception as e:
        await msg.reply_text(f"Error saving photo: {e}")

# Command to upload to Gofile
@Client.on_message(filters.command("gofile") & filters.chat(GROUP))
async def gofile_upload(bot, msg: Message):
    user_id = msg.from_user.id
    
    # Retrieve the user's Gofile API key or fallback to the global key
    gofile_api_key = user_gofile_api_keys.get(user_id, GOFILE_API_KEY)

    if not gofile_api_key:
        return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it or ensure a global key is set.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a file or video to upload to Gofile.")

    media = reply.document or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid file or video.")

    args = msg.text.split(" ", 1)
    if len(args) == 2:
        custom_name = args[1]
    else:
        custom_name = media.file_name

    sts = await msg.reply_text("🚀 Uploading to Gofile...")
    c_time = time.time()
    
    downloaded_file = None

    try:
        async with aiohttp.ClientSession() as session:
            # Get the server to upload the file
            async with session.get("https://api.gofile.io/getServer") as resp:
                if resp.status != 200:
                    return await sts.edit(f"Failed to get server. Status code: {resp.status}")

                data = await resp.json()
                server = data["data"]["server"]

            # Download the media file
            downloaded_file = await bot.download_media(
                media,
                file_name=os.path.join(DOWNLOAD_LOCATION, custom_name),
                progress=progress_message,
                progress_args=("🚀 Download Started...", sts, c_time)
            )

            # Upload the file to Gofile
            with open(downloaded_file, "rb") as file:
                form_data = aiohttp.FormData()
                form_data.add_field("file", file, filename=custom_name)
                form_data.add_field("token", gofile_api_key)

                async with session.post(
                    f"https://{server}.gofile.io/uploadFile",
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

@Client.on_message(filters.command("clone") & filters.chat(GROUP))
async def clone_file(bot, msg: Message):
    global GDRIVE_FOLDER_ID

    if not GDRIVE_FOLDER_ID:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    if len(msg.command) < 2:
        return await msg.reply_text("Please specify the Google Drive file URL.")

    src_url = msg.text.split(" ", 1)[1]
    src_id = extract_id_from_url(src_url)

    if not src_id:
        return await msg.reply_text("Invalid Google Drive URL. Please provide a valid file URL.")

    sts = await msg.reply_text("Starting cloning process...")

    try:
        copied_file_info = await copy_file(src_id, GDRIVE_FOLDER_ID)
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


async def safe_edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text[:4096])  # Ensure text does not exceed 4096 characters
    except Exception as e:
        print(f"Failed to edit message: {e}")


@Client.on_message(filters.command("extractaudios") & filters.chat(GROUP))
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

def extract_audio_stream(input_path, output_path, stream_index):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-map', f'0:{stream_index}',
        '-c', 'copy',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")

def extract_audios_from_file(input_path):
    video_streams_data = ffmpeg.probe(input_path)
    audios = [stream for stream in video_streams_data.get("streams") if stream.get("codec_type") == "audio"]

    extracted_files = []
    for audio in audios:
        codec_name = audio.get('codec_name', 'aac')
        output_file = os.path.join(os.path.dirname(input_path), f"{audio['index']}.{codec_name}")
        extract_audio_stream(input_path, output_file, audio['index'])
        extracted_files.append((output_file, audio))

    return extracted_files

@Client.on_message(filters.command("extractsubtitles") & filters.chat(GROUP))
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

def extract_subtitle_stream(input_path, output_path, stream_index):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-map', f'0:{stream_index}',
        '-c', 'copy',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")

def extract_subtitles_from_file(input_path):
    video_streams_data = ffmpeg.probe(input_path)
    subtitles = [stream for stream in video_streams_data.get("streams") if stream.get("codec_type") == "subtitle"]

    extracted_files = []
    for subtitle in subtitles:
        output_file = os.path.join(os.path.dirname(input_path), f"{subtitle['index']}.{subtitle['codec_type']}.srt")
        extract_subtitle_stream(input_path, output_file, subtitle['index'])
        extracted_files.append((output_file, subtitle))

    return extracted_files


@Client.on_message(filters.command("extractvideo") & filters.chat(GROUP))
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

def extract_video_stream(input_path, output_path, stream_index, codec_name):
    temp_output = f"{output_path}.{codec_name}"  # Temporary output file
    command = [
        'ffmpeg',
        '-i', input_path,
        '-map', f'0:{stream_index}',
        '-c', 'copy',
        temp_output,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")

    # Convert to .mkv or .mp4
    mkv_output = f"{output_path}.mkv"
    mp4_output = f"{output_path}.mp4"
    command_mkv = [
        'ffmpeg',
        '-i', temp_output,
        '-c', 'copy',
        mkv_output,
        '-y'
    ]
    command_mp4 = [
        'ffmpeg',
        '-i', temp_output,
        '-c', 'copy',
        mp4_output,
        '-y'
    ]

    process_mkv = subprocess.Popen(command_mkv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_mkv, stderr_mkv = process_mkv.communicate()
    process_mp4 = subprocess.Popen(command_mp4, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_mp4, stderr_mp4 = process_mp4.communicate()

    if process_mkv.returncode != 0 and process_mp4.returncode != 0:
        raise Exception(f"FFmpeg error during conversion: {stderr_mkv.decode('utf-8')} {stderr_mp4.decode('utf-8')}")

    os.remove(temp_output)  # Remove temporary file
    return mkv_output if process_mkv.returncode == 0 else mp4_output

def extract_video_from_file(input_path):
    video_streams_data = ffmpeg.probe(input_path)
    video_streams = [stream for stream in video_streams_data.get("streams") if stream.get("codec_type") == "video"]

    if not video_streams:
        return None

    video_stream = video_streams[0]  # Assuming we extract the first video stream found
    codec_name = video_stream['codec_name']
    output_file = os.path.join(os.path.dirname(input_path), f"{video_stream['index']}")
    output_file = extract_video_stream(input_path, output_file, video_stream['index'], codec_name)

    return output_file


# Command handler for /list
@Client.on_message(filters.command("list") & filters.chat(GROUP))
async def list_files(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID
    gdrive_folder_id = user_gdrive_folder_ids.get(user_id)
    
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

# Command handler for /clean
@Client.on_message(filters.command("clean") & filters.chat(GROUP))
async def clean_files_by_name(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID
    gdrive_folder_id = user_gdrive_folder_ids.get(user_id)
    
    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    try:
        # Extract file name from the command
        command_parts = msg.text.split(maxsplit=1)
        if len(command_parts) < 2:
            return await msg.reply_text("Please provide a file name to clean.")

        file_name = command_parts[1].strip()

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


if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
