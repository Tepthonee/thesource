import asyncio
import glob
import io
import os
import re
import pathlib
from time import time
import requests

import aiohttp
import aiofiles
import wget
import yt_dlp
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

from urlextract import URLExtract
from wget import download
from yt_dlp import YoutubeDL
from yt_dlp.utils import (
    ContentTooShortError,
    DownloadError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from telethon import events
from telethon.tl import types
from telethon.utils import get_attributes
from telethon.errors.rpcerrorlist import YouBlockedUserError, ChatSendMediaForbiddenError
from telethon.tl.functions.contacts import UnblockRequest as unblock

from ..Config import Config
from ..core import pool
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import progress, reply_id
from ..helpers.functions import delete_conv
from ..helpers.functions.utube import _mp3Dl, get_yt_video_id, get_ytthumb, ytsearch
from ..helpers.utils import _format
from . import BOTLOG, BOTLOG_CHATID, zedub

BASE_YT_URL = "https://www.youtube.com/watch?v="
extractor = URLExtract()
LOGS = logging.getLogger(__name__)

plugin_category = "البحث"


video_opts = {
    "format": "best",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "writethumbnail": True,
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "cookiefile": "rcookies/cozc.txt",  # إضافة ملف الكوكيز هنا
    "postprocessors": [
        {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        {"key": "FFmpegMetadata"},
    ],
    "outtmpl": "/root/zelz/downloads/cat_ytv.mp4",  # مسار حفظ الفيديو
    "logtostderr": False,
    "quiet": True,
}


async def ytdl_down(event, opts, url):
    ytdl_data = None
    try:
        await event.edit("**╮ ❐ يتـم جلـب البيانـات انتظـر قليلاً ...𓅫╰▬▭ **")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await event.edit(f"`{DE}`")
    except ContentTooShortError:
        await event.edit("**- عذرا هذا المحتوى قصير جدا لتنزيله ⚠️**")
    except GeoRestrictedError:
        await event.edit(
            "**- الفيديو غير متاح من موقعك الجغرافي بسبب القيود الجغرافية التي يفرضها موقع الويب ❕**"
        )
    except MaxDownloadsReached:
        await event.edit("**- تم الوصول إلى الحد الأقصى لعدد التنزيلات ❕**")
    except PostProcessingError:
        await event.edit("**كان هناك خطأ أثناء المعالجة**")
    except UnavailableVideoError:
        await event.edit("**⌔∮عـذراً .. الوسائط غير متوفـره بالتنسيق المطلـوب**")
    except XAttrMetadataError as XAME:
        await event.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        await event.edit("**حدث خطأ أثناء استخراج المعلومات يرجى وضعها بشكل صحيح ⚠️**")
    except Exception as e:
        await event.edit(f"**- خطـأ : **\n__{e}__")
    return ytdl_data


async def fix_attributes(
    path, info_dict: dict, supports_streaming: bool = False, round_message: bool = False
) -> list:
    """Avoid multiple instances of an attribute."""
    new_attributes = []
    video = False
    audio = False

    uploader = info_dict.get("uploader", "Unknown artist")
    duration = int(info_dict.get("duration", 0))
    suffix = path.suffix[1:]
    if supports_streaming and suffix != "mp4":
        supports_streaming = True

    attributes, mime_type = get_attributes(path)
    if suffix == "mp3":
        title = str(info_dict.get("title", info_dict.get("id", "Unknown title")))
        audio = types.DocumentAttributeAudio(
            duration=duration, voice=None, title=title, performer=uploader
        )
    elif suffix == "mp4":
        width = int(info_dict.get("width", 0))
        height = int(info_dict.get("height", 0))
        for attr in attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                duration = duration or attr.duration
                width = width or attr.w
                height = height or attr.h
                break
        video = types.DocumentAttributeVideo(
            duration=duration,
            w=width,
            h=height,
            round_message=round_message,
            supports_streaming=supports_streaming,
        )

    if audio and isinstance(audio, types.DocumentAttributeAudio):
        new_attributes.append(audio)
    if video and isinstance(video, types.DocumentAttributeVideo):
        new_attributes.append(video)

    new_attributes.extend(
        attr
        for attr in attributes
        if (
            isinstance(attr, types.DocumentAttributeAudio)
            and not audio
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not video
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not isinstance(attr, types.DocumentAttributeVideo)
        )
    )
    return new_attributes, mime_type


@zedub.zed_cmd(pattern="سناب(?: |$)(.*)")
async def download_video(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(zedevent, video_opts, url)
        if ytdl_down is None:
            return
        try:
            f = pathlib.Path("cat_ytv.mp4")
            print(f)
            catthumb = pathlib.Path("cat_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("cat_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
            await zedevent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, zedevent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**⎉╎المقطــع :** `{ytdl_data["title"]}`\n**⎉╎الرابـط : {msg}**\n**⎉╎تم  التحميـل .. بنجـاح ✅**"',
                thumb=catthumb,
            )
            os.remove(f)
            if catthumb:
                os.remove(catthumb)
        except TypeError:
            await asyncio.sleep(2)
    await event.delete()


@zedub.zed_cmd(pattern="فيس(?: |$)(.*)")
async def download_video(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(zedevent, video_opts, url)
        if ytdl_down is None:
            return
        try:
            f = pathlib.Path("cat_ytv.mp4")
            print(f)
            catthumb = pathlib.Path("cat_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("cat_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
            await zedevent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, zedevent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**⎉╎المقطــع :** `{ytdl_data["title"]}`\n**⎉╎الرابـط : {msg}**\n**⎉╎تم  التحميـل .. بنجـاح ✅**"',
                thumb=catthumb,
            )
            os.remove(f)
            if catthumb:
                os.remove(catthumb)
        except TypeError:
            await asyncio.sleep(2)
    await event.delete()


@zedub.zed_cmd(pattern="بنترست(?: |$)(.*)")
async def download_video(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(zedevent, video_opts, url)
        if ytdl_down is None:
            return
        try:
            f = pathlib.Path("cat_ytv.mp4")
            print(f)
            catthumb = pathlib.Path("cat_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("cat_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
            await zedevent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, zedevent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**⎉╎المقطــع :** `{ytdl_data["title"]}`\n**⎉╎الرابـط : {msg}**\n**⎉╎تم  التحميـل .. بنجـاح ✅**"',
                thumb=catthumb,
            )
            os.remove(f)
            if catthumb:
                os.remove(catthumb)
        except TypeError:
            await asyncio.sleep(2)
    await event.delete()


@zedub.zed_cmd(
    pattern="ساوند(?: |$)(.*)",
    command=("ساوند", plugin_category),
    info={
        "header": "تحميـل الاغـاني مـن سـاونـد كـلاود الـخ عـبر الرابـط",
        "مثــال": ["{tr}ساوند بالــرد ع رابــط", "{tr}ساوند + رابــط"],
    },
)
async def download_audio(event):
    """To download audio from YouTube and many other sites."""
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        try:
            vid_data = YoutubeDL({"no-playlist": True}).extract_info(
                url, download=False
            )
        except ExtractorError:
            vid_data = {"title": url, "uploader": "Catuserbot", "formats": []}
        startTime = time()
        retcode = await _mp3Dl(url=url, starttime=startTime, uid="320")
        if retcode != 0:
            return await event.edit(str(retcode))
        _fpath = ""
        thumb_pic = None
        for _path in glob.glob(os.path.join(Config.TEMP_DIR, str(startTime), "*")):
            if _path.lower().endswith((".jpg", ".png", ".webp")):
                thumb_pic = _path
            else:
                _fpath = _path
        if not _fpath:
            return await edit_delete(zedevent, "__Unable to upload file__")
        await zedevent.edit(
            f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
            \n**{vid_data['title']}***"
        )
        attributes, mime_type = get_attributes(str(_fpath))
        ul = io.open(pathlib.Path(_fpath), "rb")
        if thumb_pic is None:
            thumb_pic = str(
                await pool.run_in_thread(download)(
                    await get_ytthumb(get_yt_video_id(url))
                )
            )
        uploaded = await event.client.fast_upload_file(
            file=ul,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    zedevent,
                    startTime,
                    "trying to upload",
                    file_name=os.path.basename(pathlib.Path(_fpath)),
                )
            ),
        )
        ul.close()
        media = types.InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime_type,
            attributes=attributes,
            force_file=False,
            thumb=await event.client.upload_file(thumb_pic) if thumb_pic else None,
        )
        await event.client.send_file(
            event.chat_id,
            file=media,
            caption=f"<b>⎉╎المقطع : </b><code>{vid_data.get('title', os.path.basename(pathlib.Path(_fpath)))}</code>",
            supports_streaming=True,
            reply_to=reply_to_id,
            parse_mode="html",
        )
        for _path in [_fpath, thumb_pic]:
            os.remove(_path)
    await zedevent.delete()


@zedub.zed_cmd(
    pattern="يوتيوب(?: |$)(\\d*)? ?([\\s\\S]*)",
    command=("يوتيوب", plugin_category),
    info={
        "header": "لـ البحـث عـن روابــط بالكلمــه المحــدده علـى يـوتيــوب",
        "مثــال": [
            "{tr}يوتيوب + كلمـه",
            "{tr}يوتيوب + عدد + كلمـه",
        ],
    },
)
async def yt_search(event):
    "Youtube search command"
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
    if not query:
        return await edit_delete(
            event, "**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**"
        )
    video_q = await edit_or_reply(event, "**╮ جـارِ البحث ▬▭... ╰**")
    if event.pattern_match.group(1) != "":
        lim = int(event.pattern_match.group(1))
        if lim <= 0:
            lim = int(10)
    else:
        lim = int(10)
    try:
        full_response = await ytsearch(query, limit=lim)
    except Exception as e:
        return await edit_delete(video_q, str(e), time=10, parse_mode=_format.parse_pre)
    reply_text = f"**⎉╎اليك عزيزي قائمة بروابط الكلمة اللتي بحثت عنها:**\n`{query}`\n\n**⎉╎النتائج:**\n{full_response}"
    await edit_or_reply(video_q, reply_text)

# ================================================================================================ #
# =========================================ساوند كلاود================================================= #
# ================================================================================================ #

def remove_if_exists(path): #Code by T.me/zzzzl1l
    if os.path.exists(path):
        os.remove(path)

#Code by T.me/zzzzl1l
@zedub.zed_cmd(pattern="بحث(?: |$)(.*)")
async def _(event): #Code by T.me/zzzzl1l
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
    elif reply and reply.message:
        query = reply.message
    else:
        return await edit_or_reply(event, "**⎉╎قم باضافـة إسـم للامـر ..**\n**⎉╎بحث + اسـم المقطـع الصـوتي**")
    zedevent = await edit_or_reply(event, "**╮ جـارِ البحث ؏ـن المقطـٓع الصٓوتـي... 🎧♥️╰**")
    ydl_ops = {
    'format': 'bestaudio[ext=m4a]',
    'keepvideo': True,
    'prefer_ffmpeg': False,
    'geo_bypass': True,
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,  # تصحيح الخطأ الإملائي
    'cookiefile': 'rcookies/cozc.txt',  # تحديد ملف الكوكيز
    }
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        try:
            open(thumb_name, "wb").write(thumb.content)
        except Exception:
            thumb_name = None
            pass
        duration = results[0]["duration"]

    except Exception as e:
        await zedevent.edit(f"**- فشـل التحميـل** \n**- الخطأ :** `{str(e)}`")
        return
    await zedevent.edit("**╮ جـارِ التحميل ▬▭ . . .🎧♥️╰**")
    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        host = str(info_dict["uploader"])
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60
        await zedevent.edit("**╮ جـارِ الرفـع ▬▬ . . .🎧♥️╰**")
        await event.client.send_file(
            event.chat_id,
            audio_file,
            force_document=False,
            caption=f"**⎉╎البحث :** `{title}`",
            thumb=thumb_name,
        )
        await zedevent.delete()
    except ChatSendMediaForbiddenError as err: # Code By T.me/zzzzl1l
        await zedevent.edit("**- عـذراً .. الوسـائـط مغلقـه هنـا ؟!**")
        LOGS.error(str(err))
    except Exception as e:
        await zedevent.edit(f"**- فشـل التحميـل** \n**- الخطأ :** `{str(e)}`")
    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)


#Code by T.me/zzzzl1l
@zedub.zed_cmd(pattern="فيديو(?: |$)(.*)")
async def _(event): #Code by T.me/zzzzl1l
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
    elif reply and reply.message:
        query = reply.message
    else:
        return await edit_or_reply(event, "**⎉╎قم باضافـة إسـم للامـر ..**\n**⎉╎فيديو + اسـم الفيديـو**")
    zedevent = await edit_or_reply(event, "**╮ جـارِ البحث ؏ـن الفيديـو... 🎧♥️╰**")
    ydl_opts = {
    "format": "best",
    "keepvideo": True,
    "prefer_ffmpeg": False,
    "geo_bypass": True,
    "outtmpl": "%(title)s.%(ext)s",
    "quiet": True,  # تصحيح الخطأ الإملائي من 'quite' إلى 'quiet'
    "cookiefile": "rcookies/cozc.txt",  # إضافة ملف الكوكيز
    }
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        results[0]["duration"]
        results[0]["url_suffix"]
        results[0]["views"]
    except Exception as e:
        await zedevent.edit(f"**- فشـل التحميـل** \n**- الخطأ :** `{str(e)}`")
        #return
    try:
        msg = await zedevent.edit("**╮ جـارِ التحميل ▬▭ . . .🎧♥️╰**")
        with YoutubeDL(ydl_opts) as ytdl:
            ytdl_data = ytdl.extract_info(link, download=True)
            file_name = ytdl.prepare_filename(ytdl_data)
    except Exception as e:
        return await zedevent.edit(f"**- فشـل التحميـل** \n**- الخطأ :** `{str(e)}`")
    preview = wget.download(thumbnail)
    await zedevent.edit("**╮ جـارِ الرفـع ▬▬ . . .🎧♥️╰**")
    await event.client.send_file(
        event.chat_id,
        file_name,
        caption=f"**⎉╎البحث :** `{title}`",
        thumb=preview,
        supports_streaming=True,
    )
    try:
        remove_if_exists(file_name)
        await zedevent.delete()
    except Exception as e:
        print(e)


# ================================================================================================ #
# =========================================ردود الخاص================================================= #
# ================================================================================================ #
import re
import datetime
from asyncio import sleep

from telethon import events
from telethon.utils import get_display_name

from . import zedub
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import pmpermit_sql as pmpermit_sql
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.pasmat_sql import (
    add_pasmat,
    get_pasmats,
    remove_all_pasmats,
    remove_pasmat,
)
from ..sql_helper.pmrad_sql import (
    add_pmrad,
    get_pmrads,
    remove_all_pmrads,
    remove_pmrad,
)
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "الخدمات"
LOGS = logging.getLogger(__name__)


ZelzalMeMe_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗧𝗘𝗣𝗧𝗛𝗢𝗡 ⌁ - اوامـر البصمـات 🎙](t.me/veevv2) 𓆪\n\n"
    "**✾╎قائـمه اوامـر ردود البصمات والميديا العامـه🎙:**\n\n"
    "**⎞𝟏⎝** `.بصمه`\n"
    "**•• ⦇الامـر + كلمـة الـرد بالـرد ع بصمـه او ميديـا⦈ لـ اضـافة رد بصمـه عـام**\n\n"
    "**⎞𝟐⎝** `.حذف بصمه`\n"
    "**•• ⦇الامـر + كلمـة البصمـه⦈ لـ حـذف رد بصمـه محـدد**\n\n"
    "**⎞𝟑⎝** `.بصماتي`\n"
    "**•• لـ عـرض قائمـة بـ جميـع بصمـاتك المضـافـه**\n\n"
    "**⎞𝟒⎝** `.حذف بصماتي`\n"
    "**•• لـ حـذف جميـع بصمـاتك المضافـه**\n\n"
    "\n 𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝗧𝗘𝗣𝗧𝗛𝗢𝗡 ⌁](t.me/Tepthon) 𓆪"
)


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="البصمات")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalMeMe_cmd)

