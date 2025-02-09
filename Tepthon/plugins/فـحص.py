import asyncio
from telethon import events
from Tepthon import zedub
from telethon.errors.rpcerrorlist import MediaEmptyError
from ..core.managers import edit_or_reply
from ..helpers.utils import _format

# متغير للتحكم في حالة حفظ البصمة الذاتية
vocself = True

# دالة لتفعيل حفظ الصوتيات الذاتية
@zedub.zed_cmd(pattern="(تفعيل البصمه الذاتيه|تفعيل البصمه الذاتية|تفعيل البصمة الذاتيه|تفعيل البصمة الذاتية)")
async def start_datea(event):
    global vocself

    if vocself:
        return await edit_or_reply(event, "⎉╎حفظ البصمة الذاتية التلقائي 🎙\n⎉╎مفعلـه .. مسبقًـا ✅")
    vocself = True
    await edit_or_reply(event, "⎉╎تم تفعيل حفظ البصمة الذاتية 🎙\n⎉╎تلقائيًّـا .. بنجاح ✅")

# دالة لإيقاف حفظ الصوتيات الذاتية
@zedub.zed_cmd(pattern="(ايقاف البصمه الذاتيه|ايقاف البصمه الذاتية|ايقاف البصمة الذاتيه|ايقاف البصمة الذاتية)")
async def stop_datea(event):
    global vocself
    
    if vocself:
        vocself = False
        return await edit_or_reply(event, "⎉╎تم تعطيل حفظ البصمة الذاتية 🎙\n⎉╎الان صارت مو شغالة .. ✅")
    await edit_or_reply(event, "⎉╎حفظ البصمة الذاتية التلقائي 🎙\n⎉╎معطلـه .. مسبقـاً ✅")

# دالة للاستماع للرسائل الصوتية الذاتية الجديدة وحفظها
@zedub.on(events.NewMessage(func=lambda e: e.is_private and (e.audio or e.voice) and e.media_unread))
async def sddm(event):
    global vocself

    if vocself:
        sender = await event.get_sender()
        username = f"@{sender.username}" if sender.username else "لا يوجد"
        try:
            voc = await event.download_media()  # تحميل الوسائط (الصوتيات)
            await zedub.send_file("me", voc, caption=f"[ᯓ 𝙏𝙀𝙋𝙏𝙃𝙊𝙉 ⌁ - حفـظ البصمـة الذاتية 🎙\n⋆─┄─┄─┄─┄─┄─┄─⋆\n⌔ مࢪحبـًا .. عـزيـزي 🫂\n⌔ تـم حفظ البصمة الذاتية .. تلقائيًّـا ☑️ ❝\n⌔ معلومـات المـرسـل :-\n• الاسم : {_format.mentionuser(sender.first_name , sender.id)}\n• اليوزر : {username}\n• الايدي : {sender.id}")
        except MediaEmptyError:
            await edit_or_reply(event, "⎉╎حدث خطأ أثناء حفظ الصوتية. يرجى المحاولة مجددًا.")

# ---------- تنبيه -----------
# تأكد من وجود متطلبات تشغيل البرنامج والإعدادات الصحيحة لـ Telethon
# يمكنك إضافة المزيد من الخصائص حسب الحاجة، مثل تعيين مسار التخزين أو معالجة الأخطاء

# مثال على استخدام الدوال
if __name__ == "__main__":
    # هنا يمكن إضافة كود لبدء البوت أو تشغيل الدوال
    pass
