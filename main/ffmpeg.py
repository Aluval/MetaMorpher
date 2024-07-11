#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import subprocess
import zipfile
import asyncio
import ffmpeg
import os

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
