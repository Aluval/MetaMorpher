


# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
from pyrogram.types import *
import math
import time
import random
import asyncio

PROGRESS_BAR = "\n\n📁 : {b} | {c}\n🚀 : {a}%\n⚡ : {d}/s\n⏱️ : {f}"



# Constants
DOWNLOAD_MIN_SPEED = 5 * 1024 * 1024 / 8  # 5 Mbps in Bytes/s
DOWNLOAD_MAX_SPEED = 9 * 1024 * 1024 / 8  # 9 Mbps in Bytes/s
UPLOAD_MIN_SPEED = 10 * 1024 * 1024 / 8   # 10 Mbps in Bytes/s
UPLOAD_MAX_SPEED = 15 * 1024 * 1024 / 8   # 15 Mbps in Bytes/s
PROGRESS_BAR = "\n\n📁 : {b} | {c}\n🚀 : {a}%\n⚡ : {d}/s\n⏱️ : {f}"

def mock_speed(is_download=True):
    if is_download:
        return random.uniform(DOWNLOAD_MIN_SPEED, DOWNLOAD_MAX_SPEED)
    else:
        return random.uniform(UPLOAD_MIN_SPEED, UPLOAD_MAX_SPEED)

def humanbytes(size):
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "") + \
          ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]
async def progress_message(current, total, ud_type, message, start, is_download=True):
    now = time.time()
    diff = now - start
    if round(diff % 1.00) == 0 or current == total:  # Update every second or when complete
        speed = mock_speed(is_download)
        current = min(current + speed, total)  # Ensure current doesn't exceed total

        percentage = current * 100 / total
        time_to_completion = (total - current) / speed
        elapsed_time = TimeFormatter(milliseconds=diff * 1000)
        estimated_total_time = TimeFormatter(milliseconds=time_to_completion * 1000)
        
        progress = "\n{0}{1}".format(
            ''.join(["✦" for _ in range(math.floor(percentage / 5))]),
            ''.join(["✧" for _ in range(20 - math.floor(percentage / 5))]))
        
        tmp = (f"✦ {ud_type}\n\n{progress} {percentage:.2f}%\n\n"
               f"{humanbytes(current)} of {humanbytes(total)}\n\n"
               f"✦ Speed: {humanbytes(speed)}/s\n\n"
               f"✦ ETA: {estimated_total_time}")
        
        try:
            await message.edit(text=tmp)
        except Exception as e:
            print(f"Error updating progress: {e}")

async def download_progress(current, total, message, start):
    await progress_message(current, total, "🚀Downloading media...⚡️", message, start, is_download=True)

async def upload_progress(current, total, message, start):
    await progress_message(current, total, "🚀Uploading media...⚡️", message, start, is_download=False)


async def simulate_progress(message):
    total_size = 1.61 * 1024 * 1024 * 1024  # Example total size of 1.61 GB
    current_size = 0
    start_time = time.time()

    # Simulate downloading
    while current_size < total_size:
        await download_progress(current_size, total_size, message, start_time)
        current_size += mock_speed(is_download=True)  # Increment current size
        await asyncio.sleep(1)  # Simulate delay

    current_size = 0
    start_time = time.time()
    
    # Simulate uploading
    while current_size < total_size:
        await upload_progress(current_size, total_size, message, start_time)
        current_size += mock_speed(is_download=False)  # Increment current size
        await asyncio.sleep(1)  # Simulate delay

# Assuming you have a bot and a message object from the user interaction
# asyncio.run(simulate_progress(message))
