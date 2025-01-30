import random
import glob
import asyncio
import yt_dlp
import os
from telethon import TelegramClient, events
from yt_dlp import YoutubeDL
from Tepthon import zedub
from ..Config import Config

plugin_category = "البوت"

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
    
    await event.edit("**⎉╎ جــاري البحــث عن المطلـوب 🎧..**")

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
        ],
        "outtmpl": "%(title)s.%(ext)s",
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": get_cookies_file(),
        # إلغاء تفعيل حد حجم الملف
        # "max_filesize": "50M", # عين الحجم الذي تريده أو ألغ هذا السطر
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            title = info['entries'][0]['title']
            filename = f"{title}.mp3"

            await event.edit(f"**⎉╎ تم العثـور علـى المطلـوب، جـاري إرسال الملـف ♥️..**")

            caption = "**⎉╎ تم التنزيـل : @Tepthon**"
            await zedub.send_file(event.chat_id, filename, caption=caption)

            os.remove(filename)

            await event.edit("**⎉╎ تم إرسال الملف بنجاح! 🎶**")
        except Exception as e:
            await event.edit(f"**⎉╎ حدث خطـأ: {e}**")
