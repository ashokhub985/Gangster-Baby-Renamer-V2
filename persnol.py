import os
import time
from pyrogram import Client, filters
from pyrogram.types import InputMediaVideo
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import ffmpeg

# Replace with your own details
API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
STRING = os.environ.get("STRING", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")  # The channel to process

app = Client("video_processor", api_id=API_ID, api_hash=API_HASH, session_string=STRING)

# Function to download video
async def download_video(message):
    try:
        file_path = await app.download_media(message, file_name="downloads/")
        return file_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# Function to process video (e.g., change thumbnail)
def process_video(file_path, new_thumbnail_path):
    try:
        # Generate a new thumbnail using FFmpeg
        thumbnail_path = new_thumbnail_path or 'default_thumbnail.jpg'
        output_path = 'processed_video.mp4'
        
        # Extracting the first frame as a thumbnail
        ffmpeg.input(file_path, ss=1).output(thumbnail_path, vframes=1).run()

        # Replace thumbnail in video (this is simplified, FFmpeg command may vary)
        ffmpeg.input(file_path).output(output_path, v='copy', map='0', map='1').run()
        
        return output_path
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

# Function to upload video
async def upload_video(file_path, caption, chat_id):
    try:
        await app.send_video(chat_id, file_path, caption=caption)
        os.remove(file_path)  # Clean up after upload
    except Exception as e:
        print(f"Error uploading video: {e}")

# Function to delete original video
async def delete_original_video(message_id, chat_id):
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting original video: {e}")

# Main function to process the channel's videos
async def process_channel_videos():
    async for message in app.get_chat_history(CHANNEL_ID):
        if message.video:
            print(f"Processing video: {message.video.file_name}")
            file_path = await download_video(message)
            
            if file_path:
                processed_path = process_video(file_path, 'thumbnail_path.jpg')
                
                if processed_path:
                    caption = f"Updated caption for {message.video.file_name}"
                    await upload_video(processed_path, caption, CHANNEL_ID)
                    await delete_original_video(message.message_id, CHANNEL_ID)

# Start the bot
app.run(process_channel_videos)



import asyncio
import logging
import os
import time
from datetime import timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.ffmpeg import take_screen_shot, fix_thumb
from helper.database import find, find_one, used_limit, dateupdate
from helper.progress import progress_for_pyrogram, humanbytes
from helper.set import escape_invalid_curly_brackets

# Advanced logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
STRING = os.environ.get("STRING", "")
ADMIN = int(os.environ.get("ADMIN", ""))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
DOWNLOAD_DIR = "downloads"

app = Client("advanced_bot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)

async def download_video(bot, message: Message):
    try:
        file = message.document or message.video or message.audio
        if not file:
            logger.warning(f"No valid file found in message ID {message.message_id}")
            return None

        path = await bot.download_media(file, progress=progress_for_pyrogram, progress_args=("Downloading...", None, time.time()))
        logger.info(f"Downloaded file to {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        return None

async def process_video(video_path: str, thumbnail_path: str = None):
    try:
        # Generate a new thumbnail if needed
        if thumbnail_path:
            # Advanced image processing here, like resizing and adding effects
            img = Image.open(thumbnail_path)
            img = img.resize((320, 320))
            img.save(thumbnail_path, "JPEG")

        # Video processing logic (e.g., re-encoding, adding metadata)
        output_path = f"{DOWNLOAD_DIR}/processed_{os.path.basename(video_path)}"
        take_screen_shot(video_path, output_path)
        return output_path
    except Exception as e:
        logger.error(f"Failed to process video {video_path}: {e}")
        return None

async def upload_video(bot, chat_id, file_path, caption=None, duration=None, thumbnail_path=None):
    try:
        await bot.send_video(chat_id, video=file_path, caption=caption, duration=duration, thumb=thumbnail_path)
        logger.info(f"Uploaded video: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload video {file_path}: {e}")
        return False

async def delete_original_video(bot, chat_id, message_id):
    try:
        await bot.delete_messages(chat_id, message_id)
        logger.info(f"Deleted original video message ID {message_id}")
    except Exception as e:
        logger.error(f"Failed to delete message ID {message_id}: {e}")

@app.on_callback_query(filters.regex("process_video"))
async def process_and_upload(bot, update):
    try:
        message = update.message.reply_to_message
        if not message:
            await update.message.edit("Error: No message to process.")
            return

        # Step 1: Download the video
        video_path = await download_video(bot, message)
        if not video_path:
            await update.message.edit("Failed to download video.")
            return

        # Step 2: Process the video
        processed_video_path = await process_video(video_path)
        if not processed_video_path:
            await update.message.edit("Failed to process video.")
            return

        # Step 3: Upload the processed video
        caption = "Your custom caption here"
        success = await upload_video(bot, update.message.chat.id, processed_video_path, caption=caption)
        if not success:
            await update.message.edit("Failed to upload video.")
            return

        # Step 4: Delete the original video message
        await delete_original_video(bot, update.message.chat.id, message.message_id)

        await update.message.edit("Video processed and uploaded successfully.")
    except Exception as e:
        logger.error(f"An error occurred during video processing: {e}")
        await update.message.edit("An unexpected error occurred.")

# Run the bot
if __name__ == "__main__":
    app.run()


import os
import time
import shutil
import ffmpeg
import openai
from PIL import Image, ImageDraw, ImageFont
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, filters
from pyrogram.types import ForceReply
from moviepy.video.io.VideoFileClip import VideoFileClip
from googletrans import Translator
import speech_recognition as sr

# Initialize OpenAI
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize Scheduler for periodic tasks
scheduler = AsyncIOScheduler()
scheduler.start()

# Define the client
app = Client("my_bot")

# Function for optimizing video quality
def optimize_video(input_path, output_path):
    ffmpeg.input(input_path).output(output_path, vf='scale=1280:720').run()

# Function for adding watermark
def add_watermark(input_path, output_path, watermark_text="Sample Watermark"):
    base = Image.open(input_path).convert('RGBA')
    width, height = base.size
    watermark = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    font = ImageFont.load_default()
    draw.text((width - 100, height - 50), watermark_text, font=font, fill=(255, 255, 255, 128))
    watermarked = Image.alpha_composite(base, watermark)
    watermarked.save(output_path, 'PNG')

# Function for speech-to-text conversion
def speech_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
        return recognizer.recognize_google(audio)

# Function for generating video preview
def generate_preview(file_path, preview_path, start_time=0, duration=10):
    clip = VideoFileClip(file_path).subclip(start_time, duration)
    clip.write_videofile(preview_path, codec='libx264')

# Function to translate captions
def translate_caption(caption, target_language='es'):
    translator = Translator()
    translated = translator.translate(caption, dest=target_language)
    return translated.text

# Function for content moderation
def moderate_content(file_path):
    response = requests.post(
        'https://api.deepai.org/api/nsfw-detector',
        files={'image': open(file_path, 'rb')},
        headers={'api-key': 'YOUR_API_KEY'}
    )
    return response.json()

# Scheduled task for automatic updates
async def scheduled_video_update():
    print("Scheduled video update started.")
    # Add logic to fetch and update videos

# Adding the scheduled task
scheduler.add_job(scheduled_video_update, 'interval', hours=1)

# Function for downloading and updating video details
@app.on_callback_query(filters.regex('update_video'))
async def update_video(bot, update):
    try:
        message = update.message.reply_to_message
        file = message.document or message.video or message.audio
        if not file:
            await update.message.reply_text("No file found.")
            return

        # Download file
        file_path = f"downloads/{file.file_name}"
        await bot.download_media(file, file_path)

        # Optimize video and add watermark
        optimized_path = f"downloads/optimized_{file.file_name}"
        optimize_video(file_path, optimized_path)
        watermark_path = f"downloads/watermarked_{file.file_name}"
        add_watermark(optimized_path, watermark_path)

        # Generate preview
        preview_path = f"downloads/preview_{file.file_name}"
        generate_preview(watermarked_path, preview_path)

        # Translate caption
        caption = "Your new caption here"
        translated_caption = translate_caption(caption)

        # Send the video with updated details
        await bot.send_video(
            update.message.chat.id,
            video=watermarked_path,
            caption=translated_caption,
            thumb=preview_path
        )

        # Clean up files after sending
        os.remove(file_path)
        os.remove(optimized_path)
        os.remove(watermarked_path)
        os.remove(preview_path)

        await update.message.reply_text("Video updated successfully.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Start the bot
app.run()


import os
import time
import shutil
import logging
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip
from pyrogram import Client, filters
from pyrogram.types import ForceReply
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import openai
from googletrans import Translator
import speech_recognition as sr
import ffmpeg
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize the scheduler for automated tasks
scheduler = AsyncIOScheduler()
scheduler.start()

# Define the client
app = Client("my_bot")

# Helper function to create a timestamped backup
def backup_file(file_path):
    if os.path.exists(file_path):
        backup_path = f"backups/{os.path.basename(file_path)}_{int(time.time())}"
        shutil.copy(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return backup_path
    return None

# Function to optimize video quality
def optimize_video(input_path, output_path):
    logger.info(f"Optimizing video: {input_path}")
    ffmpeg.input(input_path).output(output_path, vf='scale=1280:720').run()

# Function to add watermark to a video
def add_watermark(input_path, output_path, watermark_text="Sample Watermark"):
    logger.info(f"Adding watermark to: {input_path}")
    base = Image.open(input_path).convert('RGBA')
    width, height = base.size
    watermark = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    font = ImageFont.load_default()
    draw.text((width - 100, height - 50), watermark_text, font=font, fill=(255, 255, 255, 128))
    watermarked = Image.alpha_composite(base, watermark)
    watermarked.save(output_path, 'PNG')

# Function for speech-to-text conversion
def speech_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
        return recognizer.recognize_google(audio)

# Function to generate a video preview
def generate_preview(file_path, preview_path, start_time=0, duration=10):
    logger.info(f"Generating preview for: {file_path}")
    clip = VideoFileClip(file_path).subclip(start_time, duration)
    clip.write_videofile(preview_path, codec='libx264')

# Function to translate captions
def translate_caption(caption, target_language='es'):
    translator = Translator()
    translated = translator.translate(caption, dest=target_language)
    return translated.text

# Function to perform content moderation
def moderate_content(file_path):
    logger.info(f"Moderating content: {file_path}")
    response = requests.post(
        'https://api.deepai.org/api/nsfw-detector',
        files={'image': open(file_path, 'rb')},
        headers={'api-key': 'YOUR_DEEPAI_API_KEY'}
    )
    return response.json()

# Function for handling errors gracefully
def handle_error(bot, update, error_message):
    logger.error(f"Error occurred: {error_message}")
    try:
        update.message.reply_text(f"An error occurred: {error_message}")
    except:
        logger.error("Failed to send error message to the user")

# Scheduled task for automatic updates
async def scheduled_video_update():
    logger.info("Scheduled video update started.")
    # Placeholder for video update logic
    # You can use this to periodically check and process new videos

# Adding the scheduled task to the scheduler
scheduler.add_job(scheduled_video_update, 'interval', hours=1)

# Function for downloading and updating video details
@app.on_callback_query(filters.regex('update_video'))
async def update_video(bot, update):
    try:
        message = update.message.reply_to_message
        file = message.document or message.video or message.audio
        if not file:
            await update.message.reply_text("No file found.")
            return

        # Download the original file
        file_path = f"downloads/{file.file_name}"
        await bot.download_media(file, file_path)

        # Backup the original file
        backup_file(file_path)

        # Optimize the video and add a watermark
        optimized_path = f"downloads/optimized_{file.file_name}"
        optimize_video(file_path, optimized_path)

        watermark_path = f"downloads/watermarked_{file.file_name}"
        add_watermark(optimized_path, watermark_path)

        # Generate a preview of the video
        preview_path = f"downloads/preview_{file.file_name}"
        generate_preview(watermarked_path, preview_path)

        # Translate the caption if needed
        caption = "Your new caption here"
        translated_caption = translate_caption(caption)

        # Check content moderation
        moderation_result = moderate_content(watermarked_path)
        if moderation_result['output']['nsfw_score'] > 0.5:
            logger.warning("Content flagged as NSFW.")
            await update.message.reply_text("The content has been flagged as NSFW and will not be uploaded.")
            return

        # Send the video with updated details
        await bot.send_video(
            update.message.chat.id,
            video=watermarked_path,
            caption=translated_caption,
            thumb=preview_path
        )

        # Clean up files after sending
        os.remove(file_path)
        os.remove(optimized_path)
        os.remove(watermarked_path)
        os.remove(preview_path)

        await update.message.reply_text("Video updated successfully.")
    except Exception as e:
        handle_error(bot, update, str(e))

# Start the bot
app.run()
