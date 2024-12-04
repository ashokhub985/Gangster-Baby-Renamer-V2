from datetime import date as date_
import datetime
import os
import time
import humanize
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper.progress import humanbytes
from helper.database import (
    insert, find_one, used_limit, usertype, uploadlimit, addpredata, 
    total_rename, total_size, daily as daily_
)
from pyrogram.file_id import FileId
from helper.date import check_expi
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment Variables
CHANNEL = os.environ.get('CHANNEL', "-1002460917426")
STRING = os.environ.get("STRING", "")
ADMIN = int(os.environ.get("ADMIN", 862729509))
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Thumbnailforagentbot")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002247619392"))
TOKEN = os.environ.get('TOKEN', '7779296728:AAFFJu5Om-Nv7PGmwniWUTG14P4BSQS8K04')
BOTID = TOKEN.split(':')[0]
FLOOD = 500
LAZY_PIC = os.environ.get("LAZY_PIC", "https://graph.org/file/7519d226226bec1090db7.jpg")

# Current Time and Greeting Logic
current_time = datetime.datetime.now()
if current_time.hour < 12:
    WISH = "❤️ Good morning sweetheart ❤️"
elif 12 <= current_time.hour < 17:
    WISH = '🤍 Good afternoon my Love 🤍'
else:
    WISH = '🦋 Good evening baby 🦋'

# Command to start the bot
@Client.on_message(filters.private & filters.command(["start"]))
async def start(client, message):
    old = insert(int(message.chat.id))
    try:
        user_id = int(message.text.split(' ')[1])
    except (IndexError, ValueError):
        txt = f"""Hello {WISH} {message.from_user.first_name} \n\n
        I am a file renamer bot. Please send any Telegram **Document or Video** and enter a new filename to rename it."""
        await message.reply_photo(
            photo=LAZY_PIC,
            caption=txt,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔺 Update Channel 🔺", url="https://t.me/LazyDeveloper")],
                [InlineKeyboardButton("🦋 Subscribe us 🦋", url="https://youtube.com/@LazyDeveloperr")],
                [InlineKeyboardButton("Support Group", url='https://t.me/LazyPrincessSupport'),
                 InlineKeyboardButton("Movie Channel", url='https://t.me/real_MoviesAdda2')],
                [InlineKeyboardButton("☕ Buy Me A Coffee ☕", url='https://p.paytm.me/xCTH/vo37hii9')]
            ])
        )
        return

    # Check if the user has already used the bot
    if old:
        try:
            await client.send_message(user_id, "Your friend is already using our bot.")
            await message.reply_photo(
                photo=LAZY_PIC,
                caption=txt,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔺 Update Channel 🔺", url="https://t.me/LazyDeveloper")],
                    [InlineKeyboardButton("🦋 Subscribe us 🦋", url="https://youtube.com/@LazyDeveloperr")],
                    [InlineKeyboardButton("Support Group", url='https://t.me/LazyPrincessSupport'),
                     InlineKeyboardButton("Movie Channel", url='https://t.me/real_MoviesAdda2')],
                    [InlineKeyboardButton("☕ Buy Me A Coffee ☕", url='https://p.paytm.me/xCTH/vo37hii9')]
                ])
            )
        except Exception as e:
            logging.error(f"Failed to send message to user {user_id}: {e}")
        return
    else:
        await client.send_message(user_id, "Congrats! You won 100MB upload limit.")
        _user_ = find_one(user_id)
        new_limit = _user_["uploadlimit"] + 104857600  # 100MB
        uploadlimit(user_id, new_limit)
        await message.reply_text(
            text=f"""
            Hello {WISH} {message.from_user.first_name} \n\n
            __I am a file renamer bot. Please send any Telegram **Document or Video** and enter a new filename to rename it.__
            """,
            reply_to_message_id=message.id,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔺 Update Channel 🔺", url="https://t.me/LazyDeveloper")],
                [InlineKeyboardButton("🦋 Subscribe us 🦋", url="https://youtube.com/@LazyDeveloperr")],
                [InlineKeyboardButton("Support Group", url='https://t.me/LazyPrincessSupport'),
                 InlineKeyboardButton("Movie Channel", url='https://t.me/real_MoviesAdda2')],
                [InlineKeyboardButton("☕ Buy Me A Coffee ☕", url='https://p.paytm.me/xCTH/vo37hii9')]
            ])
        )

