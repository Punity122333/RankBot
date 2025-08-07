import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.config import load_config

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class RankBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        # Load cogs
        cogs = [
            'cogs.admin',
            'cogs.problems', 
            'cogs.scoring',
            'cogs.leaderboard'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")
        
        print(f"Bot is in {len(self.guilds)} guilds")
        commands_before = len(self.tree.get_commands())
        print(f"Commands to sync: {commands_before}")
        
        # List all commands
        for cmd in self.tree.get_commands():
            try:
                print(f"- {cmd.name}: {getattr(cmd, 'description', 'No description')}")
            except:
                print(f"- {cmd.name}")
        
        # Try syncing globally first
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands globally")
        except Exception as e:
            print(f"Failed to sync globally: {e}")
        
        # If you want to sync to a specific guild for faster testing, uncomment and add your guild ID:
        guild_id = 1369364220512174101  # Your Tech Club guild ID
        try:
            guild = discord.Object(id=guild_id)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to guild {guild_id}")
        except Exception as e:
            print(f"Failed to sync to guild: {e}")

bot = RankBot()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is now in {len(bot.guilds)} guilds:')
    for guild in bot.guilds:
        print(f'  - {guild.name} (ID: {guild.id})')
    load_config()
    
    # Try syncing to guilds after connection
    if bot.guilds:
        for guild in bot.guilds:
            try:
                synced = await bot.tree.sync(guild=guild)
                print(f"Synced {len(synced)} commands to guild: {guild.name}")
            except Exception as e:
                print(f"Failed to sync to guild {guild.name}: {e}")

@bot.event
async def on_guild_join(guild):
    print(f"Joined guild: {guild.name} (ID: {guild.id})")
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Auto-synced {len(synced)} commands to new guild: {guild.name}")
    except Exception as e:
        print(f"Failed to auto-sync to new guild {guild.name}: {e}")

if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Please set the DISCORD_BOT_TOKEN environment variable")
    else:
        bot.run(token)
