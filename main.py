#!/usr/bin/env python3
"""
Discord Manager Bot - Main Entry Point
Complete moderation bot with auto-moderation, anti-spam, warning system, and server management.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from threading import Thread

# Load environment variables from .env file
load_dotenv()

# Get tokens from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Configure logging
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate required environment variables
if not DISCORD_BOT_TOKEN:
    logger.error("ERROR: DISCORD_BOT_TOKEN not found in environment variables!")
    logger.error("Please set DISCORD_BOT_TOKEN in .env file")
    exit(1)

if not GROQ_API_KEY:
    logger.error("ERROR: GROQ_API_KEY not found in environment variables!")
    logger.error("Please set GROQ_API_KEY in .env file")
    exit(1)

# Import after loading environment variables
from app.bot import bot
from app.server.flask_app import create_app


def run_flask():
    """
    Run Flask server in background thread for 24/7 uptime.
    """
    try:
        app = create_app()
        logger.info(f"Starting Flask server on {FLASK_HOST}:{FLASK_PORT}")
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")


async def main():
    """
    Main async function to start the bot and Flask server.
    """
    try:
        # Start Flask server in background thread
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Flask background server started")
        
        # Wait a moment for Flask to start
        await asyncio.sleep(1)
        
        # Start Discord bot
        logger.info("Starting Discord bot...")
        await bot.start(DISCORD_BOT_TOKEN)
        
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("Bot shutdown")


if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Discord Manager Bot Starting")
    logger.info("="*50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