async def reply_id(event):
    reply_to_id = None
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    return reply_to_id

@zedub.on(admin_cmd(incoming=True))
async def filter_incoming_handler(event):
    name = event.raw_text
    repl = await reply_id(event)
    filters = get_pasmats(zedub.uid)
    if not filters:
        return
    for trigger in filters:
        if name == trigger.keyword:
            file_media = None
            filter_msg = None
            if trigger.f_mesg_id:
                msg_o = await event.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id)
                )
                file_media = msg_o.media
                filter_msg = msg_o.message
                link_preview = True
            elif trigger.reply:
                filter_msg = trigger.reply
                link_preview = False
            try:
                await event.client.send_file(
                    event.chat_id,
                    file=file_media,
                    link_preview=link_preview,
                    reply_to=repl,
                )
                await event.delete()
            except BaseException:
                return

@zedub.zed_cmd(pattern="بصمه (.*)")
async def add_new_meme(event):
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⪼ البصمـات 🔊 :**\
                \n**⪼ تم حفـظ البصمـه بـ اسم {keyword}**\n**⪼ لـ قائمـه بصماتك .. بنجـاح ✅**\n**⪼ لـ تصفـح قائمـة بصماتك ارسـل (.بصماتي) 📑**",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID,
                messages=msg,
                from_peer=event.chat_id,
                silent=True,
            )
            msg_id = msg_o.id
        else:
            await edit_or_reply(
                event,
                "**❈╎يتطلب اضافة البصمات تعيين كـروب السجـل اولاً ..**\n**❈╎لاضافـة كـروب السجـل**\n**❈╎اتبـع الشـرح ⇚** https://t.me/Tepthon",
            )
            return
    elif msg and msg.text and not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")
    elif not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")
    else:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")
    success = "**⪼تم {} البصمـه بـ اسم {} .. بنجـاح ✅**"
    if add_pasmat(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("اضافة", keyword))
    remove_pasmat(str(zedub.uid), keyword)
    if add_pasmat(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("تحديث", keyword))
    await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")


