import os 
from pyrogram import Client, filters
from helper.database import botdata, find_one, total_user
from helper.progress import humanbytes

token = os.environ.get('TOKEN', '')
botid = token.split(':')[0]

@Client.on_message(filters.private & filters.command(["about"]))
async def start(client, message):
    try:
        botdata(int(botid))
        data = find_one(int(botid))
        total_rename = data["total_rename"]
        total_size = data["total_size"]
        
        response_message = (
            f"Origional BOT :- <a href='https://t.me/GangsterBaby_renamer_BOT'>Gangster Baby</a>\n"
            f"Creater :- <a href='https://t.me/LazyDeveloper'>🦋LazyDeveloper🦋</a>\n"
            f"Language :- Python3\n"
            f"Library :- Pyrogram 2.0\n"
            f"Server :- KOYEB\n"
            f"Total Renamed File :- {total_rename}\n"
            f"Total Size Renamed :- {humanbytes(int(total_size))}\n\n"
            f"Thank you **<a href='https://t.me/mRiderDM'>LazyDeveloperr</a>** for your hard work \n\n"
            f"❤️ we love you <a href='https://t.me/mRiderDM'>**LazyDeveloper**</a> ❤️"
        )
        
        await message.reply_text(response_message, quote=True)
    except KeyError:
        await message.reply_text("Error: Unable to retrieve data. Please try again later.")
    except Exception as e:
        await message.reply_text(f"An unexpected error occurred: {e}")
