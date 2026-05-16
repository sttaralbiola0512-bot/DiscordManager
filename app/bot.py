"""
Discord Bot Client Setup
"""

import discord
from discord.ext import commands
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Setup bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True
intents.messages = True
intents.dm_messages = True

# Create bot instance
bot = commands.Bot(
    command_prefix="/",
    intents=intents,
    help_command=None,
    sync_commands=True,
    case_insensitive=True
)


@bot.event
async def on_ready():
    """
    Called when bot is ready and connected to Discord.
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"Bot logged in as: {bot.user}")
    logger.info(f"Bot ID: {bot.user.id}")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")
    logger.info(f"{'='*50}\n")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for rule violations"
        ),
        status=discord.Status.online
    )
    
    # Sync commands with Discord
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s) with Discord")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


@bot.event
async def on_command_error(ctx, error):
    """
    Handle command errors silently (no unnecessary messages).
    """
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        return
    elif isinstance(error, commands.BotMissingPermissions):
        return
    else:
        logger.error(f"Command error: {error}")


@bot.event
async def on_error(event, *args, **kwargs):
    """
    Handle general errors.
    """
    logger.error(f"Error in {event}: {*args, **kwargs}")


async def load_cogs():
    """
    Load all cogs from the cogs directory.
    """
    cogs_dir = Path(__file__).parent / "cogs"
    
    if not cogs_dir.exists():
        logger.warning(f"Cogs directory not found: {cogs_dir}")
        return
    
    for cog_file in cogs_dir.glob("*.py"):
        if cog_file.name.startswith("_"):
            continue
        
        cog_name = f"app.cogs.{cog_file.stem}"
        try:
            await bot.load_extension(cog_name)
            logger.info(f"Loaded cog: {cog_name}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog_name}: {e}")


# Load cogs when bot starts
@bot.event
async def setup_hook():
    """
    Called before bot connects to Discord.
    Used to load all cogs.
    """
    await load_cogs()
