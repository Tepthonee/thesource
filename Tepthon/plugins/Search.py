import random
import glob
import os
from yt_dlp import YoutubeDL
from telethon import events
from Tepthon import zedub
from telethon.tl.types import InputMessagesFilterVideo

# دالة للحصول على ملف الكوكيز بشكل عشوائي
def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    return random.choice(txt_files)

# التفاعل مع الأمر .بحث لتحميل الفيديو
@zedub.on(events.NewMessage(pattern='.بحث (.*)'))
async def get_video(event):
    search_query = event.pattern_match.group(1)

    await event.edit("⎉╎ جــاري البحــث عن المطلـوب 🎥..")

    ydl_opts = {
        "format": "best",
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegVideoConvertSegment",
            "preferedformat": "mp4",
            "outtmpl": "%(title)s.%(ext)s"
        }],
        "cookiefile": get_cookies_file(),
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search_query}", download=True)
            title = info['entries'][0]['title']
            filename = f"{title}.mp4"

            if os.path.exists(filename):
                await event.edit(f"⎉╎ تم العثـور علـى المطلـوب، جـاري إرسال الملـف ♥️..")
                caption = "⎉╎ تم التنزيـل : @Tepthon"
                await zedub.send_file(event.chat_id, filename, caption=caption)

                os.remove(filename)  # حذف الملف بعد الإرسال
                await event.edit("⎉╎ تم إرسال الملف بنجاح! 🎶")
            else:
                await event.edit("⎉╎ لم يتم العثور على الملف بعد التحميل.")
    except Exception as e:
        await event.edit(f"⎉╎ حدث خطـأ: {e}")
