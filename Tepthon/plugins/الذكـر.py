import asyncio
import random
from telethon import events
from Tepthon import zedub
from ..Config import Config

plugin_category = "الأذكار"

# قائمة بالأذكار والأدعية مع إضافة 20 أذكار جديدة
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
    "إن في خلق السماوات والأرض آيات",
    "اللهم إني أسألك الهدى والتقى والعفاف والغنى",
    "اللهم احفظني من كل سوء",
    "اللهم اجعل هذا اليوم خيراً لنا",
    "اللهم ارحم موتانا وموتى المسلمين",
    "اللهم اجعلنا من الذين يستمعون القول فيتبعون أحسنه",
    "اللهم أتنا في الدنيا حسنة وفي الآخرة حسنة",
    "اللهم اشرح صدورنا ويسر أمورنا",
    "اللهم اجعلنا من الذاكرين الشاكرين",
    "اللهم اغفر لي ولأمي وأبي وللمؤمنين",
    "اللهم اجعل لنا من كل هم فرجاً",
    "اللهم اجعلني من المتقين",
    "اللهم اغفر لي ولوالدي ولجميع المسلمين",
    "اللهم اهدني فيمن هديت",
    "اللهم انصر إخواننا في كل مكان"
]

# متغير للتحكم في حالة الأذكار
azkar_active = False
recent_azkar = []  # قائمة لتخزين الأذكار المرسلة مؤخراً

@zedub.on(events.NewMessage(pattern='\.تفعيل الاذكار'))
async def activate_azkar(event):
    global azkar_active, recent_azkar
    if event.sender_id != Config.OWNER_ID:
        return
    azkar_active = True  # تعيين المتغير إلى True عند تفعيل الأذكار
    recent_azkar = []  # إعادة تعيين قائمة الأذكار المرسلة
    await event.edit("✅ تم تفعيل الأذكار. سأرسل لك الأذكار كل 5 دقائق.")
    await asyncio.sleep(1)  # الانتظار لمدة ثانية قبل حذف الرسالة
    await event.delete()  # حذف الرسالة

    while azkar_active:
        await asyncio.sleep(300)  # الانتظار لمدة 5 دقائق
        
        # اختيار ذكر عشوائي غير مكرر
        available_azkar = [azkar for azkar in azkar_and_duas if azkar not in recent_azkar]
        if not available_azkar:
            recent_azkar = []  # إعادة تعيين القائمة إذا كانت جميع الأذكار قد تم استخدامها
            available_azkar = azkar_and_duas.copy()  # إعادة القائمة كاملة

        selected_azkar = random.choice(available_azkar)
        recent_azkar.append(selected_azkar)
        
        # إرسال الذكر
        await event.respond(selected_azkar)

        # حذف الذكر من القائمة بعد 5 دقائق
        await asyncio.sleep(300)
        recent_azkar.remove(selected_azkar)

@zedub.on(events.NewMessage(pattern='\.ايقاف الاذكار'))
async def deactivate_azkar(event):
    global azkar_active
    if event.sender_id != Config.OWNER_ID:
        return
    azkar_active = False  # تعيين المتغير إلى False عند تعطيل الأذكار
    await event.edit("⚠️ تم ايقاف الأذكار.")
    await asyncio.sleep(1)  # الانتظار لمدة ثانية قبل حذف الرسالة
    await event.delete()  # حذف الرسالة
