import os
import glob
import random
import re
from Tepthon import zedub
from yt_dlp import YoutubeDL

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
            url = info['entries'][0]['url']
            title = info['entries'][0]['title']
            return url, title
    return None, None

# دالة لتحميل المحتوى الصوتي
def download_yt(url, options, title):
    filename = f"{clean_filename(title)}.m4a"  # اسم الملف مع صيغة m4a
    options['outtmpl'] = os.path.join(os.getcwd(), filename)
    with YoutubeDL(options) as ydl:
        ydl.download([url])

# دالة لتحميل الفيديو الصوتي
def download_audio(query):
    ytd["format"] = "bestaudio"
    url, title = get_yt_link(query)
    
    if not url:
        return "⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح"
    
    download_yt(url, ytd, title)
    return "⌔∮ تم تحميل الملف الصوتي بنجاح!"

# دالة لتحميل الفيديو
def download_video(query):
    ytd["format"] = "best"
    url, title = get_yt_link(query)
    
    if not url:
        return "⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح"
    
    download_yt(url, ytd, title)
    return "⌔∮ تم تحميل الفيديو بنجاح!"

# دالة للبحث
def search_video(query):
    url, title = get_yt_link(query)
    
    if not url:
        return "⌔∮ لم يتم العثور على الفيديو، اكتب عنوانًا مفصلًا بشكل صحيح"
    
    return f"⌔∮ تم العثور على الفيديو: {title}\n⌔∮ الرابط: {url}"

# مثال على الاستخدام
if __name__ == "__main__":
    query = input("أدخل عنوان البحث: ")
    choice = input("هل تريد تحميل صوتي أو فيديو؟ (صوتي/فيديو): ")
    
    if choice == "صوتي":
        print(download_audio(query))
    elif choice == "فيديو":
        print(download_video(query))
    else:
        print("اختيار غير صحيح. يرجى الاختيار بين صوتي وفيديو.")