@zedub.zed_cmd(pattern="بصماتي$")
async def on_meme_list(event):
    OUT_STR = "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**"
    filters = get_pasmats(zedub.uid)
    for filt in filters:
        if OUT_STR == "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**":
            OUT_STR = "𓆩 𝗧𝗘𝗣𝗧𝗛𝗢𝗡 ⌁ 𝗭𝗧𝗵𝗼𝗻 - قائمـة بصمـاتك المضـافـة 🔊𓆪\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
        OUT_STR += "🎙 `{}`\n".format(filt.keyword)
    await edit_or_reply(
        event,
        OUT_STR,
        caption="**⧗╎قائمـة بصمـاتك المضـافـه🔊**",
        file_name="filters.text",
    )


@zedub.zed_cmd(pattern="حذف بصمه(?: |$)(.*)")
async def remove_a_meme(event):
    filt = event.pattern_match.group(1)
    if not remove_pasmat(zedub.uid, filt):
        await event.edit("**- ❝ البصمـه ↫** {} **غيـر موجـوده ⁉️**".format(filt))
    else:
        await event.edit("**- ❝ البصمـه ↫** {} **تم حذفهـا بنجاح ☑️**".format(filt))


@zedub.zed_cmd(pattern="حذف بصماتي$")
async def on_all_meme_delete(event):
    filters = get_pasmats(zedub.uid)
    if filters:
        remove_all_pasmats(zedub.uid)
        await edit_or_reply(event, "**⪼ تم حـذف جميـع بصمـاتك .. بنجـاح ✅**")
    else:
        OUT_STR = "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**"
        await edit_or_reply(event, OUT_STR)

