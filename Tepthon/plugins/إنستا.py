import os
from telethon import events
from instaloader import Instaloader, Post
from Tepthon import zedub
from ..Config import Config

plugin_category = "البوت"

# تهيئة Instaloader
loader = Instaloader()

@zedub.on(events.NewMessage(pattern='.انستا (.*)'))
async def download_instagram_video(event):
    # تحقق مما إذا كان المرسل هو الحساب المنصب فقط
    if event.sender_id != Config.OWNER_ID:  # استبدل Config.OWNER_ID بمعرف صاحب الحساب
        return

    post_url = event.pattern_match.group(1)
    await event.reply(f"جاري تحميل الفيديو من الرابط: {post_url}...")

    try:
        # استخراج جزء shortcode من الرابط
        shortcode = post_url.split("/")[-2]
        post = Post.from_shortcode(loader.context, shortcode)

        if post.is_video:  # تحقق من كون المنشور فيديو
            filename = f"{shortcode}.mp4"  # اسم الملف الذي سيتم حفظه

            # تحميل الفيديو
            loader.download_post(post, target=filename)

            await event.reply(f"تم تحميل الفيديو بنجاح: {post.title}\n⇜ جاري إرسال الملف...")

            # إرسال الملف إلى تيليجرام
            await zedub.send_file(event.chat_id, filename)

            # حذف الملف بعد الإرسال
            os.remove(filename)
        else:
            await event.reply("❌ هذا المنشور ليس فيديو.")
    except Exception as e:
        await event.reply(f"خطأ ❌: {e}")
