from telethon.errors.rpcerrorlist import MediaEmptyError
from Tepthon import zedub

vocSelf = True

def isSong(v):
    return False 

@zedub.on(events.NewMessage(pattern="(تفعيل البصمه|فع البصمه)"))
async def strtVocSav(evn):
    global vocSelf
    if vocSelf:
        return await evn.reply("حفظ البصمه شغال من قبل 🎙✅")
    vocSelf = True
    await evn.reply("تم تشغيل حفظ البصمه تلقائي 🎙✅")

@zedub.on(events.NewMessage(pattern="(ايقاف البصمه|اقف البصمه)"))
async def stpVocSav(evn):
    global vocSelf
    if not vocSelf:
        return await evn.reply("حفظ البصمه معطل من قبل 🎙❌")
    vocSelf = False
    await evn.reply("تم تعطيل حفظ البصمه 🎙❌")

@zedub.on(events.NewMessage(func=lambda e: e.is_private and e.voice and e.media_unread))
async def savVoc(evn):
    global vocSelf
    if not vocSelf:
        return
    snd = await evn.get_sender()
    us = f"@{snd.username}" if snd.username else "لا يـوجـد"
    try:
        if not isSong(evn.voice):
            pth = await evn.download_media(file="voicemsgs/")
            await zedub.send_file(
                "me",
                pth,
                caption=f"تم حفظ البصمه تلقائي 🎙✅\n\n"
                f"المرسل: {snd.first_name} ({snd.id})\n"
                f"اليوزر: {us}\n"
                f"الايدي: {snd.id}",
            )
    except MediaEmptyError:
        await evn.reply("حصل مشكله وقت الحفظ، جرب تاني.")
    except Exception as ex:
        await evn.reply(f"حصل خطأ: {str(ex)}")
