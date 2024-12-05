import os 
from pyrogram import Client, filters
from helper.database import botdata, find_one, total_user
from helper.progress import humanbytes

# Securely retrieve the bot token from environment variables
token = os.environ.get('TOKEN', '')
if not token:
    raise ValueError("Bot token is missing. Please set the TOKEN environment variable.")
    
botid = token.split(':')[0]

@Client.on_message(filters.private & filters.command(["about"]))
async def start(client, message):
    """
    Handles the /about command and sends information about the bot, its creator, and its usage.
    
    Args:
        client (Client): The Pyrogram client instance.
        message (Message): The incoming message object.
    """
    try:
        # Fetch bot data from the database
        botdata(int(botid))
        data = find_one(int(botid))
        
        if not data:
            raise ValueError("Data for the bot could not be found.")
        
        total_rename = data.get("total_rename", 0)
        total_size = data.get("total_size", 0)
        
        # Format the response message
        response_message = (
            f"Original BOT: <a href='http://t.me/Thumbnail999bot'>Gangster Baby</a>\n"
            f"Creator: <a href='https://t.me/Agent_ghost999'>🦋LazyDeveloper🦋</a>\n"
            f"Language: Python 3\n"
            f"Library: Pyrogram 2.0\n"
            f"Server: KOYEB\n"
            f"Total Renamed Files: {total_rename}\n"
            f"Total Size Renamed: {humanbytes(int(total_size))}\n\n"
            f"Thank you <a href='https://t.me/mRiderDM'>**LazyDeveloperr**</a> for your hard work.\n\n"
            f"❤️ We love you <a href='https://t.me/mRiderDM'>**LazyDeveloper**</a> ❤️"
        )
        
        # Send the message with error handling
        await message.reply_text(response_message, quote=True)
    
    except KeyError as ke:
        await message.reply_text(f"Error: Missing data key - {ke}. Please try again later.")
    except ValueError as ve:
        await message.reply_text(f"Error: {ve}")
    except Exception as e:
        # Log the exception for better debugging (consider adding logging to a file)
        print(f"Unexpected error: {e}")
        await message.reply_text(f"An unexpected error occurred: {e}")
