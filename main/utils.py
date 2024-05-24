


# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
from pyrogram.types import *
import math
import time

PROGRESS_BAR = "\n\n📁 : {b} | {c}\n🚀 : {a}%\n⚡ : {d}/s\n⏱️ : {f}"

# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def progress_message(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = (total - current) / speed
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=time_to_completion * 1000)
        progress = "\n{0}{1}".format(
            ''.join(["✦" for i in range(math.floor(percentage / 5))]),
            ''.join(["✧" for i in range(20 - math.floor(percentage / 5))]))
        tmp = f"✦ {ud_type}\n\n{progress} {percentage:.2f}%\n\n{humanbytes(current)} of {humanbytes(total)}\n\n✦ Speed: {humanbytes(speed)}\n\n✦ ETA: {estimated_total_time}"                              
        try:
            await message.edit(text=tmp)
            await asyncio.sleep(5)  # Wait for 5 seconds before updating again
        except Exception as e:
            print(f"Error updating progress: {e}")
            
# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
def humanbytes(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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
