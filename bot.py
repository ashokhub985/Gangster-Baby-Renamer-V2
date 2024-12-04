import asyncio
import os
import logging
from pyrogram import Client, idle, compose
from plugins.cb_data import app as Client2

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.environ.get("TOKEN", "7779296728:AAFFJu5Om-Nv7PGmwniWUTG14P4BSQS8K04")
API_ID = int(os.environ.get("API_ID", "22687964"))
API_HASH = os.environ.get("API_HASH", "bdce6f5214b673c8e8295403e250e383")
STRING = os.environ.get("STRING", "")

# Validate required environment variables
if not TOKEN or not API_ID or not API_HASH:
    logger.error("TOKEN, API_ID, and API_HASH must be set.")
    exit(1)

# Create clients
bot = Client(
    "Renamer",
    bot_token=TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root='plugins')
)

if STRING:
    # Start multiple clients if STRING is provided
    apps = [Client2, bot]

    async def start_clients():
        try:
            for app in apps:
                await app.start()
                logger.info(f"{app} started successfully.")
            
            await idle()
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        
        finally:
            for app in apps:
                await app.stop()
                logger.info(f"{app} stopped successfully.")

    asyncio.run(start_clients())
else:
    # Run the single bot instance
    try:
        bot.run()
        logger.info("Bot is running.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    app.run()  # Example for Flask

