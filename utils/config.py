import json
import discord
from typing import Optional, Dict

CONFIG: Dict[str, Optional[int]] = {
    'PROBLEM_CHANNEL_ID': None,
    'MODERATOR_CHANNEL_ID': None,
    'LEADERBOARD_CHANNEL_ID': None,
    'MODERATOR_ROLE_ID': None
}

def load_config():
    """Load configuration from config.json file"""
    try:
        with open('config.json', 'r') as f:
            global CONFIG
            CONFIG.update(json.load(f))
    except FileNotFoundError:
        save_config()

def save_config():
    """Save configuration to config.json file"""
    with open('config.json', 'w') as f:
        json.dump(CONFIG, f, indent=4)

def is_moderator_interaction(interaction: discord.Interaction) -> bool:
    """Check if user has moderator permissions for interactions"""
    if not interaction.guild:
        return False
    member = interaction.guild.get_member(interaction.user.id)
    if not member:
        return False
    if CONFIG['MODERATOR_ROLE_ID'] is None:
        return member.guild_permissions.manage_messages
    role = discord.utils.get(interaction.guild.roles, id=CONFIG['MODERATOR_ROLE_ID'])
    return role in member.roles if role else member.guild_permissions.manage_messages

def is_moderator(ctx) -> bool:
    """Check if user has moderator permissions for commands"""
    if CONFIG['MODERATOR_ROLE_ID'] is None:
        return ctx.author.guild_permissions.manage_messages
    role = discord.utils.get(ctx.guild.roles, id=CONFIG['MODERATOR_ROLE_ID'])
    return role in ctx.author.roles if role else ctx.author.guild_permissions.manage_messages
