import os
import glob
import random
import yt_dlp
from Tepthon import zedub  

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
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

    # إعداد خيارات yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': cookies_file_path,
        'outtmpl': './downloads/%(title)s.%(ext)s',
    }

    # البحث وتحميل الصوت
    async with event.chat.client:
        await event.reply("**جارِ البحث، يرجى الانتظار...**")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=True)
                filename = ydl.prepare_filename(info)
                
                # إرسال الملف
                await event.client.send_file(event.chat_id, filename, caption=f"تحميل: {info['title']}")
                
            except Exception as e:
                await event.reply(f"**حدث خطأ أثناء محاولة تحميل الصوت:** {e}")

    # حذف الملف بعد الإرسال
    if os.path.exists(filename):
        os.remove(filename)
