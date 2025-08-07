import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from database import Database
from typing import Optional  # add this import

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="profile", description="View your or another user's profile and stats")
    @app_commands.describe(user="User to view profile for (optional, defaults to you)")
    async def profile(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target_user = user if user is not None else interaction.user
        
        # Get user stats for both math and CP
        math_stats = self.db.get_math_user_stats(target_user.id)
        cp_stats = self.db.get_cp_user_stats(target_user.id)
        
        if not math_stats and not cp_stats:
            if target_user == interaction.user:
                await interaction.response.send_message("You haven't submitted any solutions yet! Use `/submit` to get started.", ephemeral=True)
            else:
                await interaction.response.send_message(f"{target_user.display_name} hasn't submitted any solutions yet.", ephemeral=True)
            return
        
        # Create profile embed
        embed = discord.Embed(
            title=f"📊 {target_user.display_name}'s Profile",
            color=0x0099ff,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)
        
        # Math stats
        if math_stats:
            math_score, math_solutions, math_avg, math_rank = math_stats
            embed.add_field(name="🔢 Math Score", value=str(math_score), inline=True)
            embed.add_field(name="📊 Math Rank", value=f"#{math_rank}", inline=True)
            embed.add_field(name="📈 Math Avg", value=f"{math_avg:.1f}", inline=True)
            embed.add_field(name="� Math Solutions", value=str(math_solutions), inline=True)
        else:
            embed.add_field(name="� Math Score", value="0", inline=True)
            embed.add_field(name="📊 Math Rank", value="N/A", inline=True)
            embed.add_field(name="� Math Avg", value="N/A", inline=True)
            embed.add_field(name="📄 Math Solutions", value="0", inline=True)
        
        # CP stats  
        if cp_stats:
            cp_score, cp_submissions, cp_avg, cp_rank = cp_stats
            embed.add_field(name="💻 CP Score", value=str(cp_score), inline=True)
            embed.add_field(name="📊 CP Rank", value=f"#{cp_rank}", inline=True)
            embed.add_field(name="📈 CP Avg", value=f"{cp_avg:.1f}", inline=True)
            embed.add_field(name="💻 CP Submissions", value=str(cp_submissions), inline=True)
        else:
            embed.add_field(name="💻 CP Score", value="0", inline=True)
            embed.add_field(name="� CP Rank", value="N/A", inline=True)
            embed.add_field(name="📈 CP Avg", value="N/A", inline=True)
            embed.add_field(name="� CP Submissions", value="0", inline=True)
        
        embed.set_footer(text=f"Member since {target_user.created_at.strftime('%B %Y')}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="history", description="View your submission history")
    @app_commands.describe(limit="Number of submissions to show (default: 10, max: 20)")
    async def submission_history(self, interaction: discord.Interaction, limit: int = 10):
        if limit > 20:
            limit = 20
        elif limit < 1:
            limit = 1
        
        # Get math solutions
        math_cursor = self.db.conn.cursor()
        math_cursor.execute('''
            SELECT 'math' as type, score, submitted_at, problem_id
            FROM math_solutions 
            WHERE user_id = ?
            ORDER BY submitted_at DESC
            LIMIT ?
        ''', (interaction.user.id, limit))
        math_history = math_cursor.fetchall()
        
        # Get CP submissions
        cp_cursor = self.db.conn.cursor()
        cp_cursor.execute('''
            SELECT 'cp' as type, 
                   (COALESCE(completeness_score, 0) + COALESCE(elegance_score, 0) + COALESCE(speed_score, 0)) as total_score,
                   submitted_at, language
            FROM cp_submissions 
            WHERE user_id = ?
            ORDER BY submitted_at DESC
            LIMIT ?
        ''', (interaction.user.id, limit))
        cp_history = cp_cursor.fetchall()
        
        # Combine and sort by date
        all_history = []
        for item in math_history:
            all_history.append(('math', item[1], item[2], item[3]))  # type, score, date, extra_info
        for item in cp_history:
            all_history.append(('cp', item[1], item[2], item[3]))  # type, score, date, extra_info
        
        # Sort by date (newest first)
        all_history.sort(key=lambda x: x[2], reverse=True)
        all_history = all_history[:limit]
        
        if not all_history:
            await interaction.response.send_message("You haven't submitted any solutions yet! Use `/submit` to get started.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📚 {interaction.user.display_name}'s Submission History",
            color=0x9932cc,
            timestamp=datetime.now(timezone.utc)
        )
        
        for i, submission in enumerate(all_history, 1):
            submission_type, score, submitted_at, details = submission
            
            status_emoji = "✅" if score is not None else "⏳"
            type_emoji = "💻" if submission_type == "cp" else "📄"
            
            if submission_type == "cp":
                language = details
                score_display = f"{score}/30" if score is not None else "Pending"
                embed.add_field(
                    name=f"{status_emoji} {type_emoji} CP Submission #{i}",
                    value=f"**Language:** {language}\n**Score:** {score_display}\n**Date:** {submitted_at.split(' ')[0]}",
                    inline=True
                )
            else:
                problem_id = details
                score_display = f"{score}/100" if score is not None else "Pending"
                embed.add_field(
                    name=f"{status_emoji} {type_emoji} Math Solution #{i}",
                    value=f"**Problem ID:** {problem_id}\n**Score:** {score_display}\n**Date:** {submitted_at.split(' ')[0]}",
                    inline=True
                )
        
        embed.set_footer(text="✅ = Reviewed, ⏳ = Pending Review")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
