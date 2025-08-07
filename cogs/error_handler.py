import discord
from discord.ext import commands
import traceback
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Handle slash command errors globally"""
        
        # Log the error
        logger.error(f"Command {interaction.command.name if interaction.command else 'Unknown'} failed: {error}")
        logger.error(f"User: {interaction.user} (ID: {interaction.user.id})")
        logger.error(f"Guild: {interaction.guild.name if interaction.guild else 'DM'} (ID: {interaction.guild.id if interaction.guild else 'N/A'})")
        logger.error(f"Channel: {interaction.channel} (ID: {interaction.channel.id if interaction.channel else 'N/A'})")
        logger.error(f"Full traceback: {traceback.format_exception(type(error), error, error.__traceback__)}")
        
        # User-friendly error messages
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await self._send_error_message(interaction, f"⏰ Command on cooldown. Try again in {error.retry_after:.1f} seconds.")
        elif isinstance(error, discord.app_commands.MissingPermissions):
            await self._send_error_message(interaction, "❌ You don't have permission to use this command.")
        elif isinstance(error, discord.app_commands.BotMissingPermissions):
            await self._send_error_message(interaction, "❌ I don't have the required permissions to execute this command.")
        elif isinstance(error, discord.HTTPException):
            await self._send_error_message(interaction, "❌ Network error occurred. Please try again.")
        else:
            await self._send_error_message(interaction, "❌ An unexpected error occurred. Please try again.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Handle prefix command errors"""
        
        logger.error(f"Prefix command {ctx.command} failed: {error}")
        logger.error(f"User: {ctx.author} (ID: {ctx.author.id})")
        logger.error(f"Guild: {ctx.guild.name if ctx.guild else 'DM'}")
        logger.error(f"Full traceback: {traceback.format_exception(type(error), error, error.__traceback__)}")
        
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.", delete_after=10)
        else:
            await ctx.send("❌ An error occurred while executing the command.", delete_after=10)

    async def _send_error_message(self, interaction: discord.Interaction, message: str):
        """Send error message to user"""
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=True)
            else:
                await interaction.followup.send(message, ephemeral=True)
        except:
            pass  # If we can't send the message, just log it

async def setup(bot):
    await bot.add_cog(ErrorHandlerCog(bot))
