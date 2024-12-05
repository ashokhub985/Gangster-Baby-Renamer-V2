import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from helper.database import getid, delete

# Set up logging for better error tracking and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ADMIN = int(os.environ.get("ADMIN", ""))

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if message.reply_to_message:
        try:
            ms = await message.reply_text("Fetching user IDs from database... Please wait.")
            ids = getid()
            if not ids:
                await ms.edit("No user IDs found in the database.")
                return

            tot = len(ids)
            success = 0
            failed = 0
            await ms.edit(f"Starting broadcast... \nSending message to {tot} users.")
            
            async def send_message(user_id):
                nonlocal success, failed
                try:
                    await message.reply_to_message.copy(user_id)
                    success += 1
                except FloodWait as e:
                    logging.warning(f"Rate limit hit for user {user_id}. Waiting for {e.x} seconds...")
                    await asyncio.sleep(e.x)
                    await send_message(user_id)  # Retry sending after the delay
                except Exception as e:
                    failed += 1
                    delete({"_id": user_id})
                    logging.error(f"Failed to send to user {user_id}: {e}")
        
            # Use asyncio.gather to run the message sending concurrently
            tasks = [send_message(user_id) for user_id in ids]
            await asyncio.gather(*tasks)

            # Update final status after broadcast completion
            await ms.edit(f"Broadcast complete!\nMessage sent to {success} user(s). {failed} user(s) failed.\nTotal - {tot}")
            logging.info(f"Broadcast complete: {success} sent, {failed} failed.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            await message.reply_text(f"An unexpected error occurred: {e}")
