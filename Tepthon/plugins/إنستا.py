import requests
from bs4 import BeautifulSoup
from telethon import events
from Tepthon import zedub
from ..Config import Config

plugin_category = "البوت"

@zedub.on(events.NewMessage(pattern='.انستا (.*)'))
async def download_video(event):
    if event.sender_id != Config.OWNER_ID:  # استبدل Config.OWNER_ID بمعرف صاحب الحساب
        return
    
    video_url = event.pattern_match.group(1)
    await event.reply(f"جاري تحميل الفيديو من الرابط: {video_url}...")

    try:
        response = requests.get(video_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # العثور على عنصر الفيديو
        video_tag = soup.find('video')
        if video_tag and video_tag.get('src'):
            video_src = video_tag['src']
            video_response = requests.get(video_src)
            filename = 'video.mp4'

            with open(filename, 'wb') as f:
                f.write(video_response.content)

            await event.reply(f"تم تحميل الفيديو، جاري إرسال الملف...")
            await zedub.send_file(event.chat_id, filename)

            # حذف الملف بعد الإرسال
            os.remove(filename)
        else:
            await event.reply("لم أتمكن من العثور على رابط الفيديو.")
    except Exception as e:
        await event.reply(f"حدث خطأ أثناء تحميل الفيديو: {e}")
