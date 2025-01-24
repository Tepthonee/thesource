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
async def search_video(event):
    # تحقق مما إذا كان المرسل هو الحساب المنصب فقط
    if event.sender_id != Config.OWNER_ID:
        return

    search_query = event.pattern_match.group(1)
    await event.reply(f"࿊ جاري البحث عن: {search_query}...")

    # إعداد خيارات yt-dlp للبحث
    ydl_opts = {
        "format": "best",
        "noplaylist": True,  # عدم تنزيل قوائم التشغيل
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch10:{search_query}", download=False)['entries']
            if results:
                reply_message = "نتائج البحث:\n"
                for idx, video in enumerate(results, 1):
                    title = video['title']
                    url = video['url']
                    reply_message += f"{idx}. {title} - {url}\n"

                await event.reply(reply_message)
            else:
                await event.reply("لم يتم العثور على فيديوهات متطابقة.")
        except Exception as e:
            await event.reply(f"حدث خطأ أثناء البحث: {e}")
