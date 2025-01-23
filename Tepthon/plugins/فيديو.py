import random
import glob
import asyncio
import yt_dlp
from Tepthon import zedub
import os
from telethon import events
from telethon import Button
from yt_dlp import YoutubeDL
from ..Config import Config

plugin_category = "البوت"

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file

@zedub.on(events.NewMessage(pattern='.تحميل (.*)'))
async def download_video(event):
    # تحقق مما إذا كان المستخدم هو صاحب الحساب
    if event.sender_id != Config.OWNER_ID:  # استبدل Config.OWNER_ID بمعرف صاحب الحساب
        return

    video_name = event.pattern_match.group(1)
    await event.reply(f"جاري البحث عن الفيديو المطلوب: {video_name}...")

    # إعداد خيارات yt-dlp لتحميل الفيديو
    ydl_opts = {
        "format": "best",
        "outtmpl": "%(title)s.%(ext)s",
        "cookiefile": get_cookies_file(),
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{video_name}", download=False)  # لا تقم بالتنزيل هنا
            title = info['entries'][0]['title']
            filename = f"{title}.mp4"

            # أزرار لاختيار ما يريده الباحث
            buttons = [
                [Button.inline("تحميل الفيديو", data=f"download_{title}")],
                [Button.inline("إلغاء", data="cancel")]
            ]

            await event.reply(f"تم العثور على الفيديو المطلوب: {title}\nاختر الإجراء:", buttons=buttons)

        except Exception as e:
            await event.reply(f"حدث خطأ أثناء البحث عن الفيديو: {e}")

@zedub.on(events.CallbackQuery(data=lambda data: data.startswith(b'download_')))
async def on_download_button(event):
    title = event.data.decode('utf-8').replace('download_', '')
    
    # إعداد خيارات yt-dlp لتحميل الفيديو مرة أخرى
    ydl_opts = {
        "format": "best",
        "outtmpl": f"{title}.mp4",
        "cookiefile": get_cookies_file(),
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            await event.respond(f"جاري تحميل الفيديو: {title}...")
            ydl.download([f"ytsearch:{title}"])  # تحميل الفيديو

            # إرسال الملف إلى تيليجرام
            await zedub.send_file(event.chat_id, f"{title}.mp4")

            # حذف الملف بعد الإرسال
            os.remove(f"{title}.mp4")
            await event.respond("تم إرسال الفيديو بنجاح!")

        except Exception as e:
            await event.respond(f"حدث خطأ أثناء تحميل الفيديو: {e}")

@zedub.on(events.CallbackQuery(data="cancel"))
async def on_cancel(event):
    await event.respond("تم إلغاء العملية.")
