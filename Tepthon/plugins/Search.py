from Tepthon import download_yt, get_yt_link, is_url_work, zedub
import os
import random
import glob

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

@zedub.zed_cmd(pattern="تحميل صوتي (.*)")
async def down_voic(event):
    jmbot = await event.edit("⌔∮ جار التحميل يرجى الانتظار قليلًا")
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
        return await jmbot.edit("⌔∮ يجب عليك وضع رابط للتحميل الصوتي")
    try:
        await is_url_work(url)
    except BaseException:
        return await jmbot.edit("⌔∮ يرجى وضع الرابط بشكل صحيح")
    await download_yt(jmbot, url, ytd)

@zedub.zed_cmd(pattern="تحميل فيديو (.*)")
async def vidown(event):
    jmbot = await event.edit("⌔∮ جار التحميل يرجى الانتظار قليلًا")
    ytd["format"] = "best"
    ytd["outtmpl"] = "%(id)s.mp4"
    ytd["postprocessors"].insert(
        0, {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
    )
    url = event.pattern_match.group(1)
    if not url:
        return await jmbot.edit("⌔∮ يجب عليك وضع رابط لتحميل الفيديو")
    try:
        await is_url_work(url)
    except BaseException:
        return await jmbot.edit("⌔∮ يرجى وضع الرابط بشكل صحيح")
    await download_yt(jmbot, url, ytd)

@zedub.zed_cmd(pattern="بحث( (.*)|$)")
async def sotea(event):
    jmbot = await event.edit("⌔∮ جار التحميل يرجى الانتظار قليلًا")
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
        return await jmbot.edit("⌔∮ يجب عليك تحديد ما تريد تحميله، اكتب عنوانًا مع الأمر")
    url = get_yt_link(query, ytd)
    if not url:
        return await jmbot.edit("⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح")
    await jmbot.edit("⌔∮ جار تحميل الملف الصوتي، انتظر قليلًا")
    await download_yt(jmbot, url, ytd)
