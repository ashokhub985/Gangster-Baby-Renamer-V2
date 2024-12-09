import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import uploadlimit, usertype, addpre, find_one, botdata
from helper.progress import humanbytes

# Setting up logging for debugging and error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables for admin and log channel
ADMIN = int(os.environ.get("ADMIN", ""))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["warn"]))
async def warn(client, message):
    """ Warn a user with a specific reason """
    if len(message.command) >= 3:
        try:
            user_id = int(message.text.split(' ', 2)[1])
            reason = message.text.split(' ', 2)[2]
            await client.send_message(chat_id=user_id, text=reason)
            await message.reply_text("User notified successfully.")
        except ValueError:
            await message.reply_text("Invalid user ID. Please provide a valid number.")
        except Exception as e:
            await message.reply_text(f"An error occurred while notifying the user: {e}")
            logging.error(f"Error while notifying user: {e}")

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["addpremium"]))
async def buypremium(bot, message):
    """ Display premium plan options """
    await message.reply_text(
        "🦋 Select Plan to upgrade...",
        quote=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🪙 Silver", callback_data="vip1")],
            [InlineKeyboardButton("💫 Gold", callback_data="vip2")],
            [InlineKeyboardButton("💎 Diamond", callback_data="vip3")]
        ])
    )

@Client.on_message((filters.channel | filters.private) & filters.user(ADMIN) & filters.command(["ceasepower"]))
async def ceasepremium(bot, message):
    """ Display options to cease or limit user power """
    await message.reply_text(
        "POWER CEASE MODE",
        quote=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("•× Limit 500MB ×•", callback_data="cp1"),
             InlineKeyboardButton("•× Limit 100MB ×•", callback_data="cp2")],
            [InlineKeyboardButton("•••× CEASE ALL POWER ×•••", callback_data="cp3")]
        ])
    )

@Client.on_message((filters.channel | filters.private) & filters.user(ADMIN) & filters.command(["resetpower"]))
async def resetpower(bot, message):
    """ Confirm reset of user data limits """
    await message.reply_text(
        text="Do you really want to reset daily limit to default data limit 1.2GB?",
        quote=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• YES ! Set as Default •", callback_data="dft")],
            [InlineKeyboardButton("❌ Cancel ❌", callback_data="cancel")]
        ])
    )

async def upgrade_user_limit(user_id, limit, plan_name, message, bot):
    """ Upgrade or downgrade user limit and plan """
    try:
        uploadlimit(user_id, limit)
        usertype(user_id, plan_name)
        addpre(user_id)
        await message.edit(f"Added successfully to {plan_name} plan with a limit of {humanbytes(limit)}.")
        await bot.send_message(user_id, f"Hey, you are upgraded to {plan_name}. Check your plan here /myplan.")
        await bot.send_message(LOG_CHANNEL, f"⚡️ Plan upgraded to {plan_name} for user {user_id}.")
        logging.info(f"User {user_id} upgraded to {plan_name} with limit {humanbytes(limit)}")
    except Exception as e:
        await message.edit("An error occurred while upgrading the user.")
        logging.error(f"Error upgrading user {user_id}: {e}")

# Callback handlers for upgrading user plans
@Client.on_callback_query(filters.regex('vip1'))
async def vip1(bot, update):
    """ Handle Silver plan upgrade """
    user_id = int(update.message.reply_to_message.text.split("/addpremium")[1].strip())
    await upgrade_user_limit(user_id, 10737418240, "🪙 **SILVER**", update.message, bot)

@Client.on_callback_query(filters.regex('vip2'))
async def vip2(bot, update):
    """ Handle Gold plan upgrade """
    user_id = int(update.message.reply_to_message.text.split("/addpremium")[1].strip())
    await upgrade_user_limit(user_id, 53687091200, "💫 **GOLD**", update.message, bot)

@Client.on_callback_query(filters.regex('vip3'))
async def vip3(bot, update):
    """ Handle Diamond plan upgrade """
    user_id = int(update.message.reply_to_message.text.split("/addpremium")[1].strip())
    await upgrade_user_limit(user_id, 107374182400, "💎 **DIAMOND**", update.message, bot)

# Callback handlers for limiting or ceasing user power
@Client.on_callback_query(filters.regex('cp1'))
async def cp1(bot, update):
    """ Limit user to 500MB data usage """
    user_id = int(update.message.reply_to_message.text.split("/ceasepower")[1].strip())
    await upgrade_user_limit(user_id, 524288000, "**ACCOUNT DOWNGRADED**", update.message, bot)
    await bot.send_message(user_id, "⚠️ Warning ⚠️\n\n- ACCOUNT DOWNGRADED\nYou can only use 500MB/day from Data quota. Check your plan here - /myplan.")

@Client.on_callback_query(filters.regex('cp2'))
async def cp2(bot, update):
    """ Limit user to 100MB data usage """
    user_id = int(update.message.reply_to_message.text.split("/ceasepower")[1].strip())
    await upgrade_user_limit(user_id, 104857600, "**ACCOUNT DOWNGRADED Lv-2**", update.message, bot)
    await bot.send_message(user_id, "⛔️ Last Warning ⛔️\n\n- ACCOUNT DOWNGRADED to Level 2\nYou can only use 100MB/day from Data quota. Check your plan here - /myplan.")

@Client.on_callback_query(filters.regex('cp3'))
async def cp3(bot, update):
    """ Cease all user powers """
    user_id = int(update.message.reply_to_message.text.split("/ceasepower")[1].strip())
    await upgrade_user_limit(user_id, 0, "**POWER CEASED!**", update.message, bot)
    await bot.send_message(user_id, "🚫 All POWER CEASED 🚫\n\n- All power has been ceased from you. From now you can't rename files using me. Check your plan here - /myplan.")

@Client.on_callback_query(filters.regex('dft'))
async def dft(bot, update):
    """ Reset user data limit to default (1.2GB) """
    user_id = int(update.message.reply_to_message.text.split("/resetpower")[1].strip())
    await upgrade_user_limit(user_id, 1288490188, "**Free**", update.message, bot)
    await bot.send_message(user_id, "Your daily data limit has been reset successfully.\n\nCheck your plan here - /myplan.")
