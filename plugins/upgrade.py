"""lokaman"""
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Function to generate the upgrade message and keyboard
def get_upgrade_text_and_keyboard():
    text = """**Free Plan User**
    Daily Upload limit 1.2GB
    Price 0

    **🦙 Silver Tier 🦙** 
    Daily Upload limit 10GB
    Price Rs 66 ind /🌎 0.8$ per Month

    **💫 Gold Tier 💫**
    Daily Upload limit 50GB
    Price Rs 100 ind /🌎 1.2$ per Month

    **💎 Diamond 💎**
    Daily Upload limit 100GB
    Price Rs 206 ind /🌎 2.5$ per Month

    Pay Using UPI ID: 
    7808912076@paytm

    After Payment, send screenshots of the payment to Admin @mRiderDM"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ADMIN 🛂", url="https://t.me/mRiderDM")],
        [InlineKeyboardButton("Paytm", url="https://p.paytm.me/xCTH/vo37hii9")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])
    return text, keyboard

# Callback query handler for "upgrade"
@Client.on_callback_query(filters.regex('upgrade'))
async def upgrade_callback(bot, update):
    text, keyboard = get_upgrade_text_and_keyboard()
    await update.message.edit(text=text, reply_markup=keyboard)

# Command handler for "/upgrade"
@Client.on_message(filters.private & filters.command(["upgrade"]))
async def upgrade_command(bot, message):
    text, keyboard = get_upgrade_text_and_keyboard()
    await message.reply_text(text=text, reply_markup=keyboard)
