
from operator import is_
import aiofiles
import nextcord as discord
import os
import sys
import time
import asyncio
import aiosqlite

from nextcord.ext import commands
from nextcord import Colour, Embed, SlashOption, slash_command
from nextcord.ext.commands import has_permissions, command, Cog, is_owner

def restart_program():
    sys.exit
    os.system("py main.py")

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    COG_EMOJI = "🎵"

def setup(bot):
    bot.add_cog(music(bot))
    name = "Music"
    print(f"Loaded {name}")