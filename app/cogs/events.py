"""
Events Cog - Auto-Moderation Event Handlers
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventsCog(commands.Cog):
    """Event handlers for auto-moderation."""
    
    def __init__(self, bot):
        self.bot = bot
        self.user_message_history = defaultdict(list)  # Track message history for spam
        self.spam_threshold = 5  # 5 messages
        self.spam_timeframe = 5  # in 5 seconds
        
        # Anti-link patterns
        self.link_patterns = [
            'http://', 'https://', 'www.', '.com', '.net', '.org',
            'bit.ly', 'tinyurl', 'discord.gg', 'discord.com'
        ]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle message events for auto-moderation."""
        
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Ignore DMs
        if not message.guild:
            return
        
        # Check permissions before taking action
        if not message.guild.me.guild_permissions.manage_messages:
            return
        
        # Anti-spam detection
        await self.check_spam(message)
        
        # Anti-link detection
        await self.check_links(message)
        
        # Continue processing commands
        await self.bot.process_commands(message)
    
    async def check_spam(self, message: discord.Message):
        """Detect and handle spam messages."""
        user_id = message.author.id
        current_time = datetime.now()
        
        # Add message to history
        self.user_message_history[user_id].append(current_time)
        
        # Clean old messages (older than timeframe)
        self.user_message_history[user_id] = [
            msg_time for msg_time in self.user_message_history[user_id]
            if (current_time - msg_time).total_seconds() < self.spam_timeframe
        ]
        
        # Check if spam threshold exceeded
        if len(self.user_message_history[user_id]) > self.spam_threshold:
            try:
                await message.delete()
                logger.info(f"Deleted spam message from {message.author} in {message.guild}")
            except Exception as e:
                logger.debug(f"Could not delete spam message: {e}")
    
    async def check_links(self, message: discord.Message):
        """Detect and remove link messages from non-authorized roles."""
        
        # Check if user has permissions to post links
        if message.author.guild_permissions.manage_messages:
            return
        
        # Check for links in message
        has_link = any(pattern in message.content.lower() for pattern in self.link_patterns)
        
        if has_link:
            try:
                await message.delete()
                logger.info(f"Removed link message from {message.author} in {message.guild}")
            except Exception as e:
                logger.debug(f"Could not delete link message: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Welcome message when member joins."""
        logger.info(f"Member joined: {member.name} in {member.guild.name}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log when member leaves."""
        logger.info(f"Member left: {member.name} from {member.guild.name}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Handle edited messages for moderation."""
        
        if after.author.bot or not after.guild:
            return
        
        # Recheck edited message for violations
        if not after.guild.me.guild_permissions.manage_messages:
            return
        
        await self.check_spam(after)
        await self.check_links(after)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(EventsCog(bot))
