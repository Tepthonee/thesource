import random
import glob
import os
from yt_dlp import YoutubeDL
from Tepthon import zedub
from telethon import events

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    return random.choice(txt_files)

@zedub.on(events.NewMessage(pattern='.بحث (.*)'))
async def get_song(event):
    song_name = event.pattern_match.group(1)
    
    await event.edit("⎉╎ جــاري البحــث عن المطلـوب 🎧..")

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
                "preferredquality": "192",
            },
            {"key": "FFmpegMetadata"},
        ],
        "outtmpl": "%(title)s.%(ext)s",
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": get_cookies_file(),
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            title = info['entries'][0]['title']
            filename = f"{title}.mp3"
            print(f"اسم الملف الناتج: {filename}")

            if os.path.exists(filename):
                await event.edit(f"⎉╎ تم العثـور علـى المطلـوب، جـاري إرسال الملـف ♥️..")
                caption = "⎉╎ تم التنزيـل : @Tepthon"
                await zedub.send_file(event.chat_id, filename, caption=caption)

                os.remove(filename)
                await event.edit("⎉╎ تم إرسال الملف بنجاح! 🎶")
            else:
                await event.edit("⎉╎ لم يتم العثور على الملف بعد التحميل.")
    except Exception as e:
        await event.edit(f"⎉╎ حدث خطـأ: {e}")
