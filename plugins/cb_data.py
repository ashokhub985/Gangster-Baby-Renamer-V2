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
import logging
from pyrogram import Client, filters
from pyrogram.types import ForceReply
from PIL import Image
import os
import time
import logging
from mutagen.mp3 import MP3
from mutagen import File
from datetime import timedelta
from some_module import extractMetadata, createParser, progress_for_pyrogram, humanbytes, find_one, used_limit, find, escape_invalid_curly_brackets, dateupdate  # Add your specific module for utility functions


# Setting up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
STRING = os.environ.get("STRING", "")
ADMIN = os.environ.get("ADMIN", "").split()  # Assuming multiple admin IDs are separated by spaces
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))

# Initialize Pyrogram Client
app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, session_string=STRING)

@app.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

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
    try:
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

        # Download the file
        download_path = await bot.download_media(
            message=file,
            progress=progress_for_pyrogram,
            progress_args=("Trying to download...", progress_message, start_time)
        )

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
        else:
            caption = f"**{new_filename}**"

        # Process thumbnail if available
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

        # Check upload size and handle uploading
        value = 2090000000  # Example value for upload size limit
        if value < file.file_size:
            await progress_message.edit("Uploading...")

            try:
                file_message = await app.send_document(
                    LOG_CHANNEL, document=file_path, thumb=ph_path, caption=caption,
                    progress=progress_for_pyrogram, progress_args=("Uploading...", progress_message, start_time)
                )
                from_chat = file_message.chat.id
                mg_id = file_message.id
                time.sleep(2)  # Brief delay to ensure message is sent
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await progress_message.delete()
                os.remove(file_path)
                if ph_path:
                    os.remove(ph_path)
            except Exception as e:
                neg_used = used_limit - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await progress_message.edit(f"Error: {e}")
                logger.error(f"Failed to upload document: {e}")
                os.remove(file_path)
                if ph_path:
                    os.remove(ph_path)
        else:
            await progress_message.edit("Uploading...")
            c_time = time.time()
            try:
                await bot.send_document(
                    update.from_user.id, document=file_path, thumb=ph_path, caption=caption,
                    progress=progress_for_pyrogram, progress_args=("Uploading...", progress_message, c_time)
                )
                await progress_message.delete()
                os.remove(file_path)
                if ph_path:
                    os.remove(ph_path)
            except Exception as e:
                neg_used = used_limit - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await progress_message.edit(f"Error: {e}")
                logger.error(f"Failed to send document to user: {e}")
                os.remove(file_path)
                if ph_path:
                    os.remove(ph_path)
    except Exception as e:
        logger.error(f"Unhandled exception in doc callback: {e}")
        await update.message.edit("An unexpected error occurred.")

# Logger setup
logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    """Handles the cancellation of an operation."""
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        await update.message.reply_text("Failed to delete the message. Please try again later.")

@Client.on_callback_query(filters.regex("aud"))
async def aud(bot, update):
    """Handles audio file upload and processing."""
    try:
        new_name = update.message.text
        user_data = find_one(update.from_user.id)
        used_limit_value = user_data["used_limit"]

        # Extract new filename from the callback data
        new_filename = new_name.split(":-")[1]
        file_path = f"downloads/{new_filename}"

        # Retrieve the file from the reply message
        message = update.message.reply_to_message
        file = message.document or message.video or message.audio

        if not file:
            await update.message.reply_text("No valid file found in the reply message.")
            return

        # Update the used limit for the user
        total_used = used_limit_value + int(file.file_size)
        used_limit(update.from_user.id, total_used)

        # Notify the user about the download process
        ms = await update.message.edit("Trying To Download...")
        start_time = time.time()

        # Download the media file
        path = await bot.download_media(
            message=file,
            progress=progress_for_pyrogram,
            progress_args=("Trying To Download...", ms, start_time)
        )

        # Rename and move the downloaded file
        new_file_path = os.path.join("downloads", new_filename)
        os.rename(path, new_file_path)

        # Extract metadata for audio duration
        duration = 0
        metadata = extractMetadata(createParser(new_file_path))
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds

        # Get user-specific data for custom caption and thumbnail
        user_id = int(update.message.chat.id)
        data = find(user_id)
        custom_caption = data.get(1, None)
        thumb = data.get(0, None)

        # Create caption for the audio file
        if custom_caption:
            aud_list = ["filename", "filesize", "duration"]
            caption_template = escape_invalid_curly_brackets(custom_caption, aud_list)
            caption = caption_template.format(
                filename=new_filename,
                filesize=humanbytes(file.file_size),
                duration=timedelta(seconds=duration)
            )
        else:
            caption = f"**{new_filename}**"

        # Handle thumbnail processing if available
        if thumb:
            ph_path = await bot.download_media(thumb)
            try:
                # Convert and resize thumbnail for better compatibility
                Image.open(ph_path).convert("RGB").save(ph_path)
                img = Image.open(ph_path)
                img = img.resize((320, 320))
                img.save(ph_path, "JPEG")

                # Send audio with thumbnail
                await ms.edit("Trying To Upload")
                start_time = time.time()
                try:
                    await bot.send_audio(
                        update.message.chat.id,
                        audio=new_file_path,
                        caption=caption,
                        thumb=ph_path,
                        duration=duration,
                        progress=progress_for_pyrogram,
                        progress_args=("Trying To Uploading", ms, start_time)
                    )
                    await ms.delete()
                    os.remove(new_file_path)
                    os.remove(ph_path)
                except Exception as e:
                    logger.error(f"Failed to send audio: {e}")
                    await ms.edit("Error: Failed to upload audio.")
                    used_limit(update.from_user.id, used_limit_value - int(file.file_size))
                    os.remove(new_file_path)
                    os.remove(ph_path)
            except Exception as e:
                logger.error(f"Failed to process thumbnail: {e}")
                os.remove(new_file_path)
                if ph_path:
                    os.remove(ph_path)
        else:
            # Send audio without thumbnail
            await ms.edit("Trying To Upload")
            start_time = time.time()
            try:
                await bot.send_audio(
                    update.message.chat.id,
                    audio=new_file_path,
                    caption=caption,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("Trying To Uploading", ms, start_time)
                )
                await ms.delete()
                os.remove(new_file_path)
            except Exception as e:
                logger.error(f"Failed to send audio: {e}")
                await ms.edit("Error: Failed to upload audio.")
                used_limit(update.from_user.id, used_limit_value - int(file.file_size))
                os.remove(new_file_path)
    except Exception as e:
        logger.error(f"Unhandled exception in audio processing: {e}")
        await update.message.reply_text("An unexpected error occurred during audio processing.")

