import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from database import Database

class LeaderboardTypeView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.db = Database()

    @discord.ui.button(label="Mathematics Leaderboard", style=discord.ButtonStyle.primary, emoji="🔢")
    async def math_leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = MathLeaderboardView(self.bot)
        embed = await view.get_leaderboard_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        self.stop()

    @discord.ui.button(label="CP Leaderboard", style=discord.ButtonStyle.secondary, emoji="💻")
    async def cp_leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = CPLeaderboardView(self.bot)
        embed = await view.get_leaderboard_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        self.stop()

class MathLeaderboardView(discord.ui.View):
    def __init__(self, bot, page=0, per_page=10):
        super().__init__(timeout=300)
        self.bot = bot
        self.page = page
        self.per_page = per_page
        self.db = Database()

    async def get_leaderboard_embed(self):
        leaderboard = self.db.get_math_leaderboard_paginated(self.page * self.per_page, self.per_page)
        total_users = self.db.get_total_math_users_with_scores()
        
        if not leaderboard:
            embed = discord.Embed(
                title="🔢 Mathematics Leaderboard",
                description="No scores available yet!",
                color=0x00ff00
            )
            return embed
        
        embed = discord.Embed(
            title="🔢 Mathematics Leaderboard",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, score) in enumerate(leaderboard):
            user = self.bot.get_user(user_id)
            username = user.display_name if user else f"User {user_id}"
            rank = self.page * self.per_page + i + 1
            
            if rank <= 3:
                medal = medals[rank - 1]
            else:
                medal = f"{rank}."
            
            embed.add_field(
                name=f"{medal} {username}",
                value=f"{score} points",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.page + 1}/{(total_users + self.per_page - 1) // self.per_page} • Total users: {total_users}")
        return embed

    @discord.ui.button(label='◀️ Previous', style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            embed = await self.get_leaderboard_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='▶️ Next', style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_users = self.db.get_total_math_users_with_scores()
        max_pages = (total_users + self.per_page - 1) // self.per_page
        
        if self.page < max_pages - 1:
            self.page += 1
            embed = await self.get_leaderboard_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

class CPLeaderboardView(discord.ui.View):
    def __init__(self, bot, page=0, per_page=10):
        super().__init__(timeout=300)
        self.bot = bot
        self.page = page
        self.per_page = per_page
        self.db = Database()

    async def get_leaderboard_embed(self):
        leaderboard = self.db.get_cp_leaderboard_paginated(self.page * self.per_page, self.per_page)
        total_users = self.db.get_total_cp_users_with_scores()
        
        if not leaderboard:
            embed = discord.Embed(
                title="💻 Competitive Programming Leaderboard",
                description="No scores available yet!",
                color=0x0099ff
            )
            return embed
        
        embed = discord.Embed(
            title="💻 Competitive Programming Leaderboard",
            color=0x0099ff,
            timestamp=datetime.now(timezone.utc)
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, score) in enumerate(leaderboard):
            user = self.bot.get_user(user_id)
            username = user.display_name if user else f"User {user_id}"
            rank = self.page * self.per_page + i + 1
            
            if rank <= 3:
                medal = medals[rank - 1]
            else:
                medal = f"{rank}."
            
            embed.add_field(
                name=f"{medal} {username}",
                value=f"{score} points",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.page + 1}/{(total_users + self.per_page - 1) // self.per_page} • Total users: {total_users}")
        return embed

    @discord.ui.button(label='◀️ Previous', style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            embed = await self.get_leaderboard_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='▶️ Next', style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_users = self.db.get_total_cp_users_with_scores()
        max_pages = (total_users + self.per_page - 1) // self.per_page
        
        if self.page < max_pages - 1:
            self.page += 1
            embed = await self.get_leaderboard_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="leaderboard", description="View leaderboards")
    async def leaderboard(self, interaction: discord.Interaction):
        view = LeaderboardTypeView(self.bot)
        embed = discord.Embed(
            title="🏆 Leaderboards",
            description="Which leaderboard would you like to view?",
            color=0xffd700
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="math_leaderboard", description="View mathematics leaderboard")
    async def math_leaderboard(self, interaction: discord.Interaction):
        view = MathLeaderboardView(self.bot)
        embed = await view.get_leaderboard_embed()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="cp_leaderboard", description="View competitive programming leaderboard")
    async def cp_leaderboard(self, interaction: discord.Interaction):
        view = CPLeaderboardView(self.bot)
        embed = await view.get_leaderboard_embed()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
