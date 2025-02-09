import os
import requests
import yt_dlp
from telethon import TelegramClient, events
from youtube_search import YoutubeSearch as B3KKK
from Tepthon import zedub
import glob
import random

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file

@zedub.on(events.NewMessage(pattern=".يوتيوب"))
async def srchDl(e):
    try:
        txt = e.raw_text.split()
        if len(txt) < 2:
            await e.reply("اكتب اسم الفيديو بعد الامر.")
            return
        q = txt[1]
        res = B3KKK(q, max_results=1).to_dict()  # تأكد من أن zedub معرف بشكل صحيح
        if not res:
            await e.reply("ما لقيتش حاجة 😢")
            return
        vid = res[0]
        ttl = vid["title"]
        id = vid["id"]
        lnk = f"https://youtu.be/{id}"
        await e.reply(f"بيتم التحميل يا باشا: {ttl}")
        
        opts = {
            "format": "bestaudio/best",
            "cookiefile": get_cookies_file(),
            "noplaylist": True
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(lnk, download=False)
        
        if int(info["duration"]) > 3605:
            await e.reply("طول الفيديو كبير اوي، مش هنقدر نحمله 🙄")
            return

        # تحديث التنسيق المستخدم لتفادي الأخطاء
        opts['format'] = 'bestaudio[ext=m4a]/bestaudio'
        
        audio_file = ydl.prepare_filename(info)
        ydl.download([lnk])
        
        thb = info["thumbnail"]
        thbFile = f"{id}.png"
        r = requests.get(thb)
        with open(thbFile, "wb") as f:
            f.write(r.content)
        
        await zedub.send_file(
            e.chat_id,
            audio_file,
            title=info["title"],
            performer=info["channel"],
            duration=int(info["duration"]),
            thumb=thbFile,
        )

        os.remove(thbFile)
        os.remove(audio_file)
    except Exception as ex:
        await e.reply(f"حصل خطأ: {str(ex)}")
