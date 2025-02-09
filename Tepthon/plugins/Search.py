import os
import glob
import random
import asyncio
from telethon import events
from Tepthon import zedub
from pytube import YouTube
from pytube.helpers import safe_filename

# دالة لجلب ملف الكوكيز عشوائيًا
def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

# دالة لتحميل الصوت من يوتيوب
async def download_youtube_audio(url, cookies_file):
    # قراءة الكوكيز من الملف
    with open(cookies_file, 'r') as file:
        cookies = file.read()
    
    # تعيين الكوكيز
    YouTube.cipher = lambda: cookies
    yt = YouTube(url)

    # استخراج الصوت فقط
    stream = yt.streams.filter(only_audio=True).first()
    
    # تحميل الصوت
    file_path = stream.download(filename=safe_filename(yt.title) + '.mp4')
    return file_path

# حدث للاستجابة لأمر البحث
@zedub.on(events.NewMessage(pattern=r'\.بحث (.+)'))
async def search_youtube(event):
    url = event.pattern_match.group(1)
    
    await event.respond("جاري تحميل الصوت...")
    
    try:
        # جلب ملف الكوكيز
        cookies_file = get_cookies_file()
        if not cookies_file:
            await event.respond("لم يتم العثور على ملفات الكوكيز.")
            return
        
        audio_file = await download_youtube_audio(url, cookies_file)
        
        await event.respond("تم تنزيل الصوت بنجاح!", file=audio_file)
        
    except Exception as e:
        await event.respond(f"حدثت مشكلة أثناء التنزيل: {str(e)}")

# ابدأ هنا البوت أو أي إعدادات أخرى
if __name__ == "__main__":
    # تأكد من إضافة كود بدء البوت هنا
    pass
