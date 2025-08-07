import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available commands and their usage")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 RankBot Help",
            description="A Discord bot for managing programming competitions with leaderboards!",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Admin Commands
        embed.add_field(
            name="⚙️ **Admin Commands**",
            value=(
                "`/setup` - Configure bot channels and roles\n"
                "`/post_problem` - Post a new problem with PDF\n"
                "`/post_cp_problem` - Post competitive programming problem with link\n"
                "`/score_solution` - Score a PDF solution (0-100)\n"
                "`/score_submission` - Score code submission (0-10 each category)\n"
                "`/review_queue` - View pending submissions\n"
                "`!sync_guild` - Sync slash commands to guild"
            ),
            inline=False
        )
        
        # User Commands
        embed.add_field(
            name="👤 **User Commands**",
            value=(
                "`/submit` - Submit a code solution\n"
                "`/submit_pdf` - Submit a PDF solution\n"
                "`/leaderboard` - View current rankings\n"
                "`/list_cp_problems` - List recent CP problems\n"
                "`/profile` - View your profile and stats\n"
                "`/help` - Show this help message"
            ),
            inline=False
        )
        
        # How to Submit
        embed.add_field(
            name="📝 **How to Submit Solutions**",
            value=(
                "**PDF Solutions:**\n"
                "• Use `/submit_pdf` with problem ID and PDF file\n"
                "• Or tag the bot with PDF attachment and problem ID\n\n"
                "**Code Solutions:**\n"
                "• Use `/submit` with language and your code\n"
                "• Supported languages: Python, Java, C++, etc."
            ),
            inline=False
        )
        
        # Scoring System
        embed.add_field(
            name="🏆 **Scoring System**",
            value=(
                "**PDF Solutions:** 0-100 points\n"
                "**Code Submissions:** 3 categories (0-10 each)\n"
                "• Completeness (0-10)\n"
                "• Elegance (0-10)\n"
                "• Speed (0-10)\n"
                "Total: 0-30 points per submission"
            ),
            inline=False
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
