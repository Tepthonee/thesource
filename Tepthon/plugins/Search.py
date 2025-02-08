import os
import glob
import random
from yt_dlp import YoutubeDL
from Tepthon import zedub
import re

# دالة للحصول على ملف الكوكيز
def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

# إعدادات yt-dlp
ytd = {
    "prefer_ffmpeg": True,
    "addmetadata": True,
    "geo-bypass": True,
    "nocheckcertificate": True,
    "cookiefile": get_cookies_file(),
    "postprocessors": [{"key": "FFmpegMetadata"}],
}

# دالة لتنظيف اسم الملف
def clean_filename(title):
    title = re.sub(r'[<>:"/\\|?*]', '', title)  # إزالة الرموز غير المسموحة
    return title[:50]  # تقليم العنوان ليكون مختصراً

# دالة للحصول على رابط الفيديو
def get_yt_link(query):
    with YoutubeDL(ytd) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        if info and 'entries' in info and len(info['entries']) > 0:
            if 'url' in info['entries'][0]:
                return info['entries'][0]['url'], info['entries'][0]['title']
    return None, None

# دالة لتحميل المحتوى الصوتي
async def download_yt(event, url, options, title):
    filename = f"{clean_filename(title)}.m4a"  # اسم الملف مع صيغة m4a
    options['outtmpl'] = os.path.join(os.getcwd(), filename)
    with YoutubeDL(options) as ydl:
        ydl.download([url])
    await event.edit("⌔∮ تم التحميل بنجاح!")

# دالة لتحميل الفيديو الصوتي
@zedub.zed_cmd(pattern="تحميل صوتي (.*)")
async def down_voic(event):
    zed = await event.edit("⌔∮ جار التحميل، يرجى الانتظار قليلاً...")
    ytd["format"] = "bestaudio"

    query = event.pattern_match.group(1)
    if not query:
        return await zed.edit("⌔∮ يجب عليك وضع رابط للتحميل الصوتي")

    url, title = get_yt_link(query)
    if not url:
        return await zed.edit("⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح")
    
    await download_yt(zed, url, ytd, title)

# دالة لتحميل الفيديو
@zedub.zed_cmd(pattern="تحميل فيديو (.*)")
async def vidown(event):
    zed = await event.edit("⌔∮ جار التحميل، يرجى الانتظار قليلاً...")
    ytd["format"] = "best"

    query = event.pattern_match.group(1)
    if not query:
        return await zed.edit("⌔∮ يجب عليك وضع رابط لتحميل الفيديو")

    url, title = get_yt_link(query)
    if not url:
        return await zed.edit("⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح")

    await download_yt(zed, url, ytd, title)

# دالة للبحث
@zedub.zed_cmd(pattern="بحث (.*)")
async def sotea(event):
    zed = await event.edit("⌔∮ جار البحث الآن...")
    query = event.pattern_match.group(1) if event.pattern_match.group(1) else None
    if not query:
        return await zed.edit("⌔∮ يجب عليك تحديد ما تريد تحميله، اكتب عنوانًا مع الأمر")

    url, title = get_yt_link(query)
    if not url:
        return await zed.edit("⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح")

    await zed.edit("⌔∮ جار تحميل الملف الصوتي، انتظر قليلاً")
    await download_yt(zed, url, ytd, title)
