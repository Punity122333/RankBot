# import discord
# from discord.ext import commands
# from discord import app_commands
# from datetime import datetime, timezone
# from database import Database
# from utils.config import CONFIG

# class SubmissionsCog(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.db = Database()

#     @app_commands.command(name="submit_pdf", description="Submit a PDF solution for a problem")
#     @app_commands.describe(
#         problem_id="ID of the problem you're solving",
#         pdf_file="PDF file containing your solution"
#     )
#     @app_commands.checks.cooldown(1, 60, key=lambda i: i.user.id)  # 1 per minute per user
#     async def submit_pdf_solution(self, interaction: discord.Interaction, problem_id: int, pdf_file: discord.Attachment):
#         if not pdf_file.filename.endswith('.pdf'):
#             await interaction.response.send_message("Please attach a PDF file.", ephemeral=True)
#             return
        
#         solution_id = self.db.add_solution(problem_id, interaction.user.id, pdf_file.url)
        
#         if CONFIG['MODERATOR_CHANNEL_ID']:
#             mod_channel = self.bot.get_channel(CONFIG['MODERATOR_CHANNEL_ID'])
#             if mod_channel and isinstance(mod_channel, discord.TextChannel):
#                 embed = discord.Embed(
#                     title="📋 New Solution Submitted",
#                     color=0xffa500,
#                     timestamp=datetime.now(timezone.utc)
#                 )
#                 embed.add_field(name="Solution ID", value=str(solution_id), inline=True)
#                 embed.add_field(name="Problem ID", value=str(problem_id), inline=True)
#                 embed.add_field(name="Submitted by", value=interaction.user.mention, inline=True)
#                 embed.set_footer(text=f"Use /score_solution {solution_id} to rate this solution")
                
#                 await mod_channel.send(embed=embed, file=await pdf_file.to_file())
        
#         await interaction.response.send_message(f"✅ Your PDF solution has been submitted! Solution ID: {solution_id}", ephemeral=True)

#     @app_commands.command(name="submit", description="Submit a code solution")
#     @app_commands.describe(
#         language="Programming language used",
#         code="Your code solution"
#     )
#     @app_commands.checks.cooldown(1, 60, key=lambda i: i.user.id)  # 1 per minute per user
#     async def submit_solution(self, interaction: discord.Interaction, language: str, code: str):
#         # Code length validation
#         if len(code) > 4000:
#             await interaction.response.send_message("❌ Code is too long! Please keep it under 4000 characters.", ephemeral=True)
#             return
        
#         submission_id = self.db.add_submission(interaction.user.id, code, language)
        
#         if CONFIG['MODERATOR_CHANNEL_ID']:
#             mod_channel = self.bot.get_channel(CONFIG['MODERATOR_CHANNEL_ID'])
#             if mod_channel and isinstance(mod_channel, discord.TextChannel):
#                 embed = discord.Embed(
#                     title="💻 New Code Submission",
#                     color=0x0099ff,
#                     timestamp=datetime.now(timezone.utc)
#                 )
#                 embed.add_field(name="Submission ID", value=str(submission_id), inline=True)
#                 embed.add_field(name="Language", value=language, inline=True)
#                 embed.add_field(name="Submitted by", value=interaction.user.mention, inline=True)
#                 embed.add_field(name="Code", value=f"```{language}\n{code[:1000]}{'...' if len(code) > 1000 else ''}\n```", inline=False)
#                 embed.set_footer(text=f"Use /score_submission {submission_id} to rate")
                
#                 await mod_channel.send(embed=embed)
        
#         await interaction.response.send_message(f"✅ Your solution has been submitted! Submission ID: {submission_id}", ephemeral=True)

# async def setup(bot):
#     await bot.add_cog(SubmissionsCog(bot))
