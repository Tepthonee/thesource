import os
import glob
import random
from Tepthon import zedub
from yt_dlp import YoutubeDL

# دالة للحصول على ملف الكوكيز
def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

ytd = {
    "prefer_ffmpeg": True,
    "addmetadata": True,
    "geo-bypass": True,
    "nocheckcertificate": True,
    "cookiefile": get_cookies_file(),  # إضافة الكوكيز هنا
    "postprocessors": [{"key": "FFmpegMetadata"}],
}

# دالة لبحث عن الفيديوهات
def get_yt_link(query, ytd):
    with YoutubeDL(ytd) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        if info and 'entries' in info and len(info['entries']) > 0:
            return info['entries'][0]['url']
    return None

# دالة لتحميل الصوتي
@zedub.zed_cmd(pattern="تحميل صوتي (.*)")
async def down_voic(event):
    zed = await event.edit("⌔∮ جار التحميل يرجى الانتظار قليلًا")
    ytd["format"] = "bestaudio"
    ytd["outtmpl"] = "%(id)s.m4a"
    ytd["postprocessors"].insert(
        0,
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "128",
        },
    )
    url = event.pattern_match.group(1)
    if not url:
        return await zed.edit("⌔∮ يجب عليك وضع رابط للتحميل الصوتي")
    try:
        await is_url_work(url)
    except BaseException:
        return await zed.edit("⌔∮ يرجى وضع الرابط بشكل صحيح")
    await download_yt(zed, url, ytd)

# دالة لتحميل الفيديو
@zedub.zed_cmd(pattern="تحميل فيديو (.*)")
async def vidown(event):
    zed = await event.edit("⌔∮ جار التحميل يرجى الانتظار قليلًا")
    ytd["format"] = "best"
    ytd["outtmpl"] = "%(id)s.mp4"
    ytd["postprocessors"].insert(
        0, {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
    )
    url = event.pattern_match.group(1)
    if not url:
        return await zed.edit("⌔∮ يجب عليك وضع رابط لتحميل الفيديو")
    try:
        await is_url_work(url)
    except BaseException:
        return await zed.edit("⌔∮ يرجى وضع الرابط بشكل صحيح")
    await download_yt(zed, url, ytd)

# دالة للبحث
@zedub.zed_cmd(pattern="بحث( (.*)|$)")
async def sotea(event):
    zed = await event.edit("⌔∮ جار التحميل يرجى الانتظار قليلًا")
    ytd["format"] = "bestaudio"
    ytd["outtmpl"] = "%(id)s.m4a"
    ytd["postprocessors"].insert(
        0,
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "128",
        },
    )
    query = event.pattern_match.group(2) if event.pattern_match.group(1) else None
    if not query:
        return await zed.edit("⌔∮ يجب عليك تحديد ما تريد تحميله، اكتب عنوانًا مع الأمر")
    
    # استخدم yt-dlp للبحث عن الفيديو
    url = get_yt_link(query, ytd)
    if not url:
        return await zed.edit("⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح")
    await zed.edit("⌔∮ جار تحميل الملف الصوتي، انتظر قليلًا")
    await download_yt(zed, url, ytd)

# دالة لتحميل المحتوى
async def download_yt(event, url, options):
    with YoutubeDL(options) as ydl:
        try:
            ydl.download([url])
            await event.edit("⌔∮ تم التحميل بنجاح!")
        except BaseException:
            await event.edit("⌔∮ حدث خطأ أثناء التحميل")
