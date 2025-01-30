import random
import glob
import os
from yt_dlp import YoutubeDL
from telethon import events
from Tepthon import zedub
from ..Config import Config

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
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredquality": "192",
        }],
        "outtmpl": "%(title)s.%(ext)s",
        "cookiefile": get_cookies_file(),
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            title = info['entries'][0]['title']
            filename = f"{title}.mp3"
            full_path = os.path.join(os.getcwd(), filename)

            await event.edit(f"⎉╎ تم العثـور علـى المطلـوب، جـاري إرسال الملـف ♥️..")

            if os.path.exists(full_path):
                caption = "⎉╎ تم التنزيـل : @Tepthon"
                await zedub.send_file(event.chat_id, full_path, caption=caption)
                os.remove(full_path)
                await event.edit("⎉╎ تم إرسال الملف بنجاح! 🎶")
            else:
                await event.edit("⎉╎ لم أتمكن من العثور على الملف الذي تم تحميله.")

    except Exception as e:
        await event.edit(f"⎉╎ حدث خطـأ: {e}")