@Client.on_callback_query(filters.regex("doc"))
async def doc(bot, update):
    """Handles document file upload and processing."""
    try:
        new_name = update.message.text
        user_data = find_one(update.from_user.id)
        used_limit_value = user_data["used_limit"]

        # Extract new filename from the callback data
        new_filename = new_name.split(":-")[1]
        file_path = f"downloads/{new_filename}"

        # Retrieve the file from the reply message
        message = update.message.reply_to_message
        file = message.document or message.video or message.audio

        if not file:
            await update.message.reply_text("No valid file found in the reply message.")
            return

        # Update the used limit for the user
        total_used = used_limit_value + int(file.file_size)
        used_limit(update.from_user.id, total_used)

        # Notify the user about the download process
        ms = await update.message.edit("Trying To Download...")
        start_time = time.time()

        # Download the media file
        path = await bot.download_media(
            message=file,
            progress=progress_for_pyrogram,
            progress_args=("Trying To Download...", ms, start_time)
        )

        # Rename and move the downloaded file
        new_file_path = os.path.join("downloads", new_filename)
        os.rename(path, new_file_path)

        # Get user-specific data for custom caption and thumbnail
        user_id = int(update.message.chat.id)
        data = find(user_id)
        custom_caption = data.get(1, None)
        thumb = data.get(0, None)

        # Create caption for the document file
        if custom_caption:
            doc_list = ["filename", "filesize"]
            caption_template = escape_invalid_curly_brackets(custom_caption, doc_list)
            caption = caption_template.format(
                filename=new_filename,
                filesize=humanbytes(file.file_size)
            )
        else:
            caption = f"**{new_filename}**"

        # Handle thumbnail processing if available
        if thumb:
            ph_path = await bot.download_media(thumb)
            try:
                # Convert and resize thumbnail for better compatibility
                Image.open(ph_path).convert("RGB").save(ph_path)
                img = Image.open(ph_path)
                img = img.resize((320, 320))
                img.save(ph_path, "JPEG")

                # Send document with thumbnail
                await ms.edit("Trying To Upload")
                start_time = time.time()
                try:
                    await bot.send_document(
                        update.message.chat.id,
                        document=new_file_path,
                        caption=caption,
                        thumb=ph_path,
                        progress=progress_for_pyrogram,
                        progress_args=("Trying To Uploading", ms, start_time)
                    )
                    await ms.delete()
                    os.remove(new_file_path)
                    os.remove(ph_path)
                except Exception as e:
                    logger.error(f"Failed to send document: {e}")
                    await ms.edit("Error: Failed to upload document.")
                    os.remove(new_file_path)
                    os.remove(ph_path)
            except Exception as e:
                logger.error(f"Failed to process thumbnail: {e}")
                os.remove(new_file_path)
                if ph_path:
                    os.remove(ph_path)
        else:
            # Send document without thumbnail
            await ms.edit("Trying To Upload")
            start_time = time.time()
            try:
                await bot.send_document(
                    update.message.chat.id,
                    document=new_file_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("Trying To Uploading", ms, start_time)
                )
                await ms.delete()
                os.remove(new_file_path)
            except Exception as e:
                logger.error(f"Failed to send document: {e}")
                await ms.edit("Error: Failed to upload document.")
                os.remove(new_file_path)
    except Exception as e:
        logger.error(f"Unhandled exception in document processing: {e}")
        await update.message.reply_text("An unexpected error occurred during document processing.")

@Client.on_callback_query(filters.regex('rename'))
async def rename(bot, update):
    """Handles file renaming requests."""
    date_fa = str(update.message.date)
    pattern = '%Y-%m-%d %H:%M:%S'
    date = int(time.mktime(time.strptime(date_fa, pattern)))
    chat_id = update.message.chat.id
    id = update.message.reply_to_message_id

    await update.message.delete()
    await update.message.reply_text(
        f"__Please enter the new filename...__\n\nNote: Extension is not required",
        reply_to_message_id=id,
        reply_markup=ForceReply(True)
    )

    dateupdate(chat_id, date)