# Function to handle file messages
@Client.on_message((filters.private & (filters.document | filters.audio | filters.video)) | filters.channel & (filters.document | filters.audio | filters.video))
async def send_doc(client, message):
    update_channel = CHANNEL
    user_id = message.from_user.id

    # Check if the user is subscribed to the update channel
    if update_channel:
        try:
            await client.get_chat_member(update_channel, user_id)
        except UserNotParticipant:
            _newus = find_one(user_id)
            user_plan = _newus["usertype"]
            await message.reply_text(
                "**__You are not subscribed to my channel__**",
                reply_to_message_id=message.id,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔺 Update Channel 🔺", url=f"https://t.me/{update_channel}")]])
            )
            await client.send_message(LOG_CHANNEL, f"🦋 #GangsterBaby_LOGS 🦋,\n\n**ID**: `{user_id}`\n**Name**: {message.from_user.first_name} {message.from_user.last_name}\n**User Plan**: {user_plan}")
            return

    try:
        bot_data = find_one(int(BOTID))
        prrename = bot_data['total_rename']
        prsize = bot_data['total_size']
        user_data = find_one(user_id)
    except Exception as e:
        logging.error(f"Error fetching data for user {user_id}: {e}")
        await message.reply_text("Use the About command first (/about).")
        return

    # Check for user data and handle expired plans
    try:
        used_date = user_data["date"]
        buy_date = user_data["prexdate"]
        daily = user_data["daily"]
        user_type = user_data["usertype"]
    except KeyError:
        await message.reply_text(
            text=f"Hello {message.from_user.first_name}, we are currently working on this issue. Please try renaming files from another account.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🦋 Contact LazyDeveloper 🦋", url='https://telegram.me/LazyDeveloper')],
                [InlineKeyboardButton("🔺 Watch Tutorial 🔺", url='https://youtube.com/@LazyDeveloperr')],
                [InlineKeyboardButton("🦋 Visit Channel", url='https://t.me/LazyDeveloper'),
                 InlineKeyboardButton("Support Group 🦋", url='https://t.me/LazyPrincessSupport')],
                [InlineKeyboardButton("☕ Buy Me A Coffee ☕", url='https://p.paytm.me/xCTH/vo37hii9')]
            ])
        )
        return

    # Time and Limit Calculation
    current_time = time.time()
    if user_type == "Free":
        LIMIT = 600
    else:
        LIMIT = 50
    expiry_time = used_date + LIMIT
    time_left = round(expiry_time - current_time)
    conversion = datetime.timedelta(seconds=time_left)
    left_time_str = str(conversion)

    if time_left > 0:
        await message.reply_text(
            f"```Sorry, flood control is active. Please wait for {left_time_str}```",
            reply_to_message_id=message.id
        )
    else:
        # Process the file
        media = await client.get_messages(message.chat.id, message.id)
        file = media.document or media.video or media.audio
        dc_id = FileId.decode(file.file_id).dc_id
        filename = file.file_name
        user_data = find_one(user_id)
        user_size = user_data["uploadlimit"]

        # Perform file size and limit checks
        if file.file_size > user_size:
            await message.reply_text(
                f"**Sorry, your upload limit of {humanbytes(user_size)} has been reached. Upgrade for more!**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("☕ Upgrade Plan ☕", url='https://t.me/LazyDeveloper')]])
            )
            return
        # Proceed with renaming and updating user data here as needed

    c_time = time.time()

    if user_type == "Free":
        LIMIT = 600
    else:
        LIMIT = 50
    then = used_date + LIMIT
    left = round(then - c_time)
    conversion = datetime.timedelta(seconds=left)
    ltime = str(conversion)
    if left > 0:
        await message.reply_text(f"```Sorry Dude I am not only for YOU \n Flood control is active so please wait for {ltime}```", reply_to_message_id=message.id)
    else:
        # Forward a single message
        media = await client.get_messages(message.chat.id, message.id)
        file = media.document or media.video or media.audio
        dcid = FileId.decode(file.file_id).dc_id
        filename = file.file_name
        value = 2147483648
        used_ = find_one(message.from_user.id)
        used = used_["used_limit"]
        limit = used_["uploadlimit"]
        expi = daily - int(time.mktime(time.strptime(str(date_.today()), '%Y-%m-%d')))
        if expi != 0:
            today = date_.today()
            pattern = '%Y-%m-%d'
            epcho = int(time.mktime(time.strptime(str(today), pattern)))
            daily_(message.from_user.id, epcho)
            used_limit(message.from_user.id, 0)
        remain = limit - used
        if remain < int(file.file_size):
            await message.reply_text(f"100% of daily {humanbytes(limit)} data quota exhausted.\n\n  File size detected {humanbytes(file.file_size)}\n  Used Daily Limit {humanbytes(used)}\n\nYou have only **{humanbytes(remain)}** left on your Account.\nIf U Want to Rename Large File Upgrade Your Plan ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Upgrade 💰💳", callback_data="upgrade")]]))
            return
        if value < file.file_size:
            
            if STRING:
                if buy_date == None:
                    await message.reply_text(f" You Can't Upload More Then {humanbytes(limit)} Used Daily Limit {humanbytes(used)} ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Upgrade 💰💳", callback_data="upgrade")]]))
                    return
                pre_check = check_expi(buy_date)
                if pre_check == True:
                    await message.reply_text(f"""__What do you want me to do with this file?__\n**File Name** :- {filename}\n**File Size** :- {humanize.naturalsize(file.file_size)}\n**Dc ID** :- {dcid}""", reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 Rename", callback_data="rename"), InlineKeyboardButton("✖️ Cancel", callback_data="cancel")]]))
                    total_rename(int(botid), prrename)
                    total_size(int(botid), prsize, file.file_size)
                else:
                    uploadlimit(message.from_user.id, 1288490188)
                    usertype(message.from_user.id, "Free")

                    await message.reply_text(f'Your Plan Expired On {buy_date}', quote=True)
                    return
            else:
                await message.reply_text("Can't upload files bigger than 2GB ")
                return
        else:
            if buy_date:
                pre_check = check_expi(buy_date)
                if pre_check == False:
                    uploadlimit(message.from_user.id, 1288490188)
                    usertype(message.from_user.id, "Free")

            filesize = humanize.naturalsize(file.file_size)
            fileid = file.file_id
            total_rename(int(botid), prrename)
            total_size(int(botid), prsize, file.file_size)
            await message.reply_text(f"""__What do you want me to do with this file?__\n**File Name** :- {filename}\n**File Size** :- {filesize}\n**Dc ID** :- {dcid}""", reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📝 Rename", callback_data="rename"),
                  InlineKeyboardButton("✖️ Cancel", callback_data="cancel")]]))
