from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.private & filters.command(["refer"]))
async def refer(client, message):
    try:
        # Generate a shareable referral link for the user
        user_id = message.from_user.id
        share_link = f"https://t.me/share/url?url=http://t.me/Thumbnail999bot?start={user_id}"
        referral_link = f"http://t.me/Thumbnail999bot?start={user_id}"

        # Create an inline keyboard with a button for sharing the link
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Share Your Link", url=share_link)]]
        )

        # Send the referral information with the button
        await message.reply_text(
            f"Refer And Earn: Get 100MB Upload Limit\nPer Refer: 100MB\nYour Link: {referral_link}",
            reply_to_message_id=message.id,
            reply_markup=reply_markup
        )

    except Exception as e:
        # Log the error and notify the user
        print(f"Error occurred while sending referral: {e}")
        await message.reply_text("**An error occurred while generating your referral link. Please try again later.**")
