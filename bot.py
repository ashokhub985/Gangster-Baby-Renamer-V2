import asyncio
import os
import logging
import sqlite3
from PIL import Image
from pyrogram import Client, idle
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from pyrogram import Client

# Aapki API credentials
API_ID = 22687964
API_HASH = "bdce6f5214b673c8e8295403e250e383"

# Create Client instance
with Client("my_account", api_id=API_ID, api_hash=API_HASH) as app:
    session_string = app.export_session_string()
    print("\nYour Session String:")
    print(session_string)
  
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.environ.get("TOKEN", "")
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
STRING = os.environ.get("STRING", "")
CREDENTIALS_FILE = 'credentials.json'

# Database setup
db_path = 'user_profiles.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS profiles
             (user_id INTEGER PRIMARY KEY, rename_pattern TEXT, custom_caption TEXT)''')
conn.commit()

# Helper function to create a thumbnail
def create_thumbnail(input_path, output_path, size=(128, 128)):
    try:
        img = Image.open(input_path)
        img.thumbnail(size)
        img.save(output_path)
        logger.info(f"Thumbnail created and saved to {output_path}")
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")

# Function to handle photo uploads
def handle_photo(update: Update, context: CallbackContext) -> None:
    try:
        photo_file = update.message.photo[-1].get_file()
        photo_path = 'image.jpg'
        photo_file.download(photo_path)

        # Create thumbnail
        thumbnail_path = 'thumbnail.jpg'
        create_thumbnail(photo_path, thumbnail_path)

        # Send the thumbnail back to the user
        with open(thumbnail_path, 'rb') as thumbnail:
            update.message.reply_photo(photo=thumbnail, caption="Thumbnail created!")

        os.remove(photo_path)  # Clean up original image
        os.remove(thumbnail_path)  # Clean up thumbnail
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        update.message.reply_text("An error occurred while processing the photo.")

# Function to handle document uploads
def handle_document(update: Update, context: CallbackContext) -> None:
    try:
        document_file = update.message.document.get_file()
        document_path = 'document.pdf'
        document_file.download(document_path)

        # Implement renaming logic here if needed
        update.message.reply_text("Document received and processed.")
        os.remove(document_path)  # Clean up document after processing
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        update.message.reply_text("An error occurred while processing the document.")

# Function to handle audio uploads
def handle_audio(update: Update, context: CallbackContext) -> None:
    try:
        audio_file = update.message.audio.get_file()
        audio_path = 'audio.mp3'
        audio_file.download(audio_path)

        # Implement renaming logic here if needed
        update.message.reply_text("Audio received and processed.")
        os.remove(audio_path)  # Clean up audio after processing
    except Exception as e:
        logger.error(f"Error handling audio: {e}")
        update.message.reply_text("An error occurred while processing the audio.")

# Authenticate and upload a file to Google Drive
def authenticate_google_drive():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])
        creds = flow.run_local_server(port=0)
        service = build('drive', 'v3', credentials=creds)
        logger.info("Google Drive authentication successful.")
        return service
    except Exception as e:
        logger.error(f"Error authenticating Google Drive: {e}")
        raise

def upload_to_drive(file_path):
    try:
        service = authenticate_google_drive()
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='application/pdf')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        logger.info(f"File uploaded to Google Drive with ID: {file_id}")
        return file_id
    except Exception as e:
        logger.error(f"Error uploading to Google Drive: {e}")
        raise

# Main function to start the bot
def main():
    # Setup Telegram bot using Python Telegram Bot library
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.document, handle_document))
    dp.add_handler(MessageHandler(Filters.audio, handle_audio))

    # Start bot polling
    try:
        updater.start_polling()
        logger.info("Telegram bot is running.")
        updater.idle()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")

# Pyrogram client setup
def start_pyrogram_client():
    if not TOKEN or not API_ID or not API_HASH:
        logger.error("TOKEN, API_ID, and API_HASH must be set.")
        return

    bot = Client(
        "Renamer",
        bot_token=TOKEN,
        api_id=API_ID,
        api_hash=API_HASH,
        plugins=dict(root='plugins')
    )

    if STRING:
        async def start_clients():
            try:
                await bot.start()
                logger.info("Pyrogram client started successfully.")
                await idle()
            except Exception as e:
                logger.error(f"Error starting Pyrogram client: {e}")
            finally:
                await bot.stop()
                logger.info("Pyrogram client stopped successfully.")

        asyncio.run(start_clients())
    else:
        try:
            bot.run()
            logger.info("Pyrogram bot is running.")
        except Exception as e:
            logger.error(f"Error running Pyrogram bot: {e}")

if __name__ == "__main__":
    main()
    start_pyrogram_client()
