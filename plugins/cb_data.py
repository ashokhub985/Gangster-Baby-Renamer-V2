from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import *
from PIL import Image
import os
import random
import time
from datetime import timedelta
from helper.ffmpeg import take_screen_shot, fix_thumb
from helper.progress import humanbytes, progress_for_pyrogram, TimeFormatter
from helper.set import escape_invalid_curly_brackets

# Environment variables
API_ID = int(os.environ.get("API_ID", "22687964"))
API_HASH = os.environ.get("API_HASH", "bdce6f5214b673c8e8295403e250e383")
STRING = os.environ.get("STRING", "")
ADMIN = os.environ.get("ADMIN", "862729509")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002247619392"))

# Initialize Pyrogram Client
app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, session_string=STRING)

@app.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

@app.on_callback_query(filters.regex('rename'))
async def rename(bot, update):
    date_fa = str(update.message.date)
    date_pattern = '%Y-%m-%d %H:%M:%S'
    date = int(time.mktime(time.strptime(date_fa, date_pattern)))
    chat_id = update.message.chat.id
    message_id = update.message.reply_to_message_id

    await update.message.delete()
    await update.message.reply_text(
        "__Please enter the new filename...__\n\nNote: Extension Not Required",
        reply_to_message_id=message_id,
        reply_markup=ForceReply(True)
    )
    dateupdate(chat_id, date)

@app.on_callback_query(filters.regex("doc"))
async def doc(bot, update):
    new_name = update.message.text
    user_data = find_one(update.from_user.id)
    used_limit = user_data.get("used_limit", 0)
    date = user_data.get("date")
    name_parts = new_name.split(":-")
    new_filename = name_parts[1]
    file_path = f"downloads/{new_filename}"

    message = update.message.reply_to_message
    file = message.document or message.video or message.audio

    progress_message = await update.message.edit("Trying to download...")
    start_time = time.time()

    # Update user's used limit with the file size
    total_used = used_limit + int(file.file_size)
    used_limit(update.from_user.id, total_used)

    try:
        download_path = await bot.download_media(
            message=file,
            progress=progress_for_pyrogram,
            progress_args=("Trying to download...", progress_message, start_time)
        )
    except Exception as e:
        # Revert the used limit in case of failure
        used_limit(update.from_user.id, used_limit - int(file.file_size))
        await progress_message.edit(f"Error: {e}")
        return

    # Rename the downloaded file
    os.rename(download_path, file_path)

    # Get user-specific data and generate caption if needed
    user_id = int(update.message.chat.id)
    user_data = find(user_id)
    custom_caption = user_data.get("caption", "")
    thumb = user_data.get("thumbnail", "")

    if custom_caption:
        doc_list = ["filename", "filesize"]
        formatted_caption = escape_invalid_curly_brackets(custom_caption, doc_list)
        caption = formatted_caption.format(
            filename=new_filename,
            filesize=humanbytes(file.file_size)
        )

      if c_caption:
        doc_list = ["filename", "filesize"]
        new_tex = escape_invalid_curly_brackets(c_caption, doc_list)
        caption = new_tex.format(
            filename=new_filename, filesize=humanbytes(file.file_size))
    else:
        caption = f"**{new_filename}**"

    if thumb:
        ph_path = await bot.download_media(thumb)
        try:
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img = img.resize((320, 320))
            img.save(ph_path, "JPEG")
        except Exception as e:
            logger.error(f"Failed to process thumbnail: {e}")
            ph_path = None

    else:
        ph_path = None

    value = 2090000000  # Example value for upload size limit
    if value < file.file_size:
        await ms.edit("Uploading...")

        try:
            filw = await app.send_document(
                log_channel, document=file_path, thumb=ph_path, caption=caption,
                progress=progress_for_pyrogram, progress_args=("Uploading...", ms, c_time)
            )
            from_chat = filw.chat.id
            mg_id = filw.id
            time.sleep(2)  # Brief delay to ensure message is sent
            await bot.copy_message(update.from_user.id, from_chat, mg_id)
            await ms.delete()
            os.remove(file_path)
            if ph_path:
                try:
                    os.remove(ph_path)
                except Exception as e:
                    logger.error(f"Failed to remove thumbnail: {e}")

        except Exception as e:
            neg_used = used - int(file.file_size)
            used_limit(update.from_user.id, neg_used)
            await ms.edit(f"Error: {e}")
            logger.error(f"Failed to upload document: {e}")
            os.remove(file_path)
            if ph_path:
                try:
                    os.remove(ph_path)
                except Exception as e:
                    logger.error(f"Failed to remove thumbnail: {e}")
            return
    else:
        await ms.edit("Uploading...")
        c_time = time.time()
        try:
            await bot.send_document(
                update.from_user.id, document=file_path, thumb=ph_path, caption=caption,
                progress=progress_for_pyrogram, progress_args=("Uploading...", ms, c_time)
            )
            await ms.delete()
            os.remove(file_path)
            if ph_path:
                try:
                    os.remove(ph_path)
                except Exception as e:
                    logger.error(f"Failed to remove thumbnail: {e}")

        except Exception as e:
            neg_used = used - int(file.file_size)
            used_limit(update.from_user.id, neg_used)
            await ms.edit(f"Error: {e}")
            logger.error(f"Failed to send document to user: {e}")
            os.remove(file_path)
            if ph_path:
                try:
                    os.remove(ph_path)
                except Exception as e:
                    logger.error(f"Failed to remove thumbnail: {e}")
            return



