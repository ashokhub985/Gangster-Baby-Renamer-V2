from pyrogram import Client, filters
from pyrogram.types import Message
from helper.database import find, delthumb, addthumb

# View custom thumbnail command
@Client.on_message(filters.private & filters.command(['viewthumb']))
async def viewthumb(client, message: Message):
    try:
        # Check if there is a custom thumbnail in the database
        file_id = find(message.chat.id)
        if file_id:
            await message.reply_photo(file_id, caption="**Here is your custom thumbnail**")
        else:
            await message.reply_text("**You don't have any custom thumbnail**")
    except Exception as e:
        await message.reply_text(f"Error retrieving thumbnail: {e}")

# Delete custom thumbnail command
@Client.on_message(filters.private & filters.command(['delthumb']))
async def removethumb(client, message: Message):
    try:
        delthumb(message.chat.id)  # Remove the custom thumbnail from the database
        await message.reply_text("**Custom thumbnail deleted successfully**")
    except Exception as e:
        await message.reply_text(f"Error deleting thumbnail: {e}")

# Add custom thumbnail command (triggered by a photo)
@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message: Message):
    try:
        file_id = str(message.photo.file_id)
        addthumb(message.chat.id, file_id)  # Save the custom thumbnail to the database
        await message.reply_text("**Custom thumbnail saved successfully** ✅")
    except Exception as e:
        await message.reply_text(f"Error saving thumbnail: {e}")
