import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import (
    find_one, used_limit, daily as daily_,
    uploadlimit, usertype
)
from helper.date import check_expi
from helper.progress import humanbytes
from datetime import datetime, date

@Client.on_message(filters.private & filters.command(["myplan"]))
async def show_plan(client, message):
    user_id = message.from_user.id
    
    try:
        # Fetch user data from the database
        user_data = find_one(user_id)

        # Check if user data is found
        if not user_data:
            await message.reply_text("**Error**: User data not found.", quote=True)
            return

        # Check for daily reset and update limits if needed
        daily = user_data["daily"]
        current_date_epoch = int(time.mktime(time.strptime(str(date.today()), '%Y-%m-%d')))
        if daily != current_date_epoch:
            daily_(user_id, current_date_epoch)
            used_limit(user_id, 0)

        # Fetch updated user data
        user_data = find_one(user_id)
        used = user_data["used_limit"]
        limit = user_data["uploadlimit"]
        remaining = limit - used
        user_type = user_data["usertype"]
        expiration_date = user_data["prexdate"]

        # Check for plan expiration and reset if needed
        if expiration_date and not check_expi(expiration_date):
            uploadlimit(user_id, 1288490188)  # Unlimited or reset
            usertype(user_id, "Free")

        # Build the response message
        if expiration_date is None:
            message_text = (
                f"User ID: ```{user_id}```\n"
                f"Plan: {user_type}\n"
                f"Daily Upload Limit: {humanbytes(limit)}\n"
                f"Today Used: {humanbytes(used)}\n"
                f"Remaining: {humanbytes(remaining)}"
            )
        else:
            expiration_date_formatted = datetime.fromtimestamp(expiration_date).strftime('%Y-%m-%d')
            message_text = (
                f"User ID: ```{user_id}```\n"
                f"Plan: {user_type}\n"
                f"Daily Upload Limit: {humanbytes(limit)}\n"
                f"Today Used: {humanbytes(used)}\n"
                f"Remaining: {humanbytes(remaining)}\n\n"
                f"Your Plan Ends On: {expiration_date_formatted}"
            )

        # Respond with a keyboard for Free users
        if user_type == "Free":
            await message.reply(
                message_text,
                quote=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Upgrade 💰💳", callback_data="upgrade"),
                     InlineKeyboardButton("Cancel ✖️", callback_data="cancel")]
                ])
            )
        else:
            await message.reply(message_text, quote=True)

    except Exception as e:
        # Log error and inform the user
        print(f"Error occurred while showing plan: {e}")
        await message.reply_text(f"**Error**: {str(e)}", quote=True)
