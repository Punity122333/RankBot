import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from database import Database
from utils.config import CONFIG, is_moderator_interaction
from typing import Optional

class PostTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📊 Math Problem", style=discord.ButtonStyle.primary, emoji="📊")
    async def math_problem(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MathProblemModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="💻 CP Problem", style=discord.ButtonStyle.secondary, emoji="💻")
    async def cp_problem(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CPProblemModal()
        await interaction.response.send_modal(modal)

class MathProblemModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Post Math Problem")
        
        self.title_input = discord.ui.TextInput(
            label="Problem Title",
            placeholder="Enter the math problem title...",
            max_length=200
        )
        self.add_item(self.title_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Store the problem title temporarily for the user to upload PDF
        # In a production system, you might want to use a database or cache
        # For now, we'll provide instructions
        bot_name = interaction.client.user.display_name if interaction.client.user else "Bot"
        embed = discord.Embed(
            title="📎 Upload Problem PDF",
            description=f"**Problem Title:** {self.title_input.value}\n\nPlease upload the PDF file containing the math problem as a message in this channel. Make sure to mention the bot (@{bot_name}) in your message with the PDF attachment.",
            color=0x00ff00
        )
        embed.add_field(
            name="Format",
            value=f"@{bot_name} Math Problem: {self.title_input.value}",
            inline=False
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

class CPProblemModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Post CP Problem")
        
        self.title_input = discord.ui.TextInput(
            label="Problem Title",
            placeholder="Enter the competitive programming problem title...",
            max_length=200
        )
        self.add_item(self.title_input)
        
        self.url_input = discord.ui.TextInput(
            label="Problem URL",
            placeholder="Enter the problem URL (e.g., Codeforces, LeetCode link)...",
            max_length=500
        )
        self.add_item(self.url_input)
        
        self.platform_input = discord.ui.TextInput(
            label="Platform",
            placeholder="e.g., Codeforces, LeetCode, AtCoder, etc...",
            max_length=100
        )
        self.add_item(self.platform_input)
        
        self.difficulty_input = discord.ui.TextInput(
            label="Difficulty",
            placeholder="Enter difficulty (e.g., Easy, Medium, Hard, Div2A, etc)...",
            max_length=50
        )
        self.add_item(self.difficulty_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        db = Database()
        try:
            problem_id = db.add_cp_problem(
                title=self.title_input.value,
                problem_url=self.url_input.value,
                platform=self.platform_input.value,
                difficulty=self.difficulty_input.value,
                posted_by=interaction.user.id
            )
            
            embed = discord.Embed(
                title="💻 New CP Problem Posted!",
                color=0x0099ff,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Title", value=self.title_input.value, inline=False)
            embed.add_field(name="Platform", value=self.platform_input.value, inline=True)
            embed.add_field(name="Difficulty", value=self.difficulty_input.value, inline=True)
            embed.add_field(name="Problem ID", value=str(problem_id), inline=True)
            embed.add_field(name="Posted by", value=interaction.user.mention, inline=True)
            embed.add_field(name="URL", value=f"[View Problem]({self.url_input.value})", inline=False)
            
            # Post to the configured problem channel
            if CONFIG['PROBLEM_CHANNEL_ID']:
                problem_channel = interaction.client.get_channel(CONFIG['PROBLEM_CHANNEL_ID'])
                if problem_channel and isinstance(problem_channel, discord.TextChannel):
                    await problem_channel.send(embed=embed)
                    await interaction.response.send_message(f"✅ CP problem posted successfully! Problem ID: {problem_id}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"⚠️ Problem created (ID: {problem_id}) but couldn't post to channel. Please check channel configuration.", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ Problem created (ID: {problem_id}) but no problem channel configured. Use /setup to configure channels.", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"Error posting problem: {str(e)}", ephemeral=True)
        finally:
            db.close()

class SubmitTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📊 Math Solution", style=discord.ButtonStyle.primary, emoji="📊")
    async def math_solution(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get available math problems
        db = Database()
        try:
            problems = db.get_math_problems(limit=25)
            if not problems:
                await interaction.response.send_message("No math problems available to submit for.", ephemeral=True)
                return
            
            view = MathSolutionView(problems)
            embed = discord.Embed(
                title="📊 Submit Math Solution",
                description="Select the math problem you want to submit a solution for:",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        finally:
            db.close()
    
    @discord.ui.button(label="💻 CP Submission", style=discord.ButtonStyle.secondary, emoji="💻")
    async def cp_submission(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get available CP problems
        db = Database()
        try:
            problems = db.get_cp_problems(limit=25)
            if not problems:
                await interaction.response.send_message("No CP problems available to submit for.", ephemeral=True)
                return
            
            view = CPSubmissionView(problems)
            embed = discord.Embed(
                title="💻 Submit CP Solution",
                description="Select the CP problem you want to submit a solution for:",
                color=0x0099ff
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        finally:
            db.close()

class MathSolutionModal(discord.ui.Modal):
    def __init__(self, problems):
        super().__init__(title="Submit Math Solution")
        
        # Create problem selection dropdown
        self.problems = problems
        self.problem_select = discord.ui.Select(
            placeholder="Choose a math problem to submit solution for...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=f"ID {problem[0]}: {problem[1][:80]}...",
                    description=f"Posted by User {problem[3]}",
                    value=str(problem[0])
                )
                for problem in problems[:25]  # Discord limit is 25 options
            ]
        )
        
        # We'll handle problem selection in a view instead
        
    async def on_submit(self, interaction: discord.Interaction):
        # This won't be called directly - we'll use a view with select dropdown
        pass

class MathSolutionView(discord.ui.View):
    def __init__(self, problems):
        super().__init__(timeout=300)
        self.problems = problems
        
        # Add problem selection dropdown
        self.problem_select = discord.ui.Select(
            placeholder="Choose a math problem to submit solution for...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=f"ID {problem[0]}: {problem[1][:80]}" + ("..." if len(problem[1]) > 80 else ""),
                    description=f"Posted by User {problem[3]}",
                    value=str(problem[0])
                )
                for problem in problems[:25]  # Discord limit is 25 options
            ]
        )
        self.problem_select.callback = self.problem_selected
        self.add_item(self.problem_select)
    
    async def problem_selected(self, interaction: discord.Interaction):
        problem_id = int(self.problem_select.values[0])
        selected_problem = next((p for p in self.problems if p[0] == problem_id), None)
        
        if selected_problem:
            embed = discord.Embed(
                title="📎 Upload Solution PDF",
                description=f"Please upload your PDF solution for **{selected_problem[1]}** (Problem ID: {problem_id})",
                color=0x00ff00
            )
            embed.add_field(name="Next Step", value="Upload a PDF file in this channel with your solution.", inline=False)
            embed.add_field(name="Problem URL", value=f"[View Problem]({selected_problem[2]})", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        self.stop()

class CPCodeSubmissionModal(discord.ui.Modal):
    def __init__(self, problem_id, problem_title):
        super().__init__(title="Submit CP Code")
        
        self.problem_id = problem_id
        self.problem_title = problem_title
        
        self.language_input = discord.ui.TextInput(
            label="Programming Language",
            placeholder="e.g., Python, C++, Java, JavaScript...",
            max_length=50
        )
        self.add_item(self.language_input)
        
        self.code_input = discord.ui.TextInput(
            label="Your Code",
            placeholder="Paste your solution code here...",
            style=discord.TextStyle.paragraph,
            max_length=2000
        )
        self.add_item(self.code_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        db = Database()
        try:
            submission_id = db.add_cp_submission(
                problem_id=self.problem_id,
                user_id=interaction.user.id,
                code=self.code_input.value,
                language=self.language_input.value,
                file_url=None
            )
            
            embed = discord.Embed(
                title="✅ CP Code Submission Received!",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Submission ID", value=str(submission_id), inline=True)
            embed.add_field(name="Problem ID", value=str(self.problem_id), inline=True)
            embed.add_field(name="Language", value=self.language_input.value, inline=True)
            embed.add_field(name="Problem Title", value=self.problem_title, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Notify moderators
            if CONFIG['MODERATOR_CHANNEL_ID']:
                mod_channel = interaction.client.get_channel(CONFIG['MODERATOR_CHANNEL_ID'])
                if mod_channel and isinstance(mod_channel, discord.TextChannel):
                    mod_embed = discord.Embed(
                        title="💻 New CP Submission",
                        color=0x0099ff,
                        timestamp=datetime.now(timezone.utc)
                    )
                    mod_embed.add_field(name="Submission ID", value=str(submission_id), inline=True)
                    mod_embed.add_field(name="Problem", value=f"{self.problem_title} (ID: {self.problem_id})", inline=True)
                    mod_embed.add_field(name="Submitted by", value=interaction.user.mention, inline=True)
                    mod_embed.add_field(name="Language", value=self.language_input.value, inline=True)
                    mod_embed.add_field(name="Code", value=f"```{self.language_input.value.lower()}\n{self.code_input.value[:1000]}\n```", inline=False)
                    mod_embed.set_footer(text=f"Use /score_cp_submission {submission_id} to rate this submission")
                    
                    await mod_channel.send(embed=mod_embed)
        finally:
            db.close()

class CPSubmissionView(discord.ui.View):
    def __init__(self, problems):
        super().__init__(timeout=300)
        self.problems = problems
        
        # Add problem selection dropdown
        self.problem_select = discord.ui.Select(
            placeholder="Choose a CP problem to submit solution for...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=f"ID {problem[0]}: {problem[1][:80]}" + ("..." if len(problem[1]) > 80 else ""),
                    description=f"{problem[3]} - {problem[2]}",  # platform - difficulty
                    value=str(problem[0])
                )
                for problem in problems[:25]  # Discord limit is 25 options
            ]
        )
        self.problem_select.callback = self.problem_selected
        self.add_item(self.problem_select)
        
        # Add submission type buttons (disabled initially)
        self.code_button = discord.ui.Button(label="📝 Submit Code", style=discord.ButtonStyle.primary, disabled=True)
        self.code_button.callback = self.submit_code
        self.add_item(self.code_button)
        
        self.file_button = discord.ui.Button(label="📎 Submit File", style=discord.ButtonStyle.secondary, disabled=True)
        self.file_button.callback = self.submit_file
        self.add_item(self.file_button)
        
        self.selected_problem = None
    
    async def problem_selected(self, interaction: discord.Interaction):
        problem_id = int(self.problem_select.values[0])
        self.selected_problem = next((p for p in self.problems if p[0] == problem_id), None)
        
        if not self.selected_problem:
            await interaction.response.send_message("Problem not found.", ephemeral=True)
            return
        
        # Enable submission buttons
        self.code_button.disabled = False
        self.file_button.disabled = False
        
        embed = discord.Embed(
            title="💻 CP Problem Selected",
            description=f"You selected: **{self.selected_problem[1]}**\n\nNow choose how you want to submit:",
            color=0x0099ff
        )
        embed.add_field(name="Problem ID", value=str(problem_id), inline=True)
        embed.add_field(name="Platform", value=self.selected_problem[3], inline=True)
        embed.add_field(name="Difficulty", value=self.selected_problem[4], inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def submit_code(self, interaction: discord.Interaction):
        if not self.selected_problem:
            await interaction.response.send_message("Please select a problem first.", ephemeral=True)
            return
        
        modal = CPCodeSubmissionModal(self.selected_problem[0], self.selected_problem[1])
        await interaction.response.send_modal(modal)
        self.stop()
    
    async def submit_file(self, interaction: discord.Interaction):
        if not self.selected_problem:
            await interaction.response.send_message("Please select a problem first.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📎 Upload Solution File",
            description=f"Please upload your code file for **{self.selected_problem[1]}** (Problem ID: {self.selected_problem[0]})",
            color=0x0099ff
        )
        embed.add_field(name="Next Step", value="Upload a code file in this channel with your solution.", inline=False)
        embed.add_field(name="Problem URL", value=f"[View Problem]({self.selected_problem[1]})", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()

class ProblemsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="post", description="Post a new problem (interactive)")
    async def post_problem(self, interaction: discord.Interaction):
        from utils.config import is_moderator_interaction
        if not is_moderator_interaction(interaction):
            await interaction.response.send_message("You don't have permission to post problems.", ephemeral=True)
            return
        
        view = PostTypeView()
        embed = discord.Embed(
            title="📋 Post New Problem",
            description="Choose the type of problem you want to post:",
            color=0xffd700
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="submit", description="Submit a solution (interactive)")
    async def submit_solution(self, interaction: discord.Interaction):
        view = SubmitTypeView()
        embed = discord.Embed(
            title="📤 Submit Solution",
            description="Choose the type of solution you want to submit:",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="list_math_problems", description="List recent math problems")
    async def list_math_problems(self, interaction: discord.Interaction):
        problems = self.db.get_math_problems(limit=10)
        
        if not problems:
            await interaction.response.send_message("No math problems found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Recent Math Problems",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        for problem_id, title, pdf_url, posted_by, posted_at in problems:
            user = self.bot.get_user(posted_by)
            username = user.display_name if user else f"User {posted_by}"
            embed.add_field(
                name=f"ID {problem_id}: {title}",
                value=f"By {username} | [View PDF]({pdf_url})",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list_cp_problems", description="List recent competitive programming problems")
    async def list_cp_problems(self, interaction: discord.Interaction):
        problems = self.db.get_cp_problems(limit=10)
        
        if not problems:
            await interaction.response.send_message("No CP problems found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💻 Recent CP Problems",
            color=0x0099ff,
            timestamp=datetime.now(timezone.utc)
        )
        
        for problem_id, title, problem_url, platform, difficulty, posted_by, posted_at in problems:
            user = self.bot.get_user(posted_by)
            username = user.display_name if user else f"User {posted_by}"
            
            embed.add_field(
                name=f"ID {problem_id}: {title}",
                value=f"Platform: {platform} | Difficulty: {difficulty}\nBy {username} | [View Problem]({problem_url})",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle file uploads for problem posting and solution submissions"""
        if message.author.bot:
            return
        
        # Handle PDF uploads for math problems
        if message.attachments and self.bot.user in message.mentions:
            # Check if user has moderator permissions
            if message.guild:
                member = message.guild.get_member(message.author.id)
                if member and CONFIG['MODERATOR_ROLE_ID']:
                    role = discord.utils.get(message.guild.roles, id=CONFIG['MODERATOR_ROLE_ID'])
                    has_permission = role in member.roles if role else member.guild_permissions.manage_messages
                else:
                    has_permission = member.guild_permissions.manage_messages if member else False
                
                if not has_permission:
                    await message.add_reaction("❌")
                    await message.reply("You don't have permission to post problems.", delete_after=10)
                    return
            for attachment in message.attachments:
                if attachment.filename.endswith('.pdf'):
                    # Check if this is a math problem upload
                    if "math problem:" in message.content.lower() or "math problem " in message.content.lower():
                        # Extract problem title from message
                        content_lower = message.content.lower()
                        if "math problem:" in content_lower:
                            title = message.content.split("Math Problem:", 1)[-1].strip()
                        elif "math problem " in content_lower:
                            title = message.content.split("Math Problem", 1)[-1].strip()
                        else:
                            title = "Untitled Math Problem"
                        
                        # Clean up the title (remove bot mentions)
                        title = title.replace(f"<@{self.bot.user.id}>", "").strip()
                        if not title:
                            title = "Untitled Math Problem"
                        
                        db = Database()
                        try:
                            problem_id = db.add_math_problem(
                                title=title,
                                pdf_url=attachment.url,
                                posted_by=message.author.id
                            )
                            
                            embed = discord.Embed(
                                title="📊 New Math Problem Posted!",
                                color=0x00ff00,
                                timestamp=datetime.now(timezone.utc)
                            )
                            embed.add_field(name="Title", value=title, inline=False)
                            embed.add_field(name="Problem ID", value=str(problem_id), inline=True)
                            embed.add_field(name="Posted by", value=message.author.mention, inline=True)
                            embed.add_field(name="PDF", value=f"[View Problem]({attachment.url})", inline=False)
                            
                            # Post to the configured problem channel
                            if CONFIG['PROBLEM_CHANNEL_ID']:
                                problem_channel = self.bot.get_channel(CONFIG['PROBLEM_CHANNEL_ID'])
                                if problem_channel and isinstance(problem_channel, discord.TextChannel):
                                    await problem_channel.send(embed=embed)
                                    await message.add_reaction("✅")
                                else:
                                    await message.reply(f"⚠️ Problem created (ID: {problem_id}) but couldn't post to channel. Please check channel configuration.")
                            else:
                                await message.reply(f"⚠️ Problem created (ID: {problem_id}) but no problem channel configured. Use /setup to configure channels.")
                            
                        except Exception as e:
                            await message.reply(f"Error posting math problem: {str(e)}")
                        finally:
                            db.close()
                    
                elif any(attachment.filename.endswith(ext) for ext in ['.py', '.cpp', '.java', '.js', '.c', '.cs', '.go', '.rs', '.rb', '.php']):
                    # Handle code file uploads for solutions
                    pass

async def setup(bot):
    await bot.add_cog(ProblemsCog(bot))
