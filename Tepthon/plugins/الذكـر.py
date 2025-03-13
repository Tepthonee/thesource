import asyncio
import random
from telethon import events
from Tepthon import zedub
from ..Config import Config

plugin_category = "الأذكار"

# قائمة بالأذكار والأدعية
azkar_and_duas = [
    "سبحان الله",
    "الحمد لله",
    "لا إله إلّا الله",
    "اللهم أبعد عنا الداء",
    "أستغفر الله",
    "اللهم صلّ وسلم على نبينا محمد",
    "اللهم ارزقني رحمتك",
    "إن الله مع الصابرين",
    "بسم الله الرحمن الرحيم",
    "اللهم اجعلنا من اهل الجنة",
    "لا حول ولاقوة الا بالله",
    "الحمد لله رب العالمين",
    "رب اغفر لي وارحمني",
    "اللهم إنّي أسألك العفو والعافية",
    "اللهم ألهمني رشدي وأعدني من شر نفسي",
    "اللهم اجعلني من الصالحين",
    "أعظم الله أجركم",
    "إن في خلق السماوات والأرض",
    "اللهم إني أسألك الهدى والتقى والعفاف والغنى",
    "اللهم احفظني من كل سوء",
    "اللهم اجعل هذا اليوم خيراً لنا"
]

# متغير للتحكم في حالة الأذكار
azkar_active = False

@zedub.on(events.NewMessage(pattern='\.تفعيل الاذكار'))
async def activate_azkar(event):
    global azkar_active
    if event.sender_id != Config.OWNER_ID:
        return
    azkar_active = True  # تعيين المتغير إلى True عند تفعيل الأذكار
    await event.reply("✅ تم تفعيل الأذكار. سأرسل لك الأذكار كل 5 دقائق.")
    
    while azkar_active:
        await asyncio.sleep(300)  # الانتظار لمدة 5 دقائق
        # إرسال ذكر عشوائي
        await event.reply(azkar_and_duas[random.randint(0, len(azkar_and_duas) - 1)])

@zedub.on(events.NewMessage(pattern='\.تعطيل الاذكار'))
async def deactivate_azkar(event):
    global azkar_active
    if event.sender_id != Config.OWNER_ID:
        return
    azkar_active = False  # تعيين المتغير إلى False عند تعطيل الأذكار
    await event.reply("⚠️ تم تعطيل الأذكار.")
