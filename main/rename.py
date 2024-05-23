import os
import time
import shutil
import zipfile
import tarfile
import requests
from pyrogram.types import Message
from pyrogram.types import Document, Video
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import MessageNotModified
from config import DOWNLOAD_LOCATION, CAPTION
from main.utils import progress_message, humanbytes
import subprocess
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import GROUP
from pyrogram.errors import FloodWait, RPCError
from pyrogram.session import Session



# Constants
FILE_SIZE_LIMIT = 2097152000  # 2GB

# Config class to hold your configurations
class Config:
    STRING_SESSION = "BQCk-AgAXjv-rvP8Q3ZK7uVQ4bc6maTPaqtZ6iFqJDxWELtFu74RHoIvXfn6dLPZ9b1u9fWlV4ZqFJmWKm4jXrbw_LzfAeuYLbiFgdAcZ-mKa22oeHOZuN2iFFYzKCeDBOA4ZgJX74pQo8EliICqLxXI7Jo3gOPElzU3O11CS4kxFMGylSW_vSW9v6lTimUGXz4aW6Te-VkWLUmzQrvOiWaObizOe_y1dK3CXwNfCp0mzh1cDbTmGpAiHG5ShRC4Du2sAPudcnobX9hrPRKp5Ly0M0AOVnpJtKfh1zyOzDWjwoY9qA97hoyd1ITfNg8ZBHHe3a_2gKh2Lj85OWNANgL8doeABAAAAAGBoJ6aAA"

# Helper function to convert bytes to a human-readable format
def humanbytes(size):
    return f"{size / (1024 * 1024):.2f} MB"

# Initialize the string session client
string_session_client = Client("my_session", api_id="10811400", api_hash="191bf5ae7a6c39771e7b13cf4ffd1279", session_string=Config.STRING_SESSION)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Rename Command
@Client.on_message(filters.command("rename") & filters.chat(GROUP))
async def rename_file(bot, msg):
    reply = msg.reply_to_message
    if len(msg.command) < 2 or not reply:
        return await msg.reply_text("Please Reply To A File, Video, or Audio With filename + .extension (e.g., `.mkv`, `.mp4`, or `.zip`)")
    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please Reply To A File, Video, or Audio With filename + .extension (e.g., `.mkv`, `.mp4`, or `.zip`)")
    
    og_media = getattr(reply, reply.media.value)
    new_name = msg.text.split(" ", 1)[1]
    sts = await msg.reply_text("🚀Downloading.....⚡")
    c_time = time.time()
    downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀Download Started...⚡️", sts, c_time))
    filesize = humanbytes(og_media.file_size)
    
    if CAPTION:
        try:
            cap = CAPTION.format(file_name=new_name, file_size=filesize)
        except Exception as e:
            return await sts.edit(text=f"Your caption has an error: unexpected keyword ●> ({e})")
    else:
        cap = f"{new_name}\n\n🌟size : {filesize}"

    # Thumbnail handling
    dir = os.listdir(DOWNLOAD_LOCATION)
    if len(dir) == 0:
        file_thumb = await bot.download_media(og_media.thumbs[0].file_id)
        og_thumbnail = file_thumb
    else:
        try:
            og_thumbnail = f"{DOWNLOAD_LOCATION}/thumbnail.jpg"
        except Exception as e:
            print(e)
            og_thumbnail = None

    await sts.edit("💠Uploading...⚡")
    c_time = time.time()
    try:
        await bot.send_document(msg.chat.id, document=downloaded, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠Upload Started.....", sts, c_time))
    except Exception as e:
        return await sts.edit(f"Error {e}")
    
    try:
        if file_thumb:
            os.remove(file_thumb)
        os.remove(downloaded)
    except:
        pass
    await sts.delete()

@Client.on_message(filters.command("rename"))
async def rename_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)     
    
