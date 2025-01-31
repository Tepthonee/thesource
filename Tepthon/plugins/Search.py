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
    
    await event.edit("⎉╎ جــاري البحــث عن المطلـوب 🎧..")

    # تعريف دالة hook هنا
    def hook(d):
        if d['status'] == 'finished':
            print(f"\nتم تحميل: {d['filename']}")

    ydl_opts = {
        "format": "bestaudio/best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": False,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
        ],
        "outtmpl": "%(title)s.%(ext)s",
        "progress_hooks": [hook],
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": get_cookies_file(),
        "ratelimit": 1000,  # تحديد معدل التحميل (يمكنك ضبط القيمة حسب السرعة عندك)
        "socket_timeout": 60,  # مهلة الاتصال
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            title = info['entries'][0]['title']
            filename = f"{title}.mp3"

            await event.edit(f"⎉╎ تم العثـور علـى المطلـوب، جـاري إرسال الملـف ♥️..")

            caption = "⎉╎ تم التنزيـل : @Tepthon"
            await zedub.send_file(event.chat_id, filename, caption=caption)

            os.remove(filename)

            await event.edit("⎉╎ تم إرسال الملف بنجاح! 🎶")
        except Exception as e:
            await event.edit(f"⎉╎ حدث خطـأ: {e}")