# ================================================================================================ #
# =========================================ردود الخاص================================================= #
# ================================================================================================ #

@zedub.on(admin_cmd(incoming=True))
async def filter_incoming_handler(event):
    if not event.is_private:
        return
    if event.sender_id == event.client.uid:
        return
    name = event.raw_text
    filters = get_pmrads(zedub.uid)
    if not filters:
        return
    a_user = await event.get_sender()
    chat = await event.get_chat()
    me = await event.client.get_me()
    title = None
    #participants = await event.client.get_participants(chat)
    count = None
    mention = f"[{a_user.first_name}](tg://user?id={a_user.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    first = a_user.first_name
    last = a_user.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{a_user.username}" if a_user.username else mention
    userid = a_user.id
    my_first = me.first_name
    my_last = me.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{me.username}" if me.username else my_mention
    for trigger in filters:
        pattern = f"( |^|[^\\w]){re.escape(trigger.keyword)}( |$|[^\\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            file_media = None
            filter_msg = None
            if trigger.f_mesg_id:
                msg_o = await event.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id)
                )
                file_media = msg_o.media
                filter_msg = msg_o.message
                link_preview = True
            elif trigger.reply:
                filter_msg = trigger.reply
                link_preview = False
            await event.reply(
                filter_msg.format(
                    mention=mention,
                    first=first,
                    last=last,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                    my_first=my_first,
                    my_last=my_last,
                    my_fullname=my_fullname,
                    my_username=my_username,
                    my_mention=my_mention,
                ),
                file=file_media,
                link_preview=link_preview,
            )

