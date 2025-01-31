import os
import glob
import random
import yt_dlp
from telethon import events
from Tepthon import zedub

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("لا توجد ملفات .txt في المجلد المحدد.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file

@zedub.on(events.NewMessage(pattern=r'\.بحث(?:\s|$)(.*)'))
async def search_song(event):
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.reply("**يجب عليك إدخال اسم المقطع الصوتي.**")

    # قراءة ملف الكوكيز عشوائياً
    try:
        cookies_file_path = get_cookies_file()
    except FileNotFoundError as e:
        return await event.reply(f"**خطأ: {e}**")

    # إنشاء مجلد التنزيلات إذا لم يكن موجوداً
    downloads_folder = './downloads'
    os.makedirs(downloads_folder, exist_ok=True)

    # إعداد خيارات yt-dlp مع البحث في يوتيوب
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': cookies_file_path,
        'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),  # استخدام المسار الصحيح
        'default_search': 'ytsearch',
        'noplaylist': True,  # تحميل مقطع واحد
    }

    # البحث وتحميل الصوت
    await event.reply("**جارِ البحث، يرجى الانتظار...**")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info)

            # التحقق من وجود الملف
            if not os.path.exists(filename):
                return await event.reply("**حدث خطأ: لم يتم العثور على الملف المحمل.**")
            
            # إرسال الملف
            await zedub.send_file(event.chat_id, filename, caption=f"تحميل: {info['title']}")
            
        except Exception as e:
            await event.reply(f"**حدث خطأ أثناء محاولة تحميل الصوت:** {e}")

    # حذف الملف بعد الإرسال
    if os.path.exists(filename):
        os.remove(filename)