@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        return

@Client.on_callback_query(filters.regex("aud"))
async def aud(bot, update):
    try:
        new_name = update.message.text
        used_ = find_one(update.from_user.id)
        used = used_["used_limit"]
        name = new_name.split(":-")
        new_filename = name[1]
        file_path = f"downloads/{new_filename}"
        message = update.message.reply_to_message
        file = message.document or message.video or message.audio
        total_used = used + int(file.file_size)
        used_limit(update.from_user.id, total_used)
        
        ms = await update.message.edit("Trying To Download...")
        c_time = time.time()
        path = await bot.download_media(
            message=file,
            progress=progress_for_pyrogram,
            progress_args=("Trying To Download...", ms, c_time)
        )

        splitpath = path.split("/downloads/")
        dow_file_name = splitpath[1]
        old_file_name = f"downloads/{dow_file_name}"
        os.rename(old_file_name, file_path)

        # Extract file metadata and process audio
        duration = 0
        metadata = extractMetadata(createParser(file_path))
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds

        user_id = int(update.message.chat.id)
        data = find(user_id)
        c_caption = data.get(1, None)
        thumb = data.get(0, None)

        if c_caption:
            aud_list = ["filename", "filesize", "duration"]
            new_tex = escape_invalid_curly_brackets(c_caption, aud_list)
            caption = new_tex.format(
                filename=new_filename,
                filesize=humanbytes(file.file_size),
                duration=timedelta(seconds=duration)
            )
        else:
            caption = f"**{new_filename}**"

        if thumb:
            ph_path = await bot.download_media(thumb)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img = img.resize((320, 320))
            img.save(ph_path, "JPEG")

            await ms.edit("Trying To Upload")
            c_time = time.time()
            try:
                await bot.send_audio(
                    update.message.chat.id,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("Trying To Uploading", ms, c_time)
                )
                await ms.delete()
                os.remove(file_path)
                os.remove(ph_path)
            except Exception as e:
                logger.error(f"Failed to send audio: {e}")
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await ms.edit(e)
                os.remove(file_path)
                os.remove(ph_path)
        else:
            await ms.edit("Trying To Upload")
            c_time = time.time()
            try:
                await bot.send_audio(
                    update.message.chat.id,
                    audio=file_path,
                    caption=caption,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("Trying To Uploading", ms, c_time)
                )
                await ms.delete()
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to send audio: {e}")
                await ms.edit(e)
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                os.remove(file_path)

@Client.on_callback_query(filters.regex("doc"))
async def doc(bot, update):
    try:
        new_name = update.message.text
        used_ = find_one(update.from_user.id)
        used = used_["used_limit"]
        name = new_name.split(":-")
        new_filename = name[1]
        file_path = f"downloads/{new_filename}"
        message = update.message.reply_to_message
        file = message.document or message.video or message.audio
        
        ms = await update.message.edit("Trying To Download...")
        used_limit(update.from_user.id, file.file_size)
        c_time = time.time()
        total_used = used + int(file.file_size)
        used_limit(update.from_user.id, total_used)

        path = await bot.download_media(
            message=file,
            progress=progress_for_pyrogram,
            progress_args=("Trying To Download...", ms, c_time)
        )

        splitpath = path.split("/downloads/")
        dow_file_name = splitpath[1]
        old_file_name = f"downloads/{dow_file_name}"
        os.rename(old_file_name, file_path)

        user_id = int(update.message.chat.id)
        data = find(user_id)
        c_caption = data.get(1, None)
        thumb = data.get(0, None)

        if c_caption:
            doc_list = ["filename", "filesize"]
            new_tex = escape_invalid_curly_brackets(c_caption, doc_list)
            caption = new_tex.format(
                filename=new_filename,
                filesize=humanbytes(file.file_size)
            )
        else:
            caption = f"**{new_filename}**"

        if thumb:
            ph_path = await bot.download_media(thumb)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img = img.resize((320, 320))
            img.save(ph_path, "JPEG")

            await ms.edit("Trying To Upload")
            c_time = time.time()
            try:
                await bot.send_document(
                    update.message.chat.id,
                    document=file_path,
                    caption=caption,
                    thumb=ph_path,
                    progress=progress_for_pyrogram,
                    progress_args=("Trying To Uploading", ms, c_time)
                )
                await ms.delete()
                os.remove(file_path)
                os.remove(ph_path)
            except Exception as e:
                logger.error(f"Failed to send document: {e}")
                await ms.edit(e)
                os.remove(file_path)
                os.remove(ph_path)
        else:
            await ms.edit("Trying To Upload")
            c_time = time.time()
            try:
                await bot.send_document(
                    update.message.chat.id,
                    document=file_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("Trying To Uploading", ms, c_time)
                )
                await ms.delete()
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to send document: {e}")
                await ms.edit(e)
                os.remove(file_path)

@Client.on_callback_query(filters.regex('rename'))
async def rename(bot, update):
    date_fa = str(update.message.date)
    pattern = '%Y-%m-%d %H:%M:%S'
    date = int(time.mktime(time.strptime(date_fa, pattern)))
    chat_id = update.message.chat.id
    id = update.message.reply_to_message_id
    await update.message.delete()
    await update.message.reply_text(
        f"__Please enter the new filename...__\n\nNote:- Extension Not Required",
        reply_to_message_id=id,
        reply_markup=ForceReply(True)
    )
    dateupdate(chat_id, date)
