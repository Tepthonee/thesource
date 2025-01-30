from telethon import TelegramClient, events
from Tepthon import zedub 
from telethon.errors import YouBlockedUserError
from ShazamAPI import Shazam
import io
import logging
from ..Config import Config  # استدعاء الإعدادات

# إعدادات تسجيل الأخطاء
LOGS = logging.getLogger(__name__)

# إعداد عميل تيليجرام باستخدام api_id و api_hash من Config
zedub = TelegramClient("zedub", api_id=Config.APP_ID, api_hash=Config.API_HASH)

@zedub.on(events.NewMessage(pattern='بحث(?:\\ع|$)([\\s\\S]*)'))
async def shazamcmd(event):
    "To reverse search song."
    
    reply = await event.get_reply_message()
    mediatype = reply.media
    chat = "@DeezerMusicBot"
    delete = False
    flag = event.pattern_match.group(1)

    if not reply or not mediatype or mediatype not in ["voice", "audio"]:
        return await event.reply("- بالــرد ع مقـعـط صـوتي")

    zedevent = await event.reply("- جـار تحميـل المقـطع الصـوتي ...")
    name = "zed.mp3"

    try:
        # تحميل الملف
        await zedub.download_media(reply.media, name)
        
        # التعرف على الأغنية
        with open(name, "rb") as f:
            shazam = Shazam(f.read())
            recognize_generator = shazam.recognizeSong()
            track = next(recognize_generator)[1]["track"]
    except Exception as e:
        LOGS.error(e)
        return await zedevent.edit(f"- خطـأ :\n{e}")

    file = track["images"]["background"]
    title = track["share"]["subject"]
    
    # هنا قد تحتاج لتنفيذ دالة yt_search
    slink = await yt_search(title)  # تأكد من تعريف هذه الدالة في مكان ما بالأعلى

    if flag == "s":
        deezer = track["hub"]["providers"][1]["actions"][0]["uri"][15:]
        async with zedub.conversation(chat) as conv:
            try:
                await conv.send_message("/start")
                await conv.get_response()
                await conv.send_message(deezer)
                await conv.get_response()
                file = await conv.get_response()
                delete = True
            except YouBlockedUserError:
                await zedub.send_message(chat, "/start")
                await conv.get_response()
                await conv.send_message(deezer)
                await conv.get_response()
                file = await conv.get_response()
                delete = True

    await event.reply(
        f"<b>⎉╎ المقطـع الصـوتي :</b> <code>{title}</code>\n<b>⎉╎ الرابـط : <a href = {slink}/1>YouTube</a></b>",
        file=file,
        parse_mode='html',
    )
    await zedevent.delete()
    if delete:
        await zedub.send_message(chat, "/stop")  # نظف المحادثة إذا كنت بحاجة لذلك 

# شغل العميل 
zedub.start()
zedub.run_until_disconnected()
