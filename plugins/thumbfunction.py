from pyrogram import Client, filters
from helper.database import find, delthumb, addthumb

# View custom thumbnail command
@Client.on_message(filters.private & filters.command(['viewthumb']))
async def viewthumb(client, message):
    print(f"Received viewthumb request from chat ID: {message.chat.id}")
    thumb = find(int(message.chat.id))[0]  # Fetch the custom thumbnail file ID

    if thumb:
        try:
            await client.send_photo(message.chat.id, photo=thumb)
        except Exception as e:
            await message.reply_text(f"Error sending thumbnail: {e}")
    else:
        await message.reply_text("**You don't have any custom thumbnail**")

# Delete custom thumbnail command
@Client.on_message(filters.private & filters.command(['delthumb']))
async def removethumb(client, message):
    try:
        delthumb(int(message.chat.id))  # Remove the custom thumbnail from the database
        await message.reply_text("**Custom thumbnail deleted successfully**")
    except Exception as e:
        await message.reply_text(f"Error deleting thumbnail: {e}")

# Add custom thumbnail command (triggered by a photo)
@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    file_id = str(message.photo.file_id)
    
    try:
        addthumb(message.chat.id, file_id)  # Save the custom thumbnail to the database
        await message.reply_text("**Custom thumbnail saved successfully** ✅")
    except Exception as e:
        await message.reply_text(f"Error saving thumbnail: {e}")