@zedub.zed_cmd(pattern="اضف تلقائي (.*)")
async def add_new_meme(event):
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⪼ ردودك التلقائيـه خـاص 🗣 :**\
                \n**⪼ تم حفـظ الـرد التلقـائـي بـ اسم {keyword}**\n**⪼ لـ قائمـه ردودك التلقائيـه .. بنجـاح ✅**\n**⪼ لـ تصفـح قائمـة ردودك التلقائيـه ارسـل (.ردود الخاص) 📑**",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID,
                messages=msg,
                from_peer=event.chat_id,
                silent=True,
            )
            msg_id = msg_o.id
        else:
            await edit_or_reply(
                event,
                "**❈╎يتطلب اضافة الـردود التلقـائـيـه تعيين كـروب السجـل اولاً ..**\n**❈╎لاضافـة كـروب السجـل**\n**❈╎اتبـع الشـرح ⇚** https://t.me/Tepthon",
            )
            return
    elif msg and msg.text and not string:
        string = msg.text
    elif not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لاضافتهـا لـ قائمـة ردودك التلقائيـه 🧾**")
    else:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لاضافتهـا لـ قائمـة ردودك التلقائيـه 🧾**")
    success = "**⪼تم {} الـرد التلقـائـي بـ اسم {} .. بنجـاح ✅**"
    if add_pmrad(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("اضافة", keyword))
    remove_pmrad(str(zedub.uid), keyword)
    if add_pmrad(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("تحديث", keyword))
    await edit_or_reply(event, "**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لاضافتهـا لـ قائمـة ردودك التلقائيـه 🧾**")


