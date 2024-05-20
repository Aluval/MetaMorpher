import os
import time
import datetime
import shutil
import zipfile
import tarfile, json
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import MessageNotModified
from config import DOWNLOAD_LOCATION, CAPTION
from main.utils import progress_message, humanbytes
import subprocess

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Rename Command
@Client.on_message(filters.private & filters.command("rename"))
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

# Change Index Command
@Client.on_message(filters.private & filters.command("changeindex"))
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

# Change Metadata Function
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

# Change Metadata Handler
@Client.on_message(filters.private & filters.command("changemetadata"))
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

    sts = await msg.reply_text("🚀Downloading media...⚡")
    c_time = time.time()
    downloaded = await reply.download(progress=progress_message, progress_args=("🚀Download Started...⚡️", sts, c_time))

    output_file = os.path.join(DOWNLOAD_LOCATION, "output_" + os.path.basename(downloaded))

    await sts.edit("💠Changing metadata...⚡")
    try:
        change_video_metadata(downloaded, video_title.strip(), audio_title.strip(), subtitle_title.strip(), output_file)
    except Exception as e:
        await sts.edit(f"Error changing metadata: {e}")
        os.remove(downloaded)
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
@Client.on_message(filters.private & filters.command(["samplevideo150", "samplevideo120", "samplevideo90", "samplevideo60", "samplevideo30"]))
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

# Screenshots by Number Handler
@Client.on_message(filters.private & filters.command("screenshots"))
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
@Client.on_message(filters.private & filters.command("unzip"))
async def unzip(bot, msg):
    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file to unzip.")

    media = msg.reply_to_message.document
    if not media:
        return await msg.reply_text("Please reply to a valid zip file.")

    sts = await msg.reply_text("🚀Downloading file...⚡")
    c_time = time.time()
    input_path = await bot.download_media(media, progress=progress_message, progress_args=("🚀Downloading file...⚡️", sts, c_time))

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


  #Function of merge video                             
async def merge_videos_and_audios(bot, msg, video_paths, audio_paths):
    output_path = os.path.join(DOWNLOAD_LOCATION, "merged_video.mp4")
    
    # Merge the files
    try:
        ffmpeg_cmd = ['ffmpeg']
        # Add input video files
        for video_path in video_paths:
            ffmpeg_cmd.extend(['-i', video_path])
        
        # Add input audio files
        for audio_path in audio_paths:
            ffmpeg_cmd.extend(['-i', audio_path])
        
        # Concatenate videos and audios
        ffmpeg_cmd.extend(['-filter_complex', f'[0:v]concat=n={len(video_paths)}:v=1:a=1[outv];{";".join([f'[{i+1}:a]' for i in range(len(video_paths))])}concat=n={len(audio_paths)}:v=0:a=1[outa]', '-map', '[outv]', '-map', '[outa]'])
        
        # Set output format and codec
        ffmpeg_cmd.extend(['-c:v', 'copy', '-c:a', 'aac', output_path, '-y'])
        
        process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")
    except Exception as e:
        # Handle any errors during merging
        raise e

    return output_path

# Command handler to merge videos and audios
@Client.on_message(filters.private & filters.command("merge"))
async def merge_videos_and_audios_handler(bot, msg):
    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a video file to merge.")

    # Store the initial message to check if subsequent messages are sent after the command
    initial_message = msg

    # Lists to store video and audio paths
    video_paths = []
    audio_paths = []

    # Wait for subsequent messages until a timeout or until 10 files are received
    async for message in msg.iter_media():
        if len(video_paths) >= 10:
            break

        media = message.video or message.document
        if media:
            media_path = await media.download(progress=progress_message, progress_args=("🚀Download Started...⚡️", sts, c_time))
            if message.video:
                video_paths.append(media_path)
            else:
                audio_paths.append(media_path)

    # If no files were received after the command, return with a message
    if initial_message == msg:
        return await msg.reply_text("No files were received after the command.")

    # Merge the files
    try:
        output_path = await merge_videos_and_audios(bot, msg, video_paths, audio_paths)
    except Exception as e:
        # Handle any errors during merging
        return await msg.reply_text(f"❗Error merging videos and audios: {e}")

    # Upload the merged file
    filesize = os.path.getsize(output_path)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_path)}\n\n🌟Size: {filesize_human}"

    await msg.reply_text("💠Merging complete. Uploading...⚡")

    try:
        await bot.send_document(msg.chat.id, document=output_path, caption=cap, progress=progress_message, progress_args=("💠Upload Started.....", sts, c_time))
    except Exception as e:
        return await msg.reply_text(f"Error uploading merged file: {e}")

    # Remove the downloaded files and the merged file
    for audio_path in audio_paths:
        os.remove(audio_path)
    os.remove(output_path)
   

@Client.on_message(filters.private & filters.command("extract"))
async def extract_media_handler(bot, msg):
    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a video file to extract media.")

    reply = msg.reply_to_message
    video = reply.video or reply.document
    if not video:
        return await msg.reply_text("Please reply to a valid video file.")

    sts = await msg.reply_text("💠Extracting media...⚡")

    if isinstance(video, Document):
        video_path = await bot.download_media(video)
    elif isinstance(video, Video):
        video_path = await bot.download_media(video, progress=progress_message, progress_args=("🚀Download Started...⚡️", sts, time.time()))

    # Define output paths
    output_audio_path = os.path.join(DOWNLOAD_LOCATION, "extracted_audio.mp3")
    output_subtitles_path = os.path.join(DOWNLOAD_LOCATION, "extracted_subtitles.srt")

    try:
        extract_media(video_path, output_audio_path, output_subtitles_path)
    except Exception as e:
        await sts.edit(f"❗Error extracting media: {e}")
        os.remove(video_path)
        return

    # Get duration of the extracted audio
    audio_duration = get_duration(output_audio_path)

    # Get duration of the extracted subtitles
    subtitles_duration = get_duration(output_subtitles_path) if os.path.exists(output_subtitles_path) else None

    # Output duration information
    duration_info = f"🎵 Extracted Audio Duration: {audio_duration}\n📝 Extracted Subtitles Duration: {subtitles_duration}" if subtitles_duration else f"🎵 Extracted Audio Duration: {audio_duration}"

    await sts.edit(duration_info)

    # Send the extracted media
    if os.path.exists(output_subtitles_path):
        await bot.send_document(msg.chat.id, document=output_subtitles_path, caption="🎵 Extracted Audio & Subtitles 📝", progress=progress_message, progress_args=("💠Upload Started.....", sts, time.time()))
    else:
        await bot.send_audio(msg.chat.id, audio=output_audio_path, caption="🎵 Extracted Audio 🎶", progress=progress_message, progress_args=("💠Upload Started.....", sts, time.time()))

    os.remove(video_path)
    os.remove(output_audio_path)
    if os.path.exists(output_subtitles_path):
        os.remove(output_subtitles_path)

    await sts.delete()

    audio_duration = get_duration(output_audio_path)
subtitles_duration = get_duration(output_subtitles_path) if os.path.exists(output_subtitles_path) else None

duration_info = f"🎵 Extracted Audio Duration: {audio_duration} seconds\n📝 Extracted Subtitles Duration: {subtitles_duration} seconds" if subtitles_duration else f"🎵 Extracted Audio Duration: {audio_duration} seconds"
    


def get_duration(file_path):
    try:
        ffprobe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', file_path]
        result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        duration_info = json.loads(result.stdout)
        duration = float(duration_info['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting duration: {e}")
        return None

    
if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
