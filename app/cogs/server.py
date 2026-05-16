"""
Server Management Cog - Server Commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)


class ServerCog(commands.Cog):
    """Server management commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        user="User to kick",
        reason="Reason for kick"
    )
    async def kick(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
        """Kick a user from the server."""
        
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            await interaction.guild.kick(user, reason=reason)
            logger.info(f"Kicked {user} from {interaction.guild}: {reason}")
        except Exception as e:
            logger.error(f"Failed to kick {user}: {e}")
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="User to ban",
        reason="Reason for ban"
    )
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
        """Ban a user from the server."""
        
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            await interaction.guild.ban(user, reason=reason)
            logger.info(f"Banned {user} from {interaction.guild}: {reason}")
        except Exception as e:
            logger.error(f"Failed to ban {user}: {e}")
    
    @app_commands.command(name="clear", description="Clear messages")
    @app_commands.describe(amount="Number of messages to clear")
    async def clear(self, interaction: discord.Interaction, amount: int):
        """Clear messages from channel."""
        
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.manage_messages:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            if amount <= 0:
                logger.error("Invalid amount to clear")
                return
            
            deleted = await interaction.channel.purge(limit=min(amount, 100))
            logger.info(f"Cleared {len(deleted)} messages in {interaction.channel}")
        except Exception as e:
            logger.error(f"Failed to clear messages: {e}")
    
    @app_commands.command(name="setname", description="Set server name")
    @app_commands.describe(name="New server name")
    async def setname(self, interaction: discord.Interaction, name: str):
        """Change server name."""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            await interaction.guild.edit(name=name)
            logger.info(f"Changed server name to: {name}")
        except Exception as e:
            logger.error(f"Failed to change server name: {e}")
    
    @app_commands.command(name="createrole", description="Create a new role")
    @app_commands.describe(name="Role name", color="Role color (hex)")
    async def createrole(self, interaction: discord.Interaction, name: str, color: str = "#000000"):
        """Create a new role."""
        
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            color_int = int(color.replace("#", ""), 16)
            role_color = discord.Color(color_int)
            await interaction.guild.create_role(name=name, color=role_color)
            logger.info(f"Created role: {name}")
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
    
    @app_commands.command(name="assignrole", description="Assign role to user")
    @app_commands.describe(user="User to assign role", role="Role to assign")
    async def assignrole(self, interaction: discord.Interaction, user: discord.User, role: discord.Role):
        """Assign a role to a user."""
        
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            member = await interaction.guild.fetch_member(user.id)
            await member.add_roles(role)
            logger.info(f"Assigned role {role.name} to {user}")
        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
    
    @app_commands.command(name="removerole", description="Remove role from user")
    @app_commands.describe(user="User to remove role from", role="Role to remove")
    async def removerole(self, interaction: discord.Interaction, user: discord.User, role: discord.Role):
        """Remove a role from a user."""
        
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            member = await interaction.guild.fetch_member(user.id)
            await member.remove_roles(role)
            logger.info(f"Removed role {role.name} from {user}")
        except Exception as e:
            logger.error(f"Failed to remove role: {e}")
    
    @app_commands.command(name="createchannel", description="Create a new channel")
    @app_commands.describe(name="Channel name", channel_type="Channel type")
    async def createchannel(self, interaction: discord.Interaction, name: str, channel_type: str = "text"):
        """Create a new channel."""
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            if channel_type.lower() == "voice":
                await interaction.guild.create_voice_channel(name=name)
            else:
                await interaction.guild.create_text_channel(name=name)
            logger.info(f"Created {channel_type} channel: {name}")
        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
    
    @app_commands.command(name="deletechannel", description="Delete a channel")
    async def deletechannel(self, interaction: discord.Interaction):
        """Delete the current channel."""
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.defer()
            return
        
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.defer()
            return
        
        await interaction.response.defer()
        
        try:
            channel_name = interaction.channel.name
            await interaction.channel.delete()
            logger.info(f"Deleted channel: {channel_name}")
        except Exception as e:
            logger.error(f"Failed to delete channel: {e}")


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(ServerCog(bot))
