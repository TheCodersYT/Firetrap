import nextcord as discord
import os
import sys
import time
import asyncio

from nextcord.ext import commands
from nextcord import Colour, Embed, SlashOption, slash_command

intents = nextcord.Intents()

bot = commands.Bot(command_prefix=">", intents=intents.all())

for file in os.listdir("./cogs"):
  if file.endswith(".py"):
    bot.load_extension(f"cogs.{file[:-3]")

token = "ODk3NTUzOTI5MTc5NjUyMTg2.GBI0Nv.amIkSRAWhpOi82ZWE3ler7_t6Nexuv9R37nj" # add ok on the end of the token

@bot.event
async def on_ready():
  print(f"{bot.user.name}#{bot.user.discriminator} is ready!")
  channel = bot.get_channel(967853173073129512)
  
  await channel.send("I am online.")
  
 

bot.run(token)
