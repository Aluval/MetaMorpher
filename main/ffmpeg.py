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
async def remove_all_tags(input_path, output_path, sts_msg):
    try:
        total_size = os.path.getsize(input_path)
    except:
        await safe_edit_message(sts_msg, "❌ Input file error!")
        return False

    command = [
        "ffmpeg",
        "-i", input_path,
        "-map", "0",
        "-map_metadata", "-1",
        "-c", "copy",
        "-progress", "pipe:1",
        "-y", output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    start = time.time()
    last_percent = -1

    while True:
        line = await process.stdout.readline()
        if not line:
            break

        line = line.decode().strip()

        if "out_time_ms=" in line:
            # FFmpeg reports progress time only when re-encoding.
            # But for metadata stripping, we rely on file size processed.
            pass

        if "bytes=" in line:
            parts = line.split("=")[1]
            try:
                processed = int(parts)
                percent = int((processed / total_size) * 100)

                if percent != last_percent:
                    elapsed = time.time() - start
                    eta = (elapsed * (100 - percent) / percent) if percent > 0 else 0

                    await safe_edit_message(
                        sts_msg,
                        f"🧹 **Removing Metadata…**\n"
                        f"Progress: {percent}%\n"
                        f"ETA: {TimeFormatter(int(eta * 1000))}"
                    )
                    last_percent = percent

            except:
                pass

    await process.wait()

    if process.returncode != 0:
        stderr = (await process.stderr.read()).decode()
        await safe_edit_message(sts_msg, f"❌ FFmpeg Error\n{stderr}")
        return False

    await safe_edit_message(sts_msg, "✅ Metadata removed successfully!")
    return True

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def change_video_metadata(
    input_path, video_title, audio_title, subtitle_title, output_path, sts_msg
):
    # Get total size for progress calculation
    try:
        total_size = os.path.getsize(input_path)
    except:
        await safe_edit_message(sts_msg, "❌ Unable to read file size!")
        return False

    command = [
        "ffmpeg",
        "-i", input_path,

        "-metadata", f"title={video_title}",
        "-metadata:s:v", f"title={video_title}",
        "-metadata:s:a", f"title={audio_title}",
        "-metadata:s:s", f"title={subtitle_title}",

        "-map", "0:v?",
        "-map", "0:a?",
        "-map", "0:s?",

        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "copy",

        "-progress", "pipe:1",   # <-- progress enabled
        "-y", output_path,
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    start = time.time()
    last_percent = -1

    # Read progress lines
    while True:
        line = await process.stdout.readline()
        if not line:
            break

        line = line.decode().strip()

        # FFmpeg progress format: bytes=xxxxxx
        if line.startswith("bytes="):
            try:
                processed = int(line.split("=")[1])
                percent = int((processed / total_size) * 100)

                if percent != last_percent:
                    elapsed = time.time() - start
                    eta = (elapsed * (100 - percent) / percent) if percent > 0 else 0

                    await safe_edit_message(
                        sts_msg,
                        f"🏷 **Updating Metadata…**\n"
                        f"Progress: {percent}%\n"
                        f"ETA: {TimeFormatter(int(eta * 1000))}"
                    )

                    last_percent = percent
            except:
                pass

    await process.wait()

    if process.returncode != 0:
        stderr = (await process.stderr.read()).decode()
        await safe_edit_message(sts_msg, f"❌ Metadata update failed:\n{stderr}")
        return False

    await safe_edit_message(sts_msg, "✅ Metadata updated successfully!")
    return True
    
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def generate_sample_video(input_path, duration, output_path, sts_msg):
    # -------- Get full duration --------
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path
    ]

    process = subprocess.Popen(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f"ffprobe error: {stderr.decode('utf-8')}")

    total_duration = float(stdout.decode().strip())

    if duration > total_duration:
        raise ValueError("Requested duration is longer than video length")

    # Sample starts from middle
    start_time = (total_duration - duration) / 2

    # -------- Extract with progress --------
    cmd = [
        "ffmpeg",
        "-ss", str(start_time),
        "-i", input_path,
        "-t", str(duration),

        "-c:v", "copy",
        "-c:a", "copy",

        "-progress", "pipe:1",
        "-y", output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    start = time.time()
    last_percent = -1

    while True:
        line = await process.stdout.readline()
        if not line:
            break

        line = line.decode().strip()

        # FFmpeg gives: out_time_ms=1234567
        if line.startswith("out_time_ms="):
            ms = int(line.split("=")[1])
            cur_sec = ms / 1_000_000  # convert µs → seconds

            percent = int((cur_sec / duration) * 100)

            if percent != last_percent:
                elapsed = time.time() - start
                eta = elapsed * (100 - percent) / percent if percent > 0 else 0

                await safe_edit_message(
                    sts_msg,
                    f"🎞 **Generating Sample Video…**\n"
                    f"Progress: {percent}%\n"
                    f"ETA: {TimeFormatter(int(eta * 1000))}"
                )

                last_percent = percent

    await process.wait()

    if process.returncode != 0:
        stderr_fin = (await process.stderr.read()).decode()
        await safe_edit_message(sts_msg, f"❌ FFmpeg Error\n{stderr_fin}")
        return False

    await safe_edit_message(sts_msg, "✅ Sample video generated successfully!")
    return True
    
#add photo attachment 
async def add_photo_attachment(input_path, attachment_path, output_path, sts_msg):
    # --- Get total file size for progress ---
    try:
        total_size = os.path.getsize(input_path)
    except:
        await safe_edit_message(sts_msg, "❌ Cannot read file size!")
        return False

    command = [
        "ffmpeg",
        "-i", input_path,

        "-map", "0:v?",
        "-map", "0:a?",
        "-map", "0:s?",

        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "copy",

        "-attach", attachment_path,
        "-metadata:s:t", "mimetype=image/jpeg",

        "-progress", "pipe:1",   # <--- PROGRESS ENABLED
        "-y", output_path
    ]

    # --- FFmpeg async process ---
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    start = time.time()
    last_percent = -1

    # --- Read FFmpeg progress lines ---
    while True:
        line = await process.stdout.readline()
        if not line:
            break

        line = line.decode().strip()

        # FFmpeg progress line: "bytes=123456"
        if line.startswith("bytes="):
            try:
                processed = int(line.split("=")[1])
                percent = int((processed / total_size) * 100)

                if percent != last_percent:
                    elapsed = time.time() - start
                    eta = (elapsed * (100 - percent) / percent) if percent > 0 else 0

                    await safe_edit_message(
                        sts_msg,
                        f"🖼 **Adding Photo Attachment…**\n"
                        f"Progress: {percent}%\n"
                        f"ETA: {TimeFormatter(int(eta * 1000))}"
                    )

                    last_percent = percent

            except:
                pass

    await process.wait()

    # --- Check if FFmpeg failed ---
    if process.returncode != 0:
        stderr = (await process.stderr.read()).decode()
        await safe_edit_message(sts_msg, f"❌ Error adding attachment:\n{stderr}")
        return False

    await safe_edit_message(sts_msg, "✅ Photo attachment added successfully!")
    return True

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Function to merge videos 
async def merge_videos(input_file, output_file, sts_msg):
    # 1. Read concat file and calculate total duration
    total_duration = 0
    try:
        with open(input_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith("file"):
                path = line.split("file '")[1].split("'")[0]

                # ffprobe get duration
                cmd = [
                    "ffprobe", "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    path
                ]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
                info = json.loads(result.stdout)
                dur = float(info["format"]["duration"])
                total_duration += dur
    except Exception as e:
        await safe_edit_message(sts_msg, f"❌ Cannot read duration\n{e}")
        return False

    # 2. FFmpeg concat with progress
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", input_file,
        "-c", "copy",
        "-map", "0",
        "-y",
        output_file
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+)[\.:](\d+)")
    start_time = time.time()
    last_percent = -1

    # 3. Read merge progress
    while True:
        line = await process.stderr.readline()
        if not line:
            break

        line = line.decode("utf-8")
        match = time_pattern.search(line)

        if match:
            h, m, s, ms = match.groups()
            current = (
                int(h) * 3600 +
                int(m) * 60 +
                int(s) +
                int(ms) / 100
            )

            percent = int((current / total_duration) * 100)

            if percent != last_percent:
                elapsed = time.time() - start_time
                eta = elapsed * (100 - percent) / percent if percent > 0 else 0

                await safe_edit_message(
                    sts_msg,
                    f"🔗 **Merging Videos**\n"
                    f"Progress: {percent}%\n"
                    f"ETA: {TimeFormatter(int(eta * 1000))}"
                )
                last_percent = percent

    await process.wait()

    if process.returncode != 0:
        stderr = await process.stderr.read()
        await safe_edit_message(sts_msg, f"❌ Merge failed\n{stderr.decode()}")
        return False

    return True


#Extract the audio 
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def extract_audio_stream(input_path, output_path, stream_index, sts_msg):
    # --- Get size for progress calculation ---
    try:
        total_size = os.path.getsize(input_path)
    except:
        await safe_edit_message(sts_msg, "❌ Can't read input file size!")
        return False

    command = [
        "ffmpeg",
        "-i", input_path,
        "-map", f"0:{stream_index}",
        "-c", "copy",

        "-progress", "pipe:1",   # <-- key for progress
        "-y", output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    start = time.time()
    last_percent = -1

    # --- Read lines from ffmpeg progress ---
    while True:
        line = await process.stdout.readline()
        if not line:
            break

        line = line.decode().strip()

        # FFmpeg outputs: bytes=123456
        if line.startswith("bytes="):
            try:
                processed = int(line.split("=")[1])
                percent = int((processed / total_size) * 100)

                if percent != last_percent:
                    elapsed = time.time() - start
                    eta = (elapsed * (100 - percent) / percent) if percent > 0 else 0

                    await safe_edit_message(
                        sts_msg,
                        f"🎵 **Extracting Audio Stream…**\n"
                        f"Progress: {percent}%\n"
                        f"ETA: {TimeFormatter(int(eta * 1000))}"
                    )

                    last_percent = percent

            except:
                pass

    await process.wait()

    # --- FFmpeg Error Handling ---
    if process.returncode != 0:
        stderr = (await process.stderr.read()).decode()
        await safe_edit_message(sts_msg, f"❌ Audio extraction failed:\n{stderr}")
        return False

    await safe_edit_message(sts_msg, "✅ Audio stream extracted successfully!")
    return True
    
#Extract the subtitles 
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def extract_subtitle_stream(input_path, output_path, stream_index, sts_msg):
    # --- Get input total file size for progress ---
    try:
        total_size = os.path.getsize(input_path)
    except:
        await safe_edit_message(sts_msg, "❌ Unable to read file size!")
        return False

    command = [
        "ffmpeg",
        "-i", input_path,
        "-map", f"0:{stream_index}",
        "-c", "copy",

        "-progress", "pipe:1",   # Enable progress output
        "-y", output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    start = time.time()
    last_percent = -1

    # --- Read FFmpeg progress lines ---
    while True:
        line = await process.stdout.readline()
        if not line:
            break

        line = line.decode().strip()

        # FFmpeg: bytes=XXXXXX
        if line.startswith("bytes="):
            try:
                processed = int(line.split("=")[1])
                percent = int((processed / total_size) * 100)

                if percent != last_percent:
                    elapsed = time.time() - start
                    eta = (elapsed * (100 - percent) / percent) if percent > 0 else 0

                    await safe_edit_message(
                        sts_msg,
                        (
                            "📝 **Extracting Subtitle Stream…**\n"
                            f"Progress: {percent}%\n"
                            f"ETA: {TimeFormatter(int(eta * 1000))}"
                        )
                    )

                    last_percent = percent

            except:
                pass

    await process.wait()

    # --- Check for FFmpeg failure ---
    if process.returncode != 0:
        stderr = (await process.stderr.read()).decode()
        await safe_edit_message(sts_msg, f"❌ Subtitle extraction failed:\n{stderr}")
        return False

    await safe_edit_message(sts_msg, "✅ Subtitle extracted successfully!")
    return True

#Extract the video 
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def extract_video_stream(input_path, output_path, stream_index, codec_name, sts_msg):
    # -------- Step 1: Extract raw video stream --------
    temp_output = f"{output_path}.{codec_name}"

    try:
        total_size = os.path.getsize(input_path)
    except:
        await safe_edit_message(sts_msg, "❌ Cannot read input file size!")
        return False

    extract_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-map", f"0:{stream_index}",
        "-c", "copy",
        "-progress", "pipe:1",
        "-y", temp_output
    ]

    process = await asyncio.create_subprocess_exec(
        *extract_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    start = time.time()
    last = -1

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        line = line.decode().strip()

        if line.startswith("bytes="):
            try:
                processed = int(line.split("=")[1])
                percent = int((processed / total_size) * 100)

                if percent != last:
                    elapsed = time.time() - start
                    eta = elapsed * (100 - percent) / percent if percent > 0 else 0

                    await safe_edit_message(
                        sts_msg,
                        f"🎬 **Extracting Video Stream…**\n"
                        f"Progress: {percent}%\n"
                        f"ETA: {TimeFormatter(int(eta * 1000))}"
                    )

                    last = percent
            except:
                pass

    await process.wait()
    if process.returncode != 0:
        stderr = (await process.stderr.read()).decode()
        await safe_edit_message(sts_msg, f"❌ Stream extraction failed:\n{stderr}")
        return False

    # ---------------------------------------------------
    # -------- Step 2: Convert temporary → MKV --------
    # ---------------------------------------------------

    mkv_output = f"{output_path}.mkv"

    convert_cmd_mkv = [
        "ffmpeg",
        "-i", temp_output,
        "-c", "copy",
        "-progress", "pipe:1",
        "-y", mkv_output
    ]

    await safe_edit_message(sts_msg, "🔄 Converting to MKV…")

    process_mkv = await asyncio.create_subprocess_exec(
        *convert_cmd_mkv,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    while True:
        line = await process_mkv.stdout.readline()
        if not line:
            break
        line = line.decode().strip()

        if line.startswith("progress="):
            await safe_edit_message(sts_msg, "🔄 MKV conversion in progress…")

    await process_mkv.wait()

    # ---------------------------------------------------
    # -------- Step 3: Convert temporary → MP4 --------
    # ---------------------------------------------------

    mp4_output = f"{output_path}.mp4"

    convert_cmd_mp4 = [
        "ffmpeg",
        "-i", temp_output,
        "-c", "copy",
        "-progress", "pipe:1",
        "-y", mp4_output
    ]

    await safe_edit_message(sts_msg, "🔄 Converting to MP4…")

    process_mp4 = await asyncio.create_subprocess_exec(
        *convert_cmd_mp4,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    while True:
        line = await process_mp4.stdout.readline()
        if not line:
            break
        line = line.decode().strip()

        if line.startswith("progress="):
            await safe_edit_message(sts_msg, "🔄 MP4 conversion in progress…")

    await process_mp4.wait()

    # ---------------------------------------------------
    # -------- FINAL STEP: Return correct file --------
    # ---------------------------------------------------

    os.remove(temp_output)

    if process_mp4.returncode == 0:
        await safe_edit_message(sts_msg, "✅ Video stream extracted and saved as MP4!")
        return mp4_output

    if process_mkv.returncode == 0:
        await safe_edit_message(sts_msg, "✅ Video stream extracted and saved as MKV!")
        return mkv_output

    # If both conversions failed
    stderr1 = (await process_mkv.stderr.read()).decode()
    stderr2 = (await process_mp4.stderr.read()).decode()
    await safe_edit_message(sts_msg, f"❌ Conversion failed:\n{stderr1}\n{stderr2}")
    return False

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
        '-crf', '28',
        '-preset', 'ultrafast',
        '-pix_fmt', 'yuv420p',      

        '-c:a', 'libopus',
        '-b:a', '128k',

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