@zedub.zed_cmd(pattern="ردود الخاص$")
async def on_meme_list(event):
    OUT_STR = "**⪼ لا يوجـد لديك ردود تلقائيـه لـ الخـاص ❌**\n\n**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لاضافتهـا لـ قائمـة ردودك التلقائيـه 🧾**"
    filters = get_pmrads(zedub.uid)
    for filt in filters:
        if OUT_STR == "**⪼ لا يوجـد لديك ردود تلقائيـه لـ الخـاص ❌**\n\n**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لاضافتهـا لـ قائمـة ردودك التلقائيـه 🧾**":
            OUT_STR = "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗧𝗘𝗣𝗧𝗛𝗢𝗡 ⌁ - ردودك التلقـائيـه خـاص 🗣𓆪\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
        OUT_STR += "🎙 `{}`\n".format(filt.keyword)
    await edit_or_reply(
        event,
        OUT_STR,
        caption="**⧗╎قائمـة ردودك التلقـائـيـه خـاص المضـافـه🗣**",
        file_name="filters.text",
    )


@zedub.zed_cmd(pattern="حذف تلقائي(?: |$)(.*)")
async def remove_a_meme(event):
    filt = event.pattern_match.group(1)
    if not remove_pmrad(zedub.uid, filt):
        await event.edit("**- ❝ الـرد التلقـائـي ↫** {} **غيـر موجـود ⁉️**".format(filt))
    else:
        await event.edit("**- ❝ الـرد التلقـائـي ↫** {} **تم حذفه .. بنجاح ☑️**".format(filt))


@zedub.zed_cmd(pattern="حذف ردود الخاص$")
async def on_all_meme_delete(event):
    filters = get_pmrads(zedub.uid)
    if filters:
        remove_all_pmrads(zedub.uid)
        await edit_or_reply(event, "**⪼ تم حـذف جميـع ردودك التلقـائـيـه خـاص .. بنجـاح ✅**")
    else:
        OUT_STR = "**⪼ لا يوجـد لديك ردود تلقائيـه لـ الخـاص ❌**\n\n**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لاضافتهـا لـ قائمـة ردودك التلقائيـه 🧾**"
        await edit_or_reply(event, OUT_STR)
