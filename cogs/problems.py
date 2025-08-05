import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from database import Database
from utils.config import CONFIG, is_moderator_interaction

class ProblemsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="post_problem", description="Post a new problem with PDF attachment")
    @app_commands.describe(
        title="Title of the problem",
        description="Description of the problem (optional)",
        pdf_file="PDF file containing the problem"
    )
    async def post_problem(
        self,
        interaction: discord.Interaction,
        title: str,
        pdf_file: discord.Attachment,
        description: str = ""
    ):
        if not is_moderator_interaction(interaction):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        if not pdf_file.filename.endswith('.pdf'):
            await interaction.response.send_message("Please attach a PDF file.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        problem_id = self.db.add_problem(title, pdf_file.url, interaction.user.id)
        
        if CONFIG['PROBLEM_CHANNEL_ID']:
            channel = self.bot.get_channel(CONFIG['PROBLEM_CHANNEL_ID'])
            if channel and isinstance(channel, discord.TextChannel):
                embed = discord.Embed(
                    title=f"📝 New Problem: {title}",
                    description=description,
                    color=0x00ff00,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(name="Problem ID", value=str(problem_id), inline=True)
                embed.add_field(name="Posted by", value=interaction.user.mention, inline=True)
                embed.set_footer(text="Tag the bot with your solution PDF to submit!")
                
                await channel.send(embed=embed, file=await pdf_file.to_file())
        
        await interaction.followup.send(f"✅ Problem '{title}' posted successfully! ID: {problem_id}")

    @app_commands.command(name="post_cp_problem", description="Post a competitive programming problem from external site")
    @app_commands.describe(
        title="Title of the problem",
        problem_url="URL to the problem (Codeforces, AtCoder, HackerRank, etc.)",
        platform="Platform name (e.g., Codeforces, AtCoder, HackerRank)",
        difficulty="Difficulty rating or level (optional)",
        description="Additional description or notes (optional)"
    )
    async def post_cp_problem(
        self,
        interaction: discord.Interaction,
        title: str,
        problem_url: str,
        platform: str,
        difficulty: str = "",
        description: str = ""
    ):
        if not is_moderator_interaction(interaction):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        # Defer the response to prevent timeout
        await interaction.response.defer()

        # Validate URL format
        if not (problem_url.startswith('http://') or problem_url.startswith('https://')):
            await interaction.followup.send("Please provide a valid URL starting with http:// or https://", ephemeral=True)
            return

        # Store the competitive programming problem in database
        problem_id = self.db.add_cp_problem(title, problem_url, platform, difficulty, interaction.user.id)

        if CONFIG['PROBLEM_CHANNEL_ID']:
            channel = self.bot.get_channel(CONFIG['PROBLEM_CHANNEL_ID'])
            if channel and isinstance(channel, discord.TextChannel):
                # Create platform-specific embed color
                platform_colors = {
                    'codeforces': 0x1f8dd6,
                    'atcoder': 0x000000,
                    'hackerrank': 0x00d471,
                    'leetcode': 0xffa500,
                    'codechef': 0x5b4638,
                    'topcoder': 0x29a8e0,
                    'spoj': 0x267326
                }
                
                platform_lower = platform.lower()
                embed_color = platform_colors.get(platform_lower, 0x0099ff)
                
                embed = discord.Embed(
                    title=f"🏆 New CP Problem: {title}",
                    description=description if description else f"Solve this problem on {platform}!",
                    color=embed_color,
                    timestamp=datetime.now(timezone.utc),
                    url=problem_url
                )
                
                embed.add_field(name="Problem ID", value=str(problem_id), inline=True)
                embed.add_field(name="Platform", value=platform, inline=True)
                if difficulty:
                    embed.add_field(name="Difficulty", value=difficulty, inline=True)
                embed.add_field(name="Posted by", value=interaction.user.mention, inline=False)
                embed.add_field(name="🔗 Problem Link", value=f"[Click here to view problem]({problem_url})", inline=False)
                embed.set_footer(text="Submit your solutions using /submit or /submit_pdf!")
                
                await channel.send(embed=embed)

        await interaction.followup.send(f"✅ CP Problem '{title}' from {platform} posted successfully! ID: {problem_id}")

    @app_commands.command(name="list_cp_problems", description="List recent competitive programming problems")
    @app_commands.describe(limit="Number of problems to show (default: 5, max: 10)")
    async def list_cp_problems(self, interaction: discord.Interaction, limit: int = 5):
        if limit > 10:
            limit = 10
        elif limit < 1:
            limit = 1
            
        problems = self.db.get_cp_problems(limit)
        
        if not problems:
            await interaction.response.send_message("No competitive programming problems posted yet.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🏆 Recent Competitive Programming Problems",
            color=0x0099ff,
            timestamp=datetime.now(timezone.utc)
        )
        
        for problem in problems:
            problem_id, title, problem_url, platform, difficulty, posted_by, posted_at = problem
            user = self.bot.get_user(posted_by)
            poster_name = user.display_name if user else f"User {posted_by}"
            
            difficulty_text = f" ({difficulty})" if difficulty else ""
            embed.add_field(
                name=f"#{problem_id} - {title}",
                value=f"**Platform:** {platform}{difficulty_text}\n**Posted by:** {poster_name}\n[🔗 View Problem]({problem_url})",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if self.bot.user in message.mentions and message.attachments:
            if CONFIG['PROBLEM_CHANNEL_ID'] and message.channel.id == CONFIG['PROBLEM_CHANNEL_ID']:
                await self.handle_solution_submission(message)

    async def handle_solution_submission(self, message):
        attachment = message.attachments[0]
        if not attachment.filename.endswith('.pdf'):
            await message.reply("Please submit a PDF file.")
            return
        
        try:
            problem_id = int(message.content.split()[-1])
        except:
            await message.reply("Please specify the problem ID at the end of your message.")
            return
        
        solution_id = self.db.add_solution(problem_id, message.author.id, attachment.url)
        
        if CONFIG['MODERATOR_CHANNEL_ID']:
            mod_channel = self.bot.get_channel(CONFIG['MODERATOR_CHANNEL_ID'])
            if mod_channel and isinstance(mod_channel, discord.TextChannel):
                embed = discord.Embed(
                    title="📋 New Solution Submitted",
                    color=0xffa500,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(name="Solution ID", value=str(solution_id), inline=True)
                embed.add_field(name="Problem ID", value=str(problem_id), inline=True)
                embed.add_field(name="Submitted by", value=message.author.mention, inline=True)
                embed.set_footer(text=f"Use /score_solution {solution_id} to rate this solution")
                
                await mod_channel.send(embed=embed, file=await attachment.to_file())
        
        await message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(ProblemsCog(bot))
