import os
import random
import glob
import yt_dlp
from telethon import events
from Tepthon import zedub

# دالة لاختيار ملف كوكيز عشوائي
def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

@zedub.on(events.NewMessage(pattern='.بحث (.*)'))
async def get_song(event):
    song_name = event.pattern_match.group(1)
    await event.edit("**⎉╎ جــاري البحــث عن المطلـوب 🎧..**")

    # إنشاء مجلد التحميل
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)

    # إعدادات yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "paths": {"home": download_path},
        "addmetadata": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
            {"key": "FFmpegMetadata"},
        ],
        "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
        "cookiefile": get_cookies_file(),
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            entries = info.get('entries', [])
            if not entries:
                await event.edit("**⎉╎ لم يتم العثــور على نتائج 🥹**")
                return
            
            # الحصول على بيانات الفيديو
            video = entries[0]
            title = video.get('title', 'عنوان غير معروف')
            filename = os.path.join(download_path, f"{title}.mp3")

            # التحقق من وجود الملف بعد تحميله
            if not os.path.exists(filename):
                await event.edit("**⎉╎ خطــأ: لم يتم العثور على الملف بعد التحميل**")
                return

            await event.edit(f"**⎉╎ تم العثور على المطلـوب، جاري الإرسـال..**")

            # إرسال الملف
            caption = f"**⎉╎ تم التنزيل: {title} ♥️\n⎉╎ بواسطـة: @Tepthon**"
            await zedub.send_file(event.chat_id, filename, caption=caption)

            # حذف الملف بعد الإرسال
            os.remove(filename)

            await event.edit("**⎉╎ تم الإرسال بنجاح! ✅**")
        except Exception as e:
            await event.edit(f"**⎉╎ حدث خطأ: {str(e)}**")
