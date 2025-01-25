import random
import glob
import os
from yt_dlp import YoutubeDL
from Tepthon import zedub
from telethon import events
from ..Config import Config

plugin_category = "البوت"

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file

@zedub.on(events.NewMessage(pattern='.انستا (.*)'))
async def download_video(event):
    if event.sender_id != Config.OWNER_ID:  # استبدل Config.OWNER_ID بمعرف صاحب الحساب
        return
    
    video_url = event.pattern_match.group(1)
    await event.reply(f"جاري تحميل الفيديو من الرابط: {video_url}...")

    # إعداد خيارات yt-dlp
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegVideoConvert",  # تحويل الفيديو إلى صيغة محددة إذا لزم الأمر
            "preferedformat": "mp4",
        }],
        "outtmpl": "%(title)s.%(ext)s",
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": get_cookies_file(),
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=True)
            title = info['title']
            filename = f"{title}.mp4"

            await event.reply(f"تم تحميل الفيديو: {title}، جاري إرسال الملف...")

            # إرسال الملف إلى تيليجرام
            await zedub.send_file(event.chat_id, filename)

            # حذف الملف بعد الإرسال
            os.remove(filename)
        except Exception as e:
            await event.reply(f"حدث خطأ أثناء تحميل الفيديو: {e}")
