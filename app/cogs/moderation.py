"""
Moderation Cog - Warning System & Moderation Commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Database path for warnings
DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
WARNINGS_DB = DB_DIR / "warnings.json"


class ModerationCog(commands.Cog):
    """Moderation cog for warnings and user management."""
    
    def __init__(self, bot):
        self.bot = bot
        self.load_warnings()
    
    def load_warnings(self):
        """Load warnings from database."""
        try:
            if WARNINGS_DB.exists():
                with open(WARNINGS_DB, 'r') as f:
                    self.warnings = json.load(f)
            else:
                self.warnings = {}
        except Exception as e:
            logger.error(f"Error loading warnings: {e}")
            self.warnings = {}
    
    def save_warnings(self):
        """Save warnings to database."""
        try:
            with open(WARNINGS_DB, 'w') as f:
                json.dump(self.warnings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving warnings: {e}")
    
    def clean_expired_warnings(self, user_id: str, guild_id: str):
        """Remove warnings older than 7 days."""
        key = f"{guild_id}_{user_id}"
        if key not in self.warnings:
            return
        
        current_time = datetime.now()
        self.warnings[key] = [
            w for w in self.warnings[key]
            if datetime.fromisoformat(w['timestamp']) > current_time - timedelta(days=7)
        ]
        
        if not self.warnings[key]:
            del self.warnings[key]
        
        self.save_warnings()
    
    async def send_dm(self, user: discord.User, message: str):
        """Send DM to user without verbose output."""
        try:
            await user.send(message)
        except discord.Forbidden:
            logger.debug(f"Could not send DM to {user} - DMs disabled")
        except Exception as e:
            logger.debug(f"Error sending DM to {user}: {e}")
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(
        user="User to warn",
        reason="Reason for warning"
    )
    async def warn(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
        """Warn a user. Max 3 warnings before auto-kick."""
        
        # Check permissions
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        key = f"{guild_id}_{user_id}"
        
        # Clean expired warnings
        self.clean_expired_warnings(user_id, guild_id)
        
        # Add warning
        if key not in self.warnings:
            self.warnings[key] = []
        
        warning = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "moderator": interaction.user.name
        }
        
        self.warnings[key].append(warning)
        self.save_warnings()
        
        warning_count = len(self.warnings[key])
        
        # Send DM to user
        dm_message = f"You have been warned in **{interaction.guild.name}**\n"
        dm_message += f"Reason: {reason}\n"
        dm_message += f"Warnings: {warning_count}/3"
        
        if warning_count >= 3:
            dm_message += "\n\n⚠️ You have reached the maximum warnings and have been kicked from the server."
            await self.send_dm(user, dm_message)
            
            # Kick user
            try:
                await interaction.guild.kick(user, reason=f"Reached 3 warnings: {reason}")
                logger.info(f"Kicked {user} from {interaction.guild} for reaching 3 warnings")
            except Exception as e:
                logger.error(f"Failed to kick {user}: {e}")
        else:
            await self.send_dm(user, dm_message)
    
    @app_commands.command(name="warnings", description="View user's warnings")
    @app_commands.describe(user="User to check")
    async def warnings(self, interaction: discord.Interaction, user: discord.User):
        """View warnings for a user."""
        
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.defer()
            return
        
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        key = f"{guild_id}_{user_id}"
        
        # Clean expired warnings
        self.clean_expired_warnings(user_id, guild_id)
        
        await interaction.response.defer()
        
        if key not in self.warnings or not self.warnings[key]:
            logger.info(f"No warnings for {user} in {interaction.guild}")
            return
        
        logger.info(f"Viewed {len(self.warnings[key])} warnings for {user}")
    
    @app_commands.command(name="clearwarnings", description="Clear all warnings for a user")
    @app_commands.describe(user="User to clear warnings for")
    async def clearwarnings(self, interaction: discord.Interaction, user: discord.User):
        """Clear all warnings for a user."""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.defer()
            return
        
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        key = f"{guild_id}_{user_id}"
        
        await interaction.response.defer()
        
        if key in self.warnings:
            del self.warnings[key]
            self.save_warnings()
            logger.info(f"Cleared all warnings for {user}")


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(ModerationCog(bot))
