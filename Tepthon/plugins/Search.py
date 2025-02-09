import os
import glob
import random
import asyncio
from telethon import events, TelegramClient
from pytube import YouTube
from Tepthon import zedub  # تأكد من أن مكتبة zedub متوفرة لديك
from pytube.helpers import safe_filename
from config import APP_ID, API_HASH  # استيراد APP_ID و API_HASH من ملف الإعدادات

# إنشاء عميل تيليجرام بدون session_name
client = TelegramClient('client', APP_ID, API_HASH)

# دالة لجلب ملف الكوكيز عشوائيًا
def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

# دالة لتحميل الصوت من يوتيوب
async def download_youtube_audio(url, cookies_file):
    with open(cookies_file, 'r') as file:
        cookies = file.read()
    
    YouTube.cipher = lambda: cookies

    try:
        yt = YouTube(url)
    except Exception as e:
        raise ValueError("رابط الفيديو غير صحيح أو غير متوفر.") from e

    stream = yt.streams.filter(only_audio=True).first()
    if not stream:
        raise ValueError("لا يوجد مصدر صوت متاح لهذا الفيديو.")

    file_path = stream.download(filename=safe_filename(yt.title) + '.mp4')
    return file_path

# حدث للاستجابة لأمر البحث
@zedub.on(events.NewMessage(pattern=r'\.بحث (.+)'))
async def search_youtube(event):
    url = event.pattern_match.group(1).strip()
    
    await event.respond("جاري تحميل الصوت...")
    
    try:
        cookies_file = get_cookies_file()
        if not cookies_file:
            await event.respond("لم يتم العثور على ملفات الكوكيز.")
            return
        
        audio_file = await download_youtube_audio(url, cookies_file)
        
        await event.respond("تم تنزيل الصوت بنجاح!", file=audio_file)
        
    except ValueError as ve:
        await event.respond(f"خطأ: {str(ve)}")
    except Exception as e:
        await event.respond(f"حدثت مشكلة أثناء التنزيل: {str(e)}")

if __name__ == "__main__":  # يمكنك تصحيح هذا السطر بكتابة __name__ بشكل صحيح
    client.start()
    client.run_until_disconnected()
