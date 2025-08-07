import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from database import Database
from utils.config import CONFIG, is_moderator_interaction

class ScoringCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="score_math_solution", description="Score a mathematics solution submission")
    @app_commands.describe(
        solution_id="ID of the solution to score",
        score="Score from 0 to 100"
    )
    async def score_math_solution(self, interaction: discord.Interaction, solution_id: int, score: int):
        if not is_moderator_interaction(interaction):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        if not (0 <= score <= 100):
            await interaction.response.send_message("Score must be between 0 and 100.", ephemeral=True)
            return
        
        self.db.update_math_solution_score(solution_id, score)
        await interaction.response.send_message(f"✅ Math solution {solution_id} scored with {score} points!")
        await self.update_math_leaderboard()

    @app_commands.command(name="score_cp_submission", description="Score a competitive programming submission")
    @app_commands.describe(
        submission_id="ID of the submission to score",
        completeness="Completeness score (0-10)",
        elegance="Elegance score (0-10)",
        speed="Speed score (0-10)"
    )
    async def score_cp_submission(self, interaction: discord.Interaction, submission_id: int, completeness: int, elegance: int, speed: int):
        if not is_moderator_interaction(interaction):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        if not all(0 <= score <= 10 for score in [completeness, elegance, speed]):
            await interaction.response.send_message("All scores must be between 0 and 10.", ephemeral=True)
            return
        
        self.db.update_cp_submission_scores(submission_id, completeness, elegance, speed)
        total = completeness + elegance + speed
        await interaction.response.send_message(
            f"✅ CP submission {submission_id} scored!\n"
            f"Completeness: {completeness}/10\n"
            f"Elegance: {elegance}/10\n"
            f"Speed: {speed}/10\n"
            f"Total: {total}/30"
        )
        await self.update_cp_leaderboard()

    @app_commands.command(name="review_queue", description="Show pending submissions awaiting review")
    async def review_queue(self, interaction: discord.Interaction):
        if not is_moderator_interaction(interaction):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        math_solutions = self.db.get_unreviewed_math_solutions()
        cp_submissions = self.db.get_unreviewed_cp_submissions()
        
        embed = discord.Embed(
            title="📋 Review Queue",
            color=0xff6b6b,
            timestamp=datetime.now(timezone.utc)
        )
        
        if math_solutions:
            solution_text = ""
            for sol_id, user_id, pdf_url, title, submitted_at in math_solutions[:5]:
                user = self.bot.get_user(user_id)
                username = user.display_name if user else f"User {user_id}"
                solution_text += f"ID {sol_id}: {username} - {title}\n"
            embed.add_field(name="🔢 Unreviewed Math Solutions", value=solution_text or "None", inline=False)
        
        if cp_submissions:
            submission_text = ""
            for sub_id, user_id, code, language, file_url, submitted_at in cp_submissions[:5]:
                user = self.bot.get_user(user_id)
                username = user.display_name if user else f"User {user_id}"
                submission_text += f"ID {sub_id}: {username} ({language})\n"
            embed.add_field(name="💻 Unreviewed CP Submissions", value=submission_text or "None", inline=False)
        
        if not math_solutions and not cp_submissions:
            embed.description = "No pending reviews! 🎉"
        
        await interaction.response.send_message(embed=embed)

    async def update_math_leaderboard(self):
        if CONFIG['LEADERBOARD_CHANNEL_ID']:
            channel = self.bot.get_channel(CONFIG['LEADERBOARD_CHANNEL_ID'])
            if channel and isinstance(channel, discord.TextChannel):
                leaderboard = self.db.get_math_leaderboard()
                
                if leaderboard:
                    embed = discord.Embed(
                        title="🔢 Mathematics Leaderboard",
                        color=0x00ff00,
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
                    
                    embed.set_footer(text="Math leaderboard updates automatically when solutions are scored")
                    
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user and message.embeds:
                            title = message.embeds[0].title
                            if title and "Mathematics Leaderboard" in title:
                                await message.edit(embed=embed)
                                return
                    
                    await channel.send(embed=embed)

    async def update_cp_leaderboard(self):
        if CONFIG['LEADERBOARD_CHANNEL_ID']:
            channel = self.bot.get_channel(CONFIG['LEADERBOARD_CHANNEL_ID'])
            if channel and isinstance(channel, discord.TextChannel):
                leaderboard = self.db.get_cp_leaderboard()
                
                if leaderboard:
                    embed = discord.Embed(
                        title="💻 Competitive Programming Leaderboard",
                        color=0x0099ff,
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
                    
                    embed.set_footer(text="CP leaderboard updates automatically when submissions are scored")
                    
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user and message.embeds:
                            title = message.embeds[0].title
                            if title and "Competitive Programming Leaderboard" in title:
                                await message.edit(embed=embed)
                                return
                    
                    await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ScoringCog(bot))
