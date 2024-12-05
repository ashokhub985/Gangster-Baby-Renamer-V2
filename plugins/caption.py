import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import addcaption, find, delcaption

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@Client.on_message(filters.private & filters.command('set_caption'))
async def add_caption(client, message):
    if len(message.command) == 1:
        return await message.reply_text("**Please provide a caption to set.\n\nExample:- `/set_caption File Name`**")
    
    try:
        caption = message.text.split(" ", 1)[1]
        # Check if a caption already exists for this user
        existing_caption = find(int(message.chat.id))[1]
        if existing_caption:
            await message.reply_text("**You already have a caption set. Use `/del_caption` to remove it first.**")
            return
        
        addcaption(int(message.chat.id), caption)
        await message.reply_text("**Your caption has been successfully added ✅**")
    except Exception as e:
        logging.error(f"Error while adding caption for user {message.chat.id}: {e}")
        await message.reply_text("**An error occurred while adding your caption. Please try again later.**")

@Client.on_message(filters.private & filters.command('del_caption'))
async def delete_caption(client, message):
    try:
        caption = find(int(message.chat.id))[1]
        if not caption:
            await message.reply_text("**You don't have any custom caption to delete.**")
            return
        
        delcaption(int(message.chat.id))
        await message.reply_text("**Your caption has been successfully deleted ✅**")
    except Exception as e:
        logging.error(f"Error while deleting caption for user {message.chat.id}: {e}")
        await message.reply_text("**An error occurred while deleting your caption. Please try again later.**")

@Client.on_message(filters.private & filters.command('see_caption'))
async def see_caption(client, message):
    try:
        caption = find(int(message.chat.id))[1]
        if caption:
            await message.reply_text(f"<b><u>Your Caption:</b></u>\n\n`{caption}`")
        else:
            await message.reply_text("**You don't have any custom caption.**")
    except Exception as e:
        logging.error(f"Error while fetching caption for user {message.chat.id}: {e}")
        await message.reply_text("**An error occurred while fetching your caption. Please try again later.**")
