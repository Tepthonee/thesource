from telethon.errors.rpcerrorlist import MediaEmptyError
from Tepthon import zedub

vocSelf = True

def isSong(v):
    return False 

@zedub.on(events.NewMessage(pattern="(تفعيل البصمه|فع البصمه)"))
async def strtVocSav(event):
    global vocSelf
    if vocSelf:
        return await event.edit("حفظ البصمه شغال من قبل 🎙✅")
    vocSelf = True
    await event.edit("تم تشغيل حفظ البصمه تلقائي 🎙✅")

@zedub.on(events.NewMessage(pattern="(ايقاف البصمه|اقف البصمه)"))
async def stpVocSav(event):
    global vocSelf
    if not vocSelf:
        return await event.edit("حفظ البصمه معطل من قبل 🎙❌")
    vocSelf = False
    await event.edit("تم تعطيل حفظ البصمه 🎙❌")

@zedub.on(events.NewMessage(func=lambda e: e.is_private and e.voice and e.media_unread))
async def savVoc(event):
    global vocSelf
    if not vocSelf:
        return
    snd = await event.get_sender()
    us = f"@{snd.username}" if snd.username else "لا يـوجـد"
    try:
        if not isSong(event.voice):
            pth = await event.download_media(file="voicemsgs/")
            await zedub.send_file(
                "me",
                pth,
                caption=f"تم حفظ البصمه تلقائي 🎙✅\n\n"
                f"المرسل: {snd.first_name} ({snd.id})\n"
                f"اليوزر: {us}\n"
                f"الايدي: {snd.id}",
            )
    except MediaEmptyError:
        await event.edit("حصل مشكله وقت الحفظ، جرب تاني.")
    except Exception as ex:
        await event.edit(f"حصل خطأ: {str(ex)}")
