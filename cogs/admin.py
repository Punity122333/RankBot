import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.config import CONFIG, save_config, is_moderator_interaction

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Configure the bot channels and roles")
    @app_commands.describe(
        problem_channel="Channel where problems will be posted",
        moderator_channel="Channel where submissions will be reviewed",
        leaderboard_channel="Channel where the leaderboard will be displayed",
        moderator_role="Role that can moderate submissions (optional)"
    )
    async def setup_channels(
        self,
        interaction: discord.Interaction,
        problem_channel: discord.TextChannel,
        moderator_channel: discord.TextChannel,
        leaderboard_channel: discord.TextChannel,
        moderator_role: Optional[discord.Role] = None
    ):
        if not is_moderator_interaction(interaction):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        # Defer the response to prevent timeout
        await interaction.response.defer()
        
        CONFIG['PROBLEM_CHANNEL_ID'] = problem_channel.id
        CONFIG['MODERATOR_CHANNEL_ID'] = moderator_channel.id
        CONFIG['LEADERBOARD_CHANNEL_ID'] = leaderboard_channel.id
        if moderator_role:
            CONFIG['MODERATOR_ROLE_ID'] = moderator_role.id
        
        save_config()
        await interaction.followup.send(
            f"✅ Setup complete!\n"
            f"Problem Channel: {problem_channel.mention}\n"
            f"Moderator Channel: {moderator_channel.mention}\n"
            f"Leaderboard Channel: {leaderboard_channel.mention}"
            + (f"\nModerator Role: {moderator_role.mention}" if moderator_role else "")
        )

    @commands.command(name="sync_guild")
    async def sync_guild(self, ctx):
        if not ctx.guild:
            await ctx.send("This command must be used in a server.")
            return
        
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need administrator permissions to use this command.")
            return
        
        try:
            # Check bot permissions first
            if self.bot.user:
                bot_member = ctx.guild.get_member(self.bot.user.id)
                if bot_member:
                    await ctx.send(f"Bot permissions: {bot_member.guild_permissions.value}")
            
            # Check available commands
            commands = self.bot.tree.get_commands()
            await ctx.send(f"Available commands to sync: {len(commands)}")
            
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ Synced {len(synced)} commands to this guild!")
            
            # List what was synced
            if synced:
                cmd_names = [cmd.name for cmd in synced]
                await ctx.send(f"Synced commands: {', '.join(cmd_names)}")
            else:
                await ctx.send("⚠️ No commands were synced. This usually means missing `applications.commands` scope!")
                
        except Exception as e:
            await ctx.send(f"❌ Failed to sync: {e}")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
