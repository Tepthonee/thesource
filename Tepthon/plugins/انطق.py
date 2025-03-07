import os
from gtts import gTTS
from Tepthon import zedub
from telethon import events
from ..Config import Config

plugin_category = "البوت"

@zedub.on(events.NewMessage(pattern='.انطق (.*)'))
async def speak_word(event):
    text_to_speak = event.pattern_match.group(1)
    language = 'ar'  # اللغة الافتراضية، يمكنك تعديلها حسب الحاجة

    await event.reply(f"🗣️ جاري نطق: **{text_to_speak}**...")

    try:
        # تحديد اللغة بناءً على محتوى النص
        if any(char in text_to_speak for char in ['ع', 'أ', 'ب', 'ت', 'ث']):  # إذا كان هناك أحرف عربية
            language = 'ar'
        elif any(char in text_to_speak for char in ['a', 'b', 'c', 'd', 'e']):  # إذا كان هناك أحرف إنجليزية
            language = 'en'
        elif any(char in text_to_speak for char in ['a', 'à', 'é', 'è']):  # إذا كان هناك أحرف فرنسية
            language = 'fr'
        elif any(char in text_to_speak for char in ['ह', 'ब', 'क', 'ख']):  # إذا كان هناك أحرف هندية
            language = 'hi'

        tts = gTTS(text=text_to_speak, lang=language)
        filename = f"output_{language}.mp3"
        tts.save(filename)

        await event.reply("🔊 جاري إرسال الصوت...")
        await zedub.send_file(event.chat_id, filename)

        # حذف الملف بعد إرساله
        os.remove(filename)

    except Exception as e:
        await event.reply(f"🚫 حدث خطأ أثناء نطق الكلمات: {e}")
