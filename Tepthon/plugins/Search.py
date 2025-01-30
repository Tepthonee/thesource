import random
import glob
import asyncio
import yt_dlp
import os
from telethon import TelegramClient, events
from yt_dlp import YoutubeDL
from Tepthon import zedub
from ..Config import Config

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file

@zedub.on(events.NewMessage(pattern='.بحث (.*)'))
async def get_song(event):
    song_name = event.pattern_match.group(1)
    
    # تعديل الرسالة الأصلية
    await event.edit("**⎉╎ جــاري البحــث عن المطلـوب 🎧..**")

    # إعداد خيارات yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": False,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp3"},
            {"key": "FFmpegMetadata"},
            {"key": "FFmpegExtractAudio"},
        ],
        "outtmpl": "%(title)s.%(ext)s",
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": get_cookies_file(),
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            title = info['entries'][0]['title']
            filename = f"{title}.mp3"

            # تعديل الرسالة مرة أخرى
            await event.edit(f"**⎉╎ تم العثـور علـى المطلـوب، جـاري إرسال الملـف ♥️..**")

            # إرسال الملف مع وصف
            caption = "**⎉╎ تم التنزيـل : @Tepthon**"
            await zedub.send_file(event.chat_id, filename, caption=caption)

            # حذف الملف بعد الإرسال
            os.remove(filename)

            # تعديل الرسالة النهائية
            await event.edit("**⎉╎ تم إرسال الملف بنجاح! 🎶**")
        except Exception as e:
            await event.edit(f"**⎉╎ حدث خطـأ: {e}**")
