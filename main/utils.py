from pyrogram.types import *
import math
import os
import time
import asyncio

PROGRESS_BAR = "\n\n📁 : {b} | {c}\n🚀 : {a}%\n⚡ : {d}/s\n⏱️ : {f}"

# Progress message
async def progress_message(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    
    # Update progress every 10 seconds or when completed
    if int(diff) % 10 == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff * 1000)
        time_to_completion = round((total - current) / speed * 1000)
        estimated_total_time = elapsed_time + time_to_completion
        
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        
        progress = "\n{0}{1}".format(
            ''.join(["⬢" for _ in range(math.floor(percentage / 5))]),
            ''.join(["⬡" for _ in range(20 - math.floor(percentage / 5))])
        )
        
        tmp = progress + "\nProgress: {a}%\nDownloaded: {b} of {c}\nSpeed: {d}/s\nETA: {f}".format(
            a=round(percentage, 2),
            b=humanbytes(current),
            c=humanbytes(total),
            d=humanbytes(speed),
            f=estimated_total_time if estimated_total_time else "0 s"
        )
        
        try:
            chance = [[InlineKeyboardButton("🚫 Cancel", callback_data="del")]]
            await message.edit(text="{}\n{}".format(ud_type, tmp), reply_markup=InlineKeyboardMarkup(chance))
        except Exception as e:
            print(f"Error updating progress message: {e}")

# Helper functions
def humanbytes(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units) - 1:
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "") + \
          ((str(milliseconds) + "ms, ") if milliseconds else "")
    
    return tmp[:-2]  # Removing the last comma and space

# Asynchronous function to handle file download/upload
async def handle_file(file_path, ud_type, message):
    start = time.time()
    total_size = os.path.getsize(file_path)
    current_size = 0

    # Simulate file handling
    with open(file_path, 'rb') as f:
        while chunk := f.read(1024 * 1024):  # Reading in 1MB chunks
            await asyncio.sleep(0.01)  # Simulate network delay
            current_size += len(chunk)
            await progress_message(current_size, total_size, ud_type, message, start)
