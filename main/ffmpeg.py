#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import re
import time
import shutil
import subprocess
import zipfile
import asyncio
import ffmpeg
import os, sys
import json
from html_telegraph_poster import TelegraphPoster
from pyrogram.errors import FloodWait, MessageNotModified
import traceback
from main.utils import TimeFormatter

# Initialize Telegraph
telegraph = TelegraphPoster(use_api=True)
telegraph.create_api_token("MediaInfoBot")

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
def generate_sample_video(input_path, duration, output_path):
    # Get the total duration of the input video using ffprobe
    probe_command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_path
    ]
    process = subprocess.Popen(probe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"ffprobe error: {stderr.decode('utf-8')}")
    
    total_duration = float(stdout.decode('utf-8').strip())
    if duration > total_duration:
        raise ValueError("Requested duration is longer than the total duration of the video")

    # Calculate the start time for the sample (middle of the video)
    start_time = (total_duration - duration) / 2

    # Generate the sample video using ffmpeg
    command = [
        'ffmpeg',
        '-ss', str(start_time),
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

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Function to merge videos 
async def merge_videos(input_file, output_file):
    file_generator_command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        input_file,
        "-c",
        "copy",
        "-map",
        "0",
        output_file,
    ]
    try:
        process = await asyncio.create_subprocess_exec(
            *file_generator_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"FFmpeg process returned error: {stderr.decode()}")

    except Exception as e:
        raise RuntimeError(f"Error merging videos: {e}")

#Extract the audio 
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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

#Extract the subtitles 
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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


#Extract the video 
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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
  
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24        
# Recursive function to extract audio
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

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24        
# Recursive function to extract subtitles 
def extract_subtitles_from_file(input_path):
    video_streams_data = ffmpeg.probe(input_path)
    subtitles = [stream for stream in video_streams_data.get("streams") if stream.get("codec_type") == "subtitle"]

    extracted_files = []
    for subtitle in subtitles:
        output_file = os.path.join(os.path.dirname(input_path), f"{subtitle['index']}.{subtitle['codec_type']}.srt")
        extract_subtitle_stream(input_path, output_file, subtitle['index'])
        extracted_files.append((output_file, subtitle))

    return extracted_files

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24        
# Recursive function to extract  Video
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

# Function to extract media information using mediainfo command
def get_mediainfo(file_path):
    process = subprocess.Popen(
        ["mediainfo", file_path, "--Output=HTML"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Error getting media info: {stderr.decode().strip()}")
    return stdout.decode().strip()



async def compress_video(
    input_path, output_path,
    video_title, audio_title, subtitle_title,
    sts_msg
):
    # ---- Get duration (SAFE JSON method) ----
    try:
        duration_cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_path
        ]

        result = subprocess.run(duration_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not result.stdout:
            await safe_edit_message(sts_msg, "❌ ffprobe returned empty output. File may be corrupted.")
            return False

        info = json.loads(result.stdout)

        if "format" in info and "duration" in info["format"]:
            total_duration = float(info["format"]["duration"])
        else:
            total_duration = None
            for stream in info.get("streams", []):
                if "duration" in stream:
                    total_duration = float(stream["duration"])
                    break

        if not total_duration:
            raise Exception("No duration found in metadata.")

    except Exception as e:
        await safe_edit_message(sts_msg, f"❌ Could not read video duration.\n{e}")
        return False

    # ---- FFmpeg Command ----
    command = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'libx264',
        '-b:v', '400k',
        '-preset', 'superfast',
        '-pix_fmt', 'yuv420p',      

        '-c:a', 'aac',
        '-b:a', '96k',

        '-map', '0:v:0',
        '-map', '0:a',
        '-map', '0:s?',

        '-metadata', f'title={video_title}',
        '-metadata:s:v:0', f'title={video_title}',
        '-metadata:s:a', f'title={audio_title}',
        '-metadata:s:s', f'title={subtitle_title}',

        '-movflags', '+faststart',
        '-y', output_path
    ]

    # ---- Start FFmpeg ----
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+)[\.:](\d+)")
    start_time = time.time()
    last_percent = -1

    # ---- Progress Reader ----
    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break

        match = time_pattern.search(line)
        if match:
            h, m, s, ms = match.groups()
            cur = (int(h) * 3600) + (int(m) * 60) + int(s) + (int(ms) / 100)

            percent = int((cur / total_duration) * 100)

            if percent != last_percent and percent > 0:
                elapsed = time.time() - start_time
                eta = (elapsed * (100 - percent) / percent) if percent > 0 else 0

                # ✔ Correct TimeFormatter conversion: expects milliseconds
                eta_ms = int(eta * 1000)

                await safe_edit_message(
                    sts_msg,
                    f"⚙️ **Compressing:** {percent}%\n⏳ ETA: {TimeFormatter(eta_ms)}"
                )

                last_percent = percent

    # ---- Check Failure ----
    if process.poll() != 0:
        await safe_edit_message(sts_msg, "❌ FFmpeg failed.")
        return False

    return True

async def safe_edit_message(msg, text):
    if msg is None:
        return
    try:
        if msg.text == text:
            return
        await msg.edit_text(text)
    except MessageNotModified:
        pass
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await msg.edit_text(text)
        except:
            pass
    except:
        pass

# Function to compress mediainfo information using compress command
async def get_and_upload_mediainfo(bot, output_file, media):
    media_info_html = get_mediainfo(output_file)

    media_info_html = (
        f"<strong>SUNRISES 24 BOT UPDATES</strong><br>"
        f"<strong>MediaInfo X</strong><br>"
        f"{media_info_html}"
        f"<p>Rights Designed By Sᴜɴʀɪsᴇs Hᴀʀsʜᴀ 𝟸𝟺 🇮🇳 ᵀᴱᴸ</p>"
    )

    response = telegraph.post(
        title="MediaInfo",
        author="SUNRISES 24 BOT UPDATES",
        author_url="https://t.me/Sunrises24BotUpdates",
        text=media_info_html
    )

    link = f"https://graph.org/{response['path']}"
    return media_info_html, link
