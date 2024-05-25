


# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
from pyrogram.types import *
import math
import time
import random

def mock_speed(is_download=True):
    if is_download:
        return random.uniform(5 * 1024 * 1024 / 8, 9 * 1024 * 1024 / 8)  # 5-9 Mbps converted to Bytes/s
    else:
        return random.uniform(10 * 1024 * 1024 / 8, 15 * 1024 * 1024 / 8)  # 10-15 Mbps converted to Bytes/s
        
PROGRESS_BAR = "\n\n📁 : {b} | {c}\n🚀 : {a}%\n⚡ : {d}/s\n⏱️ : {f}"

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
    if round(diff % 10.00) == 0 or current == total:
        speed = mock_speed(is_download)
        current += speed * 1  # Simulate 1-second interval updates
        if current > total:
            current = total

        percentage = current * 100 / total
        elapsed_time = round(diff) * 1000
        time_to_completion = (total - current) / speed
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=time_to_completion * 1000)
        progress = "\n{0}{1}".format(
            ''.join(["▪️" for i in range(math.floor(percentage / 5))]),
            ''.join(["▫️" for i in range(20 - math.floor(percentage / 5))]))
        tmp = f"✦ {ud_type}\n\n{progress} {percentage:.2f}%\n\n{humanbytes(current)} of {humanbytes(total)}\n\n✦ Speed: {humanbytes(speed)}\n\n✦ ETA: {estimated_total_time}"                              
        try:
            await message.edit(text=tmp)
        except Exception as e:
            print(f"Error updating progress: {e}")

async def download_progress(current, total, message, start):
    await progress_message(current, total, "🚀Downloading media...⚡️", message, start, is_download=True)

async def upload_progress(current, total, message, start):
    await progress_message(current, total, "🚀Uploading media...⚡️", message, start, is_download=False)
