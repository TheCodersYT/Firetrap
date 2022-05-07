import nextcord as discord
import os
import sys
import time
import asyncio

from nextcord.ext import commands
from nextcord.embeds import EmptyEmbed
from nextcord import Colour, Embed, SlashOption, slash_command, Interaction
from nextcord.ext import menus

intents = discord.Intents()

bot = commands.Bot(command_prefix=">", intents=intents.all(), help_command=None)

for file in os.listdir("./cogs"):
  if file.endswith(".py"):
    bot.load_extension(f"cogs.{file[:-3]}")
    
class UrlButton(discord.ui.Button):
    def __init__(self, *, label, url, emoji=None):
        super().__init__(label=label, url=url, emoji=emoji)

class HelpDropdown(discord.ui.View):
    def __init__(self, user):
        self.user = user
        self.timeout = 15
        super().__init__()
        self.add_item(
            UrlButton(label="Support Server", url="https://discord.gg/xA3hBtujg7", emoji="💫")
        )
        # Set the options that will be presented inside the dropdown

    @discord.ui.select(
        placeholder="Choose your help page",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Moderation", description=f"`>help moderation`", emoji="⚒️"
            ),
            discord.SelectOption(
                label="Economy", description=f"`>help economy`", emoji="💰"
            ),
            discord.SelectOption(
                label="Music", description=f"`>help music`", emoji="🎵"
            ),
        ],
    )
    async def help_callback(self, select, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            em = discord.Embed(
                title="Not your help page!",
                description="This is not for you!",
                color=discord.Color.red(),
            )
            return await interaction.response.send_message(embed=em, ephemeral=True)
        select.placeholder = f"{select.values[0]} Help Page"
        if select.values[0] == "Moderation":
            embed = discord.Embed(
                title=f"{bot.user.name} Moderation Commands:",
                description=f"`>help [category]` for other information.",
            )
            for index, command in enumerate(bot.get_cog("moderation").get_commands()):
                description = command.description
                if not description or description is None or description == "":
                    description = "No description"
                embed.add_field(
                    name=f"`>{command.name} {command.signature if command.signature is not None else ''}`",
                    value=description,
                )
            await interaction.response.edit_message(embed=embed, view=self)
        elif select.values[0] == "Music":
            embed = discord.Embed(
                title=f"{bot.user.name} Music Commands:",
                description=f"`>help [category]` for other information.",
            )
            for command in bot.get_cog("music").walk_commands():
                description = command.description
                if not description or description is None or description == "":
                    description = "No description"
                embed.add_field(
                    name=f"`>{command.name} {command.signature if command.signature is not None else ''}`",
                    value=description,
                )
            await interaction.response.edit_message(embed=embed, view=self)
        elif select.values[0] == "Economy":
            embed = discord.Embed(
                title=f"{bot.user.name} Economy Commands:",
                description=f"`>help [category]` for other information.",
            )
            for command in bot.get_cog("economy").walk_commands():
                description = command.description
                if not description or description is None or description == "":
                    description = "No description"
                embed.add_field(
                    name=f"`>{command.name} {command.signature if command.signature is not None else ''}`",
                    value=description,
                )
            await interaction.response.edit_message(embed=embed, view=self)



# Main Help Commands:

@bot.group(invoke_without_command=True)
async def help(ctx:commands.Context):
    view = HelpDropdown(ctx.author)
    embed = discord.Embed(
        title=f"{bot.user.name} Help",
        description=f"`>help [category]` for more information.",
        color=Colour.random()
    )
    embed.set_thumbnail(url=f"{bot.user.display_avatar}")
    embed.add_field(
        name="Moderation:", value=f">help moderation", inline=False
    )
    embed.add_field(
        name="Economy:", value=f">help economy", inline=False
      )
    embed.add_field(
        name="Music:", value=f">help music", inline=False
      )
    embed.set_footer(
        text=f"Requested by {ctx.author} | Created by: ZxlcaLT#2462 | ",
        icon_url=f"{ctx.author.display_avatar}",
    )

    await ctx.send(embed=embed, view=view)
    
@help.command()
async def moderation(ctx):
    view = HelpDropdown(ctx.author)
    embed = discord.Embed(
        title=f"{bot.user.name} Moderation Commands:",
        description=f"Support Server: [Click Here!](https://discord.gg/xA3hBtujg7) || `>help [category]` for other information.",
        color=Colour.random()
    
    )
    for command in bot.get_cog("moderation").walk_commands():
        description = command.description
        if not description or description is None or description == "":
            description = "No description"
        embed.add_field(
            name=f"`>{command.name} {command.signature if command.signature is not None else ''}`",
            value=description,
        )
    await ctx.send(embed=embed, view=view)


@help.command()
async def economy(ctx):
    view = HelpDropdown(ctx.author)
    embed = discord.Embed(
        title=f"{bot.user.name} Economy Commands:",
        description=f"Support Server: [Click Here!](https://discord.gg/xA3hBtujg7) || `>help [category]` for other information.",
        color=Colour.random()
    )
    for command in bot.get_cog("economy").walk_commands():
        description = command.description
        if not description or description is None or description == "":
            description = "No description"
        embed.add_field(
            name=f"`>{command.name} {command.signature if command.signature is not None else ''}`",
            value=description,
        )
    await ctx.send(embed=embed, view=view)


@help.command()
async def music(ctx):
    view = HelpDropdown(ctx.author)
    embed = discord.Embed(
        title=f"{bot.user.name} Music Commands:",
        description=f"Support Server: [Click Here!](https://discord.gg/xA3hBtujg7) || `>help [category]` for other information.",
        color=Colour.random()
    )
    for command in bot.get_cog("music").walk_commands():
        description = command.description
        if not description or description is None or description == "":
            description = "No description"
        embed.add_field(
            name=f"`>{command.name} {command.signature if command.signature is not None else ''}`",
            value=description,
        )
    await ctx.send(embed=embed, view=view)


guilds = 964583985214803978

token = "ODk3NTUzOTI5MTc5NjUyMTg2.GBI0Nv.amIkSRAWhpOi82ZWE3ler7_t6Nexuv9R37njok"

@bot.event
async def on_ready():
  print(f"{bot.user.name}#{bot.user.discriminator} is ready!")

  
 

bot.run(token)
