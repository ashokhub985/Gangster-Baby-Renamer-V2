import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import botdata, find_one, total_user, getid
from helper.progress import humanbytes

# Initialize Bot ID and Admin ID
token = os.getenv("TOKEN", "")
botid = token.split(":")[0]
ADMIN = int(os.getenv("ADMIN", "0"))

if not token or not ADMIN:
    raise ValueError("TOKEN or ADMIN environmental variable is missing!")

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["lazyusers"]))
async def lazy_users(client, message):
    try:
        # Initialize bot data
        botdata(int(botid))
        data = find_one(int(botid))

        if not data:
            await message.reply_text("**Error**: Bot data not found.", quote=True)
            return

        # Fetch details from the database
        total_rename = data.get("total_rename", 0)
        total_size = data.get("total_size", 0)
        id_list = str(getid()).split(",")
        total_users = total_user()

        # Format human-readable message
        ids_formatted = "\n".join([f"🆔 {user_id}" for user_id in id_list if user_id.strip()])
        reply_text = (
            f"⚡️ **All User IDs**:\n{ids_formatted}\n\n"
            f"⚡️ **Total Users**: {total_users}\n"
            f"⚡️ **Total Renamed Files**: {total_rename}\n"
            f"⚡️ **Total Size Renamed**: {humanbytes(int(total_size))}"
        )

        # Send response with close menu button
        await message.reply_text(
            reply_text,
            quote=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🦋 Close Menu 🦋", callback_data="cancel")]]
            )
        )

    except Exception as e:
        # Log error and notify admin
        await message.reply_text(f"**Error**: {str(e)}", quote=True)
