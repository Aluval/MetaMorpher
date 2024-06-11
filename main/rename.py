import os
import time, datetime
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
from config import GROUP, AUTH_USERS
from main.utils import heroku_restart
import aiohttp
import aiohttp
from pyrogram.errors import RPCError, FloodWait


@Client.on_message(filters.command("removetags") & filters.chat(GROUP))
async def remove_tags(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the removetags command")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the removetags command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    cleaned_file = os.path.join(DOWNLOAD_LOCATION, "cleaned_" + os.path.basename(downloaded))

    await sts.edit("💠 Removing all tags... ⚡")
    try:
        remove_all_tags(downloaded, cleaned_file)
    except Exception as e:
        await sts.edit(f"Error removing all tags: {e}")
        os.remove(downloaded)
        return

    await sts.edit("🔼 Uploading cleaned file... ⚡")
    try:
        await bot.send_document(msg.chat.id, cleaned_file, caption="Here is your file with all tags removed.")
        await sts.delete()
    except Exception as e:
        await sts.edit(f"Error uploading cleaned file: {e}")
    finally:
        os.remove(downloaded)
        os.remove(cleaned_file)

def remove_all_tags(input_path, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-map', '0',
        '-map_metadata', '-1',  # This removes all metadata
        '-c', 'copy',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")
        
@Client.on_message(filters.command("linktofile") & filters.chat(GROUP))
async def linktofile(bot, msg: Message):
    reply = msg.reply_to_message
    if len(msg.command) < 2 or not reply:
        return await msg.reply_text("Please Reply To A File, Video, Audio, or Link With filename + .extension (e.g., `.mkv`, `.mp4`, or `.zip`)")

    new_name = msg.text.split(" ", 1)[1]

    media = reply.document or reply.audio or reply.video
    if not media and not reply.text:
        return await msg.reply_text("Please Reply To A File, Video, Audio, or Link With filename + .extension (e.g., `.mkv`, `.mp4`, or `.zip`)")

    if reply.text and ("seedr" in reply.text or "workers" in reply.text):
        await handle_link_download(bot, msg, reply.text, new_name)
    else:
        if not media:
            return await msg.reply_text("Please Reply To A Valid File, Video, Audio, or Link With filename + .extension (e.g., `.mkv`, `.mp4`, or `.zip`)")

        og_media = getattr(reply, reply.media.value)
        sts = await msg.reply_text("🚀 Downloading...")
        c_time = time.time()
        try:
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started...", sts, c_time))
        except RPCError as e:
            return await sts.edit(f"Download failed: {e}")

        filesize = humanbytes(og_media.file_size)

        if CAPTION:
            try:
                cap = CAPTION.format(file_name=new_name, file_size=filesize)
            except Exception as e:
                return await sts.edit(text=f"Your caption has an error: unexpected keyword ●> ({e})")
        else:
            cap = f"{new_name}\n\n🌟 Size: {filesize}"

        # Thumbnail handling
        file_thumb = None
        if og_media.thumbs:
            try:
                file_thumb = await bot.download_media(og_media.thumbs[0].file_id, file_name=f"{DOWNLOAD_LOCATION}/{new_name}_thumb.jpg")
            except Exception as e:
                print(f"Error downloading thumbnail: {e}")
                file_thumb = None

        await sts.edit("💠 Uploading...")
        c_time = time.time()
        try:
            await bot.send_document(
                msg.chat.id, 
                document=downloaded, 
                thumb=file_thumb, 
                caption=cap, 
                progress=progress_message, 
                progress_args=("💠 Upload Started...", sts, c_time)
            )
        except RPCError as e:
            await sts.edit(f"Upload failed: {e}")
        except TimeoutError as e:
            await sts.edit(f"Upload timed out: {e}")
        finally:
            try:
                if file_thumb:
                    os.remove(file_thumb)
                os.remove(downloaded)
            except Exception as e:
                print(f"Error deleting files: {e}")
            await sts.delete()


async def handle_link_download(bot, msg: Message, link: str, new_name: str):
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
    filesize = humanbytes(filesize)

    if CAPTION:
        try:
            cap = CAPTION.format(file_name=new_name, file_size=filesize)
        except Exception as e:
            await sts.edit(text=f"Your caption has an error: unexpected keyword ●> ({e})")
            return
    else:
        cap = f"{new_name}\n\n🌟 Size: {filesize}"

    await sts.edit("💠 Uploading...")
    c_time = time.time()
    try:
        await bot.send_document(msg.chat.id, document=new_name, caption=cap, progress=progress_message, progress_args=("💠 Upload Started...", sts, c_time))
    except RPCError as e:
        await sts.edit(f"Upload failed: {e}")
    except TimeoutError as e:
        await sts.edit(f"Upload timed out: {e}")
    finally:
        try:
            os.remove(new_name)
        except Exception as e:
            print(f"Error deleting file: {e}")
        await sts.delete()

            

@Client.on_message(filters.command("linktofile"))
async def linktofile_private(client, message):
  buttons = [[
    InlineKeyboardButton("GROUP", url="https://t.me/INFINITYRENAME24GROUP")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nTʜɪꜱ Fᴇᴀᴛᴜʀᴇ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴘ", reply_markup=reply_markup)     
    


 
 # Define restart_app command
@Client.on_message(filters.command("restart") & filters.chat(GROUP))
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
        

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Rename Command
@Client.on_message(filters.command("rename") & filters.chat(GROUP))
async def rename_file(bot, msg):
    reply = msg.reply_to_message
    if len(msg.command) < 2 or not reply:
       return await msg.reply_text("Please Reply To An File or video or audio With filename + .extension eg:-(`.mkv` or `.mp4` or `.zip`)")
    media = reply.document or reply.audio or reply.video
    if not media:
       await msg.reply_text("Please Reply To An File or video or audio With filename + .extension eg:-(`.mkv` or `.mp4` or `.zip`)")
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
            return await sts.edit(text=f"Your caption Error unexpected keyword ●> ({e})")           
    else:
        cap = f"{new_name}\n\n🌟size : {filesize}"

    #ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24

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


# Change Index Command
@Client.on_message(filters.command("changeindex") & filters.chat(GROUP))
async def change_index(bot, msg):
    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `a-3-1-2 | filename.mkv` (Audio)")

    if len(msg.command) < 2:
        return await msg.reply_text("Please provide the index command\nFormat: `a-3-1-2 | filename.mkv` (Audio)")

    command_parts = msg.command[1].strip().lower().split("|")
    index_cmd = command_parts[0].strip()
    output_filename = command_parts[1].strip() if len(command_parts) > 1 else None

    if not index_cmd.startswith("a-"):
        return await msg.reply_text("Invalid format. Use `a-3-1-2 | filename.mkv` for audio.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the index command.")

    sts = await msg.reply_text("🚀Downloading media...⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("Downloading", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        return

    if output_filename is None:
        return await sts.edit("Please provide a filename in the format `a-3-1-2 | filename.mkv`.")

    output_file = os.path.join(DOWNLOAD_LOCATION, output_filename)
    
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

    # Thumbnail handling
    file_thumb = None
    if media.thumbs:
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=f"{DOWNLOAD_LOCATION}/thumbnail.jpg")
            print("Thumbnail downloaded successfully:", file_thumb)  # Debug print
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")
            file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟Size: {filesize_human}"

    await sts.edit("💠Uploading...⚡")
    c_time = time.time()
    try:
        await bot.send_document(
            msg.chat.id, 
            document=output_file, 
            thumb=file_thumb, 
            caption=cap, 
            progress=progress_message, 
            progress_args=("Uploading", sts, c_time)
        )
        await sts.delete()
    except RPCError as e:
        await sts.edit(f"Upload failed: {e}")
    except TimeoutError as e:
        await sts.edit(f"Upload timed out: {e}")
    finally:
        try:
            if file_thumb:
                os.remove(file_thumb)
            os.remove(downloaded)
            os.remove(output_file)
        except Exception as e:
            print(f"Error deleting files: {e}")


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
        return await msg.reply_text("Please reply to a media file with the metadata command\nFormat: `changemetadata video_title | audio_title | subtitle_title | filename.mkv`")

    if len(msg.command) < 2:
        return await msg.reply_text("Please provide the new titles\nFormat: `changemetadata video_title | audio_title | subtitle_title | filename.mkv`")

    titles = " ".join(msg.command[1:]).strip().split('|')
    if len(titles) != 4:
        return await msg.reply_text("Please provide all three titles and the filename separated by '|'\nFormat: `changemetadata video_title | audio_title | subtitle_title | filename.mkv`")

    video_title, audio_title, subtitle_title, output_filename = titles
    video_title = video_title.strip()
    audio_title = audio_title.strip()
    subtitle_title = subtitle_title.strip()
    output_filename = output_filename.strip()

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

    output_file = os.path.join(DOWNLOAD_LOCATION, output_filename)

    await sts.edit("💠 Changing metadata... ⚡")
    try:
        change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await sts.edit(f"Error changing metadata: {e}")
        os.remove(downloaded)
        return

    # Thumbnail handling
    file_thumb = None
    if media.thumbs:
        try:
            file_thumb = await bot.download_media(media.thumbs[0].file_id, file_name=f"{DOWNLOAD_LOCATION}/thumbnail.jpg")
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")
            file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟Size: {filesize_human}"

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()
    try:
        await bot.send_document(
            msg.chat.id, 
            document=output_file, 
            thumb=file_thumb, 
            caption=cap, 
            progress=progress_message, 
            progress_args=("💠 Upload Started...", sts, c_time)
        )
        await sts.delete()
    except RPCError as e:
        await sts.edit(f"Upload failed: {e}")
    except TimeoutError as e:
        await sts.edit(f"Upload timed out: {e}")
    finally:
        try:
            if file_thumb:
                os.remove(file_thumb)
            os.remove(downloaded)
            os.remove(output_file)
        except Exception as e:
            print(f"Error deleting files: {e}")

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

if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
