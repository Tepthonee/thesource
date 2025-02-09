import os
import glob
import random
import asyncio
from telethon import events
from telethon.sync import TelegramClient
from Tepthon import zedub
from pytube import YouTube

# دالة لجلب ملف الكوكيز عشوائيًا
def get_cookies_file():
    folder_path = os.path.join(os.getcwd(), "rcookies")
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

# دالة لتحميل الصوت من يوتيوب
async def download_youtube_audio(url, cookies_file):
    # قراءة الكوكيز من الملف
    with open(cookies_file, 'r') as file:
        cookies = file.read()

    try:
        yt = YouTube(url, use_oauth=False, allow_oauth_cache=True)
        stream = yt.streams.filter(only_audio=True).first()
        if not stream:
            raise ValueError("لا يوجد مصدر صوت متاح لهذا الفيديو.")

        # تحديد اسم الملف
        output_path = "downloads"
        os.makedirs(output_path, exist_ok=True)
        file_name = f"{yt.title}.mp3"
        file_path = stream.download(output_path=output_path, filename=file_name)
        
        return file_path

    except Exception as e:
        raise ValueError("رابط الفيديو غير صحيح أو غير متوفر.") from e

# حدث للاستجابة لأمر البحث
@zedub.on(events.NewMessage(pattern=r'\.بحث (.+)'))  # استبدال client بـ zedub
async def search_youtube(event):
    url = event.pattern_match.group(1).strip()  # إزالة المسافات الزائدة
    
    await event.respond("جاري تحميل الصوت...")
    
    try:
        # جلب ملف الكوكيز
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
