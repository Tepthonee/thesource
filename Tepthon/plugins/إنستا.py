import requests
from bs4 import BeautifulSoup
from telethon import events
from Tepthon import zedub
from ..Config import Config
import json
import os

plugin_category = "البوت"

@zedub.on(events.NewMessage(pattern='.انستا (.*)'))
async def download_video(event):
    if event.sender_id != Config.OWNER_ID:  # استبدل Config.OWNER_ID بمعرف صاحب الحساب
        return
    
    video_url = event.pattern_match.group(1)
    await event.reply(f"جاري تحميل الفيديو من الرابط: {video_url}...")

    try:
        response = requests.get(video_url)
        if response.status_code != 200:
            await event.reply("فشل في الوصول إلى الرابط. تأكد من أنه صالح.")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # البحث عن السكربت الذي يحتوي على البيانات
        scripts = soup.find_all('script')
        video_url = None

        for script in scripts:
            if 'window._sharedData =' in str(script):
                shared_data = str(script).split('window._sharedData = ')[1].split(';</script>')[0]
                json_data = json.loads(shared_data)

                # البحث عن فيديو إذا كان موجودًا
                try:
                    media = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
                    if media['is_video']:
                        video_url = media['video_url']
                except KeyError:
                    continue

                break

        if video_url:
            video_response = requests.get(video_url)
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
