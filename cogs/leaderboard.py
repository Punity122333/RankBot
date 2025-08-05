import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from database import Database

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="leaderboard", description="Show the current leaderboard")
    async def show_leaderboard(self, interaction: discord.Interaction):
        leaderboard = self.db.get_leaderboard()
        
        if not leaderboard:
            await interaction.response.send_message("No scores available yet!")
            return
        
        embed = discord.Embed(
            title="🏆 Leaderboard",
            color=0xffd700,
            timestamp=datetime.now(timezone.utc)
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, score) in enumerate(leaderboard):
            user = self.bot.get_user(user_id)
            username = user.display_name if user else f"User {user_id}"
            medal = medals[i] if i < 3 else f"{i+1}."
            embed.add_field(
                name=f"{medal} {username}",
                value=f"{score} points",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
