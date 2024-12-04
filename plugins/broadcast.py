import os
from pyrogram.errors import FloodWait
import asyncio
from pyrogram import Client, filters
from helper.database import getid, delete
import time

ADMIN = int(os.environ.get("ADMIN", 1484670284)

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if message.reply_to_message:
        ms = await message.reply_text("Getting all IDs from database... Please wait.")
        ids = getid()
        tot = len(ids)
        success = 0
        failed = 0
        await ms.edit(f"Starting broadcast... \nSending message to {tot} users.")
        
        for id in ids:
            try:
                await message.reply_to_message.copy(id)
                success += 1
            except FloodWait as e:
                await ms.edit(f"Rate limit hit. Waiting for {e.x} seconds...")
                await asyncio.sleep(e.x)
            except Exception as e:
                failed += 1
                delete({"_id": id})
                print(f"Failed to send to {id}: {e}")
                pass

            try:
                await ms.edit(f"Message sent to {success} chat(s). {failed} chat(s) failed on receiving message. \nTotal - {tot}")
            except Exception as e:
                print(f"Error while updating status: {e}")
