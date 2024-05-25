import math
import os
import time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

PROGRESS_BAR = "\n\n📁 : {b} | {c}\n🚀 : {a}%\n⚡ : {d}/s\n⏱️ : {f}"

# Change progress_for_pyrogram to progress_message
async def progress_message(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start

    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time, time_to_completion, estimated_total_time = calculate_times(
            diff, current, total, speed
        )

        progress = "\n{0}{1}".format(
            ''.join(["⬢" for _ in range(math.floor(percentage / 5))]),
            ''.join(["⬡" for _ in range(20 - math.floor(percentage / 5))])
        )                                  
        tmp = progress + PROGRESS_BAR.format(
            a=round(percentage, 2),
            b=humanbytes(current),
            c=humanbytes(total),
            d=humanbytes(speed),
            f=estimated_total_time if estimated_total_time != '' else "0 s"
        )

        try:
            chance = [[InlineKeyboardButton("🚫 Cancel", callback_data="del")]]
            # Use await progress_message instead of await message.edit
            await progress_message(text="{}\n{}".format(ud_type, tmp), reply_markup=InlineKeyboardMarkup(chance))         
        except:
            pass

def calculate_times(diff, current, total, speed):
    elapsed_time = TimeFormatter(milliseconds=round(diff) * 1000)
    time_to_completion = TimeFormatter(round((total - current) / speed) * 1000)
    estimated_total_time = elapsed_time + time_to_completion
    return elapsed_time, time_to_completion, estimated_total_time

def humanbytes(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
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
    tmp = (
        (f"{days}ᴅ, ") if days else ""
    ) + (
        (f"{hours}ʜ, ") if hours else ""
    ) + (
        (f"{minutes}ᴍ, ") if minutes else ""
    ) + (
        (f"{seconds}ꜱ, ") if seconds else ""
    ) + (
        (f"{milliseconds}ᴍꜱ, ") if milliseconds else ""
    )
    return tmp[:-2]
