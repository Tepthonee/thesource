import os
import yt_dlp
from telethon import events

@client.on(events.NewMessage(pattern=r'\.بحث(?:\s|$)(.*)'))
async def search_song(event):
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.reply("**يجب عليك إدخال اسم المقطع الصوتي.**")

    # قراءة الكوكيز من الملف
    cookies_file_path = 'rcookies/cozc.txt'
    if os.path.exists(cookies_file_path):
        with open(cookies_file_path, 'r') as file:
            cookies = file.read().strip()
    else:
        return await event.reply("**عذراً، لم أتمكن من العثور على ملف الكوكيز.**")

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
