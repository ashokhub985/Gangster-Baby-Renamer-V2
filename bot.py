import asyncio
import os
import logging
from pyrogram import Client, idle, compose
from plugins.cb_data import app as Client2
import os
import sqlite3
from PIL import Image
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from werkzeug.utils import quote as url_quote
import os
import sqlite3
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Database setup
conn = sqlite3.connect('user_profiles.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS profiles
             (user_id INTEGER PRIMARY KEY, rename_pattern TEXT, custom_caption TEXT)''')
conn.commit()

# Function to create a thumbnail
def create_thumbnail(video_path, thumbnail_path):
    # Use ffmpeg or similar to create a thumbnail from the video
    os.system(f"ffmpeg -i {video_path} -ss 00:00:01.000 -vframes 1 {thumbnail_path}")

# Function to handle video uploads from the channel
def handle_channel_video(update: Update, context: CallbackContext) -> None:
    video_file = update.message.video.get_file()
    video_file.download('video.mp4')

    # Create thumbnail for the video
    create_thumbnail('video.mp4', 'thumbnail.jpg')

    # Send the thumbnail back to the channel (or user)
    with open('thumbnail.jpg', 'rb') as thumbnail:
        context.bot.send_photo(chat_id=update.message.chat_id, photo=thumbnail, caption="Thumbnail created!")

    # Delete original video file after upload
    os.remove('video.mp4')

# Main function to start the bot
def main():
    updater = Updater("")

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.video, handle_channel_video))

    updater.start_polling()
    updater.idle()

# Database setup
conn = sqlite3.connect('user_profiles.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS profiles
             (user_id INTEGER PRIMARY KEY, rename_pattern TEXT, custom_caption TEXT)''')
conn.commit()

# Function to create a thumbnail
def create_thumbnail(image_path, thumbnail_path):
    img = Image.open(image_path)
    img.thumbnail((128, 128))
    img.save(thumbnail_path)

# Function to save user preferences
def save_user_preferences(user_id, rename_pattern, custom_caption):
    c.execute("INSERT OR REPLACE INTO profiles (user_id, rename_pattern, custom_caption) VALUES (?, ?, ?)",
              (user_id, rename_pattern, custom_caption))
    conn.commit()

# Function to handle photo uploads
def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('image.jpg')

    # Create thumbnail
    create_thumbnail('image.jpg', 'thumbnail.jpg')

    # Send the thumbnail back to the user
    with open('thumbnail.jpg', 'rb') as thumbnail:
        update.message.reply_photo(photo=thumbnail, caption="Thumbnail created!")

# Function to handle document uploads
def handle_document(update: Update, context: CallbackContext) -> None:
    document_file = update.message.document.get_file()
    document_file.download('document.pdf')
    # Implement renaming logic for documents here
    update.message.reply_text("Document received and processed.")

# Function to handle audio uploads
def handle_audio(update: Update, context: CallbackContext) -> None:
    audio_file = update.message.audio.get_file()
    audio_file.download('audio.mp3')
    # Implement renaming logic for audio files here
    update.message.reply_text("Audio received and processed.")

# Function to authenticate Google Drive
def authenticate_google_drive():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive.file'])
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)
    return service

# Function to upload a file to Google Drive
def upload_to_drive(file_path):
    service = authenticate_google_drive()
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='application/pdf')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Main function to start the bot
def main():
    updater = Updater("")

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.document, handle_document))
    dp.add_handler(MessageHandler(Filters.audio, handle_audio))

    updater.start_polling()
    updater.idle()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.environ.get("TOKEN", "")
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
STRING = os.environ.get("STRING", "")

# Validate required environment variables
if not TOKEN or not API_ID or not API_HASH:
    logger.error("TOKEN, API_ID, and API_HASH must be set.")
    exit(1)

# Create clients
bot = Client(
    "Renamer",
    bot_token=TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root='plugins')
)

if STRING:
    # Start multiple clients if STRING is provided
    apps = [Client2, bot]

    async def start_clients():
        try:
            for app in apps:
                await app.start()
                logger.info(f"{app} started successfully.")
            
            await idle()
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        
        finally:
            for app in apps:
                await app.stop()
                logger.info(f"{app} stopped successfully.")

    asyncio.run(start_clients())
else:
    # Run the single bot instance
    try:
        bot.run()
        logger.info("Bot is running.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    app.run()  # Example for Flask

