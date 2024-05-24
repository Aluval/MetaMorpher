


# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
from pyrogram.types import *
import math
import time

PROGRESS_BAR = "\n\n📁 : {b} | {c}\n🚀 : {a}%\n⚡ : {d}/s\n⏱️ : {f}"

# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def progress(current, total, event, start, type_of_ps, file=None):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        elapsed_time_str = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time_str = TimeFormatter(milliseconds=estimated_total_time)
        progress = "\n{0}{1}".format(
            ''.join(["❤" for _ in range(math.floor(percentage / 5))]),
            ''.join(["♡" for _ in range(20 - math.floor(percentage / 5))])
        )
        tmp = progress + PROGRESS_BAR.format(
            a=round(percentage, 2),
            b=humanbytes(current),
            c=humanbytes(total),
            d=humanbytes(speed),
            f=estimated_total_time_str if estimated_total_time_str != '' else "0 s"
        )
        try:
            chance = [[InlineKeyboardButton("🚫 Cancel", callback_data="del")]]
            if file:
                await event.edit(
                    "✦ {}\n\nFile Name: {}\n\n{}".format(type_of_ps, file, tmp),
                    reply_markup=InlineKeyboardMarkup(chance)
                )
            else:
                await event.edit(
                    "✦ {}\n\n{}".format(type_of_ps, tmp),
                    reply_markup=InlineKeyboardMarkup(chance)
                )
        except Exception as e:
            print(f"An error occurred: {e}")

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
