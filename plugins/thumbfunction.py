import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from helper.database import find, delthumb, addthumb

# Setting up logging for better debugging
logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.private & filters.command(['viewthumb']))
async def viewthumb(client, message: Message):
    try:
        # Check if there is a custom thumbnail in the database
        file_id = find(message.chat.id)
        if file_id:
            logging.info(f"User {message.chat.id} viewed their custom thumbnail.")
            await message.reply_photo(file_id, caption="**Here is your custom thumbnail**")
        else:
            logging.info(f"User {message.chat.id} does not have a custom thumbnail.")
            await message.reply_text("**You don't have any custom thumbnail**")
    except Exception as e:
        logging.error(f"Error retrieving thumbnail for user {message.chat.id}: {e}")
        await message.reply_text(f"Error retrieving thumbnail: {e}")

@Client.on_message(filters.private & filters.command(['delthumb']))
async def removethumb(client, message: Message):
    try:
        delthumb(message.chat.id)  # Remove the custom thumbnail from the database
        logging.info(f"User {message.chat.id} deleted their custom thumbnail.")
        await message.reply_text("**Custom thumbnail deleted successfully**")
    except Exception as e:
        logging.error(f"Error deleting thumbnail for user {message.chat.id}: {e}")
        await message.reply_text(f"Error deleting thumbnail: {e}")

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message: Message):
    try:
        file_id = str(message.photo.file_id)
        addthumb(message.chat.id, file_id)  # Save the custom thumbnail to the database
        logging.info(f"User {message.chat.id} added a custom thumbnail with file ID {file_id}.")
        await message.reply_text("**Custom thumbnail saved successfully** ✅")
    except Exception as e:
        logging.error(f"Error saving thumbnail for user {message.chat.id}: {e}")
        await message.reply_text(f"Error saving thumbnail: {e}")
