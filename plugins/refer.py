from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.private & filters.command(["refer"]))
async def refer(client, message):
    # Generate a shareable link for the user
    share_link = f"https://t.me/share/url?url=https://t.me/GangsterBaby_renamer_BOT?start={message.from_user.id}"
    referral_link = f"https://t.me/LazyStar_BOT?start={message.from_user.id}"

    # Create the inline keyboard with a button to share the link
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Share Your Link", url=share_link)]]
    )

    # Send the message with referral information and inline keyboard
    await message.reply_text(
        f"Refer And Earn: Get 100MB Upload Limit\nPer Refer: 100MB\nYour Link: {referral_link}",
        reply_to_message_id=message.id,
        reply_markup=reply_markup
    )
