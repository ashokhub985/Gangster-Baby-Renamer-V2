from pyrogram import Client, filters
from pyrogram.types import Message
import logging
import os
import ffmpeg

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

# Define your bot credentials here (or use environment variables)
API_ID = 22687964  # Replace with your API ID
API_HASH = "bdce6f5214b673c8e8295403e250e383"  # Replace with your API Hash
BOT_TOKEN = "7350352116:AAE3Km0HQBKCAy3GYnf3o38lG1MqOowgQGA"  # Replace with your Bot Token

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Command to rename the bot
async def rename_bot(client, message: Message):
    try:
        # Extract the new name from the command
        new_name = message.text.split(' ', 1)[1]  # Assuming the format is: /rename New Bot Name
        if len(new_name) == 0:
            await message.reply("Please provide a valid name.")
            return
        
        # Update the bot name
        await client.set_my_name(new_name)
        await message.reply(f"Bot name changed to: {new_name}")
        logger.info(f"Bot name changed to: {new_name}")
    
    except Exception as e:
        await message.reply("Failed to rename bot. Please try again later.")
        logger.error(f"Error while renaming bot: {str(e)}")

# Command to generate thumbnail
async def generate_thumbnail(client, message: Message):
    try:
        # Check if the message contains a video
        if not message.video:
            await message.reply("No video found to generate a thumbnail.")
            return
        
        video_file = await client.download_media(message.video.file_id)
        
        # Set the output thumbnail path
        thumbnail_path = f"{os.path.splitext(video_file)[0]}.jpg"
        
        # Generate the thumbnail using ffmpeg
        ffmpeg.input(video_file, ss=1).output(thumbnail_path, vframes=1).run()
        
        await message.reply_photo(thumbnail_path)
        logger.info(f"Thumbnail generated and sent for video: {message.video.file_name}")
    
    except Exception as e:
        await message.reply("Failed to generate thumbnail.")
        logger.error(f"Error while generating thumbnail: {str(e)}")

# Handle incoming messages
@app.on_message(filters.text)
async def handle_message(client, message: Message):
    try:
        logger.info(f"Received message: {message.text}")
        
        if message.text.lower().startswith("/rename"):
            await rename_bot(client, message)  # Renaming bot
        elif message.text.lower().startswith("/thumbnail"):
            await generate_thumbnail(client, message)  # Thumbnail generation
        else:
            await message.reply("Command not recognized. Available commands: /rename, /thumbnail")
    
    except Exception as e:
        logger.error(f"Error while handling message: {str(e)}")
        await message.reply("An error occurred while processing your message. Please try again later.")

# Run the bot
if name == "main":
    app.run()
