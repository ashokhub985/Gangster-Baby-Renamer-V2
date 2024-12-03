from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
)

@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    # Check if the replied message has a ForceReply markup
    if message.reply_to_message.reply_markup and isinstance(message.reply_to_message.reply_markup, ForceReply):
        new_name = message.text  # Extract the new file name
        await message.delete()  # Delete the user's message

        # Retrieve the media message
        media = await client.get_messages(message.chat.id, message.reply_to_message.id)
        file = media.reply_to_message.document or media.reply_to_message.video or media.reply_to_message.audio

        if not file:
            await message.reply_text("**Error**: No file found in the replied message.")
            return

        filename = file.file_name  # Original file name
        mime = file.mime_type.split("/")[0]  # Extract MIME type (e.g., video, audio)
        mg_id = media.reply_to_message.id

        # Validate the new name and determine the output file name
        try:
            if "." in new_name:
                # If extension is provided in the new name
                out_filename = new_name
            else:
                # Use original extension if not provided
                out_filename = f"{new_name}.{filename.split('.')[-1]}"
        except Exception as e:
            await message.reply_text(f"**Error**: Invalid file name. {e}", reply_to_message_id=mg_id)
            return

        # Delete the replied message after processing
        await message.reply_to_message.delete()

        # Define the InlineKeyboardMarkup based on file type
        keyboard_options = {
            "video": [
                [
                    InlineKeyboardButton("📁 Document", callback_data="doc"),
                    InlineKeyboardButton("🎥 Video", callback_data="vid")
                ]
            ],
            "audio": [
                [
                    InlineKeyboardButton("📁 Document", callback_data="doc"),
                    InlineKeyboardButton("🎵 Audio", callback_data="aud")
                ]
            ],
            "default": [
                [InlineKeyboardButton("📁 Document", callback_data="doc")]
            ]
        }

        # Select appropriate keyboard based on MIME type
        markup = InlineKeyboardMarkup(keyboard_options.get(mime, keyboard_options["default"]))

        # Send a message with the output file name and options
        await message.reply_text(
            f"**Select the output file type**\n**Output FileName**: ```{out_filename}```",
            reply_to_message_id=mg_id,
            reply_markup=markup
        )
