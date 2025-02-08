import os
import random
import glob
import yt_dlp
from telethon import events
from Tepthon import zedub

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

@zedub.on(events.NewMessage(pattern='.بحث (.*)'))
async def get_song(event):
    song_name = event.pattern_match.group(1)
    await event.edit("**⎉╎ جــاري البحــث عن المطلـوب 🎧..**")

    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "paths": {"home": download_path},
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
            
            video = entries[0]
            title = video.get('title', 'عنوان غير معروف')
            expected_filename = os.path.join(download_path, f"{title}.m4a")  # تأكد من امتداد الملف

            if os.path.exists(expected_filename):
                filename = expected_filename

                await event.edit(f"**⎉╎ تم العثور على المطلـوب، جاري الإرسـال..**")
                caption = f"**⎉╎ تم التنزيل: {title} ♥️\n⎉╎ بواسطـة: @Tepthon**"
                await zedub.send_file(event.chat_id, filename, caption=caption)

                os.remove(filename)
                await event.edit("**⎉╎ تم الإرسال بنجاح! ✅**")
            else:
                await event.edit("**⎉╎ خطــأ: لم يتم العثور على الملف بعد التحميل**")
        except Exception as e:
            await event.edit(f"**⎉╎ حدث خطأ: {str(e)}**")