# Change Index Command
@Client.on_message(filters.command("changeindex") & filters.chat(GROUP))
async def change_index(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `a-3-1-2` (Audio)")

    if len(msg.command) < 2:
        return await msg.reply_text("Please provide the index command\nFormat: `a-3-1-2` (Audio)")

    index_cmd = msg.command[1].strip().lower()
    if not index_cmd.startswith("a-"):
        return await msg.reply_text("Invalid format. Use `a-3-1-2` for audio.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the index command.")

    sts = await msg.reply_text("🚀Downloading media...⚡")
    c_time = time.time()
    downloaded = await reply.download(progress=progress_message, progress_args=("🚀Download Started...⚡️", sts, c_time))

    output_file = os.path.join(DOWNLOAD_LOCATION, "output_" + os.path.basename(downloaded))
    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', output_file, '-y'])

    await sts.edit("💠Changing indexing...⚡")
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        await sts.edit(f"❗FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        return

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟Size: {filesize_human}"

    await sts.edit("💠Uploading...⚡")
    c_time = time.time()
    try:
        await bot.send_document(msg.chat.id, document=output_file, caption=cap, progress=progress_message, progress_args=("💠Upload Started.....", sts, c_time))
    except Exception as e:
        return await sts.edit(f"Error {e}")

    os.remove(downloaded)
    os.remove(output_file)
    await sts.delete()

@Client.on_message(filters.command("changeindex"))
async def changeindex_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)     
    
def change_video_metadata(input_path, video_title, audio_title, subtitle_title, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-metadata', f'title={video_title}',
        '-metadata:s:v', f'title={video_title}',
        '-metadata:s:a', f'title={audio_title}',
        '-metadata:s:s', f'title={subtitle_title}',
        '-map', '0:v?',
        '-map', '0:a?',
        '-map', '0:s?',
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-c:s', 'copy',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")

@Client.on_message(filters.command("changemetadata") & filters.chat(GROUP))
async def change_metadata(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the metadata command\nFormat: `changemetadata video_title | audio_title | subtitle_title`")

    if len(msg.command) < 2:
        return await msg.reply_text("Please provide the new titles\nFormat: `changemetadata video_title | audio_title | subtitle_title`")

    titles = " ".join(msg.command[1:]).strip().split('|')
    if len(titles) != 3:
        return await msg.reply_text("Please provide all three titles separated by '|'\nFormat: `changemetadata video_title | audio_title | subtitle_title`")

    video_title, audio_title, subtitle_title = titles
    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the metadata command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    output_file = os.path.join(DOWNLOAD_LOCATION, "output_" + os.path.basename(downloaded))

    await sts.edit("💠 Changing metadata... ⚡")
    try:
        change_video_metadata(downloaded, video_title.strip(), audio_title.strip(), subtitle_title.strip(), output_file)
    except Exception as e:
        await sts.edit(f"Error changing metadata: {e}")
        os.remove(downloaded)
        return

    await sts.edit("🔼 Uploading modified file... ⚡")
    try:
        await bot.send_document(msg.chat.id, output_file, caption="Here is your file with updated metadata.")
        await sts.delete()
    except Exception as e:
        await sts.edit(f"Error uploading modified file: {e}")
    finally:
        os.remove(downloaded)
        os.remove(output_file)

@Client.on_message(filters.command("changemetadata"))
async def metadata_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)     
    
 # Sample Video Generation Function
def generate_sample_video(input_path, duration, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-t', str(duration),
        '-c:v', 'copy',
        '-c:a', 'copy',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")

# Sample Video Handler
@Client.on_message(filters.command(["samplevideo150", "samplevideo120", "samplevideo90", "samplevideo60", "samplevideo30"]) & filters.chat(GROUP))
async def sample_video(bot, msg):
    durations = {
        "samplevideo150": 150,
        "samplevideo120": 120,
        "samplevideo90": 90,
        "samplevideo60": 60,
        "samplevideo30": 30
    }
    duration = durations.get(msg.command[0], 0)
    if duration == 0:
        return await msg.reply_text("Invalid command")

    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a valid video file or document.")

    media = msg.reply_to_message.video or msg.reply_to_message.document
    if not media:
        return await msg.reply_text("Please reply to a valid video file or document.")

    sts = await msg.reply_text("🚀Downloading media...⚡")
    c_time = time.time()
    input_path = await bot.download_media(media, progress=progress_message, progress_args=("🚀Downloading media...⚡️", sts, c_time))
    output_file = os.path.join(DOWNLOAD_LOCATION, f"sample_video_{duration}s.mp4")

    await sts.edit("🚀Processing sample video...⚡")
    try:
        generate_sample_video(input_path, duration, output_file)
    except Exception as e:
        await sts.edit(f"Error generating sample video: {e}")
        os.remove(input_path)
        return

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟Size: {filesize_human}"

    await sts.edit("💠Uploading sample video...⚡")
    c_time = time.time()
    try:
        await bot.send_document(msg.chat.id, document=output_file, caption=cap, progress=progress_message, progress_args=("💠Upload Started.....", sts, c_time))
    except Exception as e:
        return await sts.edit(f"Error {e}")

    os.remove(input_path)
    os.remove(output_file)
    await sts.delete()       

@Client.on_message(filters.command(["samplevideo150", "samplevideo120", "samplevideo90", "samplevideo60", "samplevideo30"]))
async def samplevideo_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)     
    
# Screenshots by Number Handler
@Client.on_message(filters.command("screenshots") & filters.chat(GROUP))
async def screenshots(bot, msg):
    if len(msg.command) != 2:
        return await msg.reply_text("Please provide the number of screenshots to generate.")
    
    try:
        num_screenshots = int(msg.command[1])
        if num_screenshots <= 0:
            return await msg.reply_text("Number of screenshots must be a positive integer.")
    except ValueError:
        return await msg.reply_text("Please provide a valid number of screenshots.")

    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a valid video file or document.")
    
    media = msg.reply_to_message.video or msg.reply_to_message.document
    if not media:
        return await msg.reply_text("Please reply to a valid video file.")

    sts = await msg.reply_text("🚀Downloading media...⚡")
    c_time = time.time()
    input_path = await bot.download_media(media, progress=progress_message, progress_args=("🚀Downloading media...⚡️", sts, c_time))

    if not os.path.exists(input_path):
        await sts.edit(f"Error: The downloaded file does not exist.")
        return

    try:
        await sts.edit("🚀Reading video duration...⚡")
        command = [
            'ffprobe', '-i', input_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'
        ]
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

    await sts.edit("🚀Generating screenshots... It's Take Time 5Min for 10 Screenshots⚡")
    screenshot_paths = []
    for i in range(num_screenshots):
        time_position = interval * i
        screenshot_path = os.path.join(DOWNLOAD_LOCATION, f"screenshot_{i}.jpg")
        command = [
            'ffmpeg', '-i', input_path, '-ss', str(time_position), '-vframes', '1', screenshot_path, '-y'
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            await sts.edit(f"Error generating screenshot {i+1}: {stderr.decode('utf-8')}")
            os.remove(input_path)
            for path in screenshot_paths:
                os.remove(path)
            return
        screenshot_paths.append(screenshot_path)

    await sts.edit("💠Uploading screenshots...⚡")
    for i, screenshot_path in enumerate(screenshot_paths):
        try:
            await bot.send_photo(msg.chat.id, photo=screenshot_path)
        except Exception as e:
            await sts.edit(f"Error uploading screenshot {i+1}: {e}")
            os.remove(screenshot_path)

    os.remove(input_path)
    for screenshot_path in screenshot_paths:
        os.remove(screenshot_path)
    await sts.delete()

@Client.on_message(filters.command("screenshots"))
async def screenshots_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)     
    
# Function to unzip files
def unzip_file(file_path, extract_path):
    extracted_files = []
    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
                extracted_files = zip_ref.namelist()
        # Add support for other archive formats here if needed
    except Exception as e:
        print(f"Error unzipping file: {e}")
    return extracted_files

# Recursive function to upload files
async def upload_files(bot, chat_id, directory, base_path=""):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            try:
                await bot.send_document(chat_id, document=item_path, caption=item)
            except Exception as e:
                print(f"Error uploading {item}: {e}")
        elif os.path.isdir(item_path):
            await upload_files(bot, chat_id, item_path, base_path=os.path.join(base_path, item))

# Unzip file command handler
@Client.on_message(filters.command("unzip") & filters.chat(GROUP))
async def unzip(bot, msg):
    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file to unzip.")

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

@Client.on_message(filters.command("unzip"))
async def unzip_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)    


def add_photo_attachment(input_path, attachment_path, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-map', '0:v?',
        '-map', '0:a?',
        '-map', '0:s?',
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-c:s', 'copy',
        '-attach', attachment_path,
        '-metadata:s:t', 'mimetype=image/jpeg',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")

@Client.on_message(filters.command("attachphoto") & filters.chat(GROUP))
async def attach_photo(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the attach photo command")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the attach photo command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    # Check if there is a previously set photo
    attachment_path = os.path.join(DOWNLOAD_LOCATION, "attachment.jpg")
    if not os.path.exists(attachment_path):
        await sts.edit("Please send a photo to be attached using the `setphoto` command.")
        os.remove(downloaded)
        return

    output_file = os.path.join(DOWNLOAD_LOCATION, "output_" + os.path.basename(downloaded))

    await sts.edit("💠 Adding photo attachment... ⚡")
    try:
        add_photo_attachment(downloaded, attachment_path, output_file)
    except Exception as e:
        await sts.edit(f"Error adding photo attachment: {e}")
        os.remove(downloaded)
        return

    await sts.edit("🔼 Uploading modified file... ⚡")
    try:
        await bot.send_document(msg.chat.id, output_file, caption="Here is your file with the photo attachment.")
        await sts.delete()
    except Exception as e:
        await sts.edit(f"Error uploading modified file: {e}")
    finally:
        os.remove(downloaded)
        os.remove(output_file)

@Client.on_message(filters.command("attachphoto"))
async def attachphoto_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)    
    
@Client.on_message(filters.command("setphoto") & filters.chat(GROUP))
async def set_photo(bot, msg):
    reply = msg.reply_to_message
    if not reply or not reply.photo:
        return await msg.reply_text("Please reply to a photo with the set photo command")

    photo = reply.photo
    attachment_path = os.path.join(DOWNLOAD_LOCATION, "attachment.jpg")
    await bot.download_media(photo, attachment_path)
    await msg.reply_text("Photo saved successfully as `attachment.jpg`.")

@Client.on_message(filters.command("setphoto"))
async def setphoto_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)    


@Client.on_message(filters.command("changeindex1"))
async def change_index1(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: a-3-1-2 (Audio)")

    if len(msg.command) < 2:
        return await msg.reply_text("Please provide the index command\nFormat: a-3-1-2 (Audio)")

    index_cmd = msg.command[1].strip().lower()
    if not index_cmd.startswith("a-"):
        return await msg.reply_text("Invalid format. Use a-3-1-2 for audio.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the index command.")

    sts = await msg.reply_text("🚀Downloading media...⚡")
    c_time = time.time()
    downloaded = await reply.download(progress=progress_message, progress_args=("🚀Download Started...⚡️", sts, c_time))

    output_file = os.path.join(DOWNLOAD_LOCATION, "output_" + os.path.basename(downloaded))
    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', output_file, '-y'])

    await sts.edit("💠Changing indexing...⚡")
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        await sts.edit(f"❗FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        return

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟Size: {filesize_human}"

    await sts.edit("💠Uploading...⚡")
    c_time = time.time()

    # Use string session if file size exceeds the limit
    if filesize > FILE_SIZE_LIMIT:
        client_to_use = string_session_client
    else:
        client_to_use = bot

    try:
        async with client_to_use:
            await client_to_use.send_document(msg.chat.id, document=output_file, caption=cap, progress=progress_message, progress_args=("💠Upload Started.....", sts, c_time))
    except Exception as e:
        return await sts.edit(f"Error {e}")

    os.remove(downloaded)
    os.remove(output_file)
    await sts.delete()

@Client.on_message(filters.command("attachphoto1") & filters.chat(GROUP))
async def attach_photo1(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the attach photo command")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the attach photo command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    # Check if there is a previously set photo
    attachment_path = os.path.join(DOWNLOAD_LOCATION, "attachment.jpg")
    if not os.path.exists(attachment_path):
        await sts.edit("Please send a photo to be attached using the `setphoto` command.")
        os.remove(downloaded)
        return

    output_file = os.path.join(DOWNLOAD_LOCATION, "output_" + os.path.basename(downloaded))

    await sts.edit("💠 Adding photo attachment... ⚡")
    try:
        add_photo_attachment(downloaded, attachment_path, output_file)
    except Exception as e:
        await sts.edit(f"Error adding photo attachment: {e}")
        os.remove(downloaded)
        return

    await sts.edit("💠 Uploading modified file... ⚡")
    c_time = time.time()
    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟Size: {filesize_human}"

    # Use string session if file size exceeds the limit
    if filesize > FILE_SIZE_LIMIT:
        client_to_use = string_session_client
    else:
        client_to_use = bot

    try:
        async with client_to_use:
            await client_to_use.send_document(msg.chat.id, document=output_file, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡️", sts, c_time))
    except Exception as e:
        return await sts.edit(f"Error uploading modified file: {e}")
    finally:
        os.remove(downloaded)
        os.remove(output_file)
        await sts.delete()

    
async def download_media(reply, progress, progress_args):
    for attempt in range(5):
        try:
            return await reply.download(progress=progress, progress_args=progress_args)
        except RPCError as e:
            print(f"RPCError: {e}. Retrying in {2 ** attempt} seconds...")
            await asyncio.sleep(2 ** attempt)
    raise Exception("Failed to download media after multiple attempts")

async def upload_document(client, chat_id, document, caption, progress, progress_args):
    for attempt in range(5):
        try:
            return await client.send_document(chat_id, document=document, caption=caption, progress=progress, progress_args=progress_args)
        except RPCError as e:
            print(f"RPCError: {e}. Retrying in {2 ** attempt} seconds...")
            await asyncio.sleep(2 ** attempt)
    raise Exception("Failed to upload document after multiple attempts")

@Client.on_message(filters.command("attachphoto") & filters.chat(GROUP))
async def attach_photo(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the attach photo command")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the attach photo command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await download_media(reply, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    attachment_path = os.path.join(DOWNLOAD_LOCATION, "attachment.jpg")
    if not os.path.exists(attachment_path):
        await sts.edit("Please send a photo to be attached using the `setphoto` command.")
        os.remove(downloaded)
        return

    output_file = os.path.join(DOWNLOAD_LOCATION, "output_" + os.path.basename(downloaded))

    await sts.edit("💠 Adding photo attachment... ⚡")
    try:
        add_photo_attachment(downloaded, attachment_path, output_file)
    except Exception as e:
        await sts.edit(f"Error adding photo attachment: {e}")
        os.remove(downloaded)
        return

    await sts.edit("💠 Uploading modified file... ⚡")
    c_time = time.time()
    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟Size: {filesize_human}"

    client_to_use = string_session_client if filesize > FILE_SIZE_LIMIT else bot
    try:
        async with client_to_use:
            await upload_document(client_to_use, msg.chat.id, document=output_file, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error uploading modified file: {e}")
    finally:
        os.remove(downloaded)
        os.remove(output_file)
        await sts.delete()

if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
