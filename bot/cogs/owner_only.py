
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

class Owner_Only(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    COG_EMOJI = "🔧"
        
    @command(name='restart', description="Restarts the bot.")
    @is_owner()
    async def restart(self, ctx):
        await ctx.reply("Restarting...")
        restart_program()
        
    @command(name='reload', description="Reloads a cog.")
    @is_owner()
    async def reload(self, ctx, cog: str):
        await ctx.reply("Reloading `{}`".format(cog))
        self.bot.reload_extension(f"cogs.{cog}")
    
    @command(name="presence", description="Sets the bot's presence.")
    @is_owner()
    async def presence(self, ctx, *, text: str):
        await self.bot.change_presence(activity=discord.Game(name=text))
        await ctx.reply("Presence changed to `{}`".format(text))
    

def setup(bot):
    bot.add_cog(Owner_Only(bot))
    name = "Owner_Only"
    print(f"Loaded {name}")