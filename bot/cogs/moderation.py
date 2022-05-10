
import aiofiles
import nextcord as discord
import os
import sys
import time
import asyncio
import aiosqlite

from nextcord.ext import commands
from nextcord import Colour, Embed, SlashOption, slash_command
from nextcord.ext.commands import has_permissions, command, Cog

def is_guild_owner():
    def predicate(ctx:commands.Context):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

def restart_program():
    sys.exit
    os.system("py main.py")

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.warnings = {}
        
    COG_EMOJI = "⚙"
        
    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            async with aiofiles.open(f"data/warnings/{guild.id}.txt", mode="a") as temp:
                pass

            self.bot.warnings[guild.id] = {}

        for guild in self.bot.guilds:
            async with aiofiles.open(f"data/warnings/{guild.id}.txt", mode="r") as file:
                lines = await file.readlines()

        for line in lines:
            data = line.split(" ")
            member_id = int(data[0])
            admin_id = int(data[1])
            warnID = int(data[2])
            reason = " ".join(data[3:]).strip("\n")

            try:
                self.bot.warnings[guild.id][member_id][0] += 1
                self.bot.warnings[guild.id][member_id][1].append((admin_id, reason, warnID))

            except KeyError:
                self.bot.warnings[guild.id][member_id] = [1, [(admin_id, reason, warnID)]]   
    
            
    @command(name='warn', description="Warns a member. [Moderator only] ")
    @commands.check_any(commands.is_owner(), is_guild_owner(), commands.has_permissions(manage_messages=True))
    async def warn(self, ctx, member: discord.Member=None, *, reason=None):

        warnID = f"{ctx.message.id}"

        if member is None:
            return await ctx.send("**The member you have provided couldn't be found or you did not provide one.**")

        if reason is None:
            return await ctx.send("**Please provide a reason for warning this user.**")
            
        try:
            first_warning = False
            self.bot.warnings[ctx.guild.id][member.id][0] += 1
            self.bot.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason, warnID))

        except KeyError:
            first_warning = True
            self.bot.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason, warnID)]]

        count = self.bot.warnings[ctx.guild.id][member.id][0]

        async with aiofiles.open(f"data/warnings/{ctx.guild.id}.txt", mode="a") as file:
            await file.write(f"{member.id} {ctx.author.id} {warnID} {reason}\n")

            warnEmbed = discord.Embed(title="Warn", description=f"{member.mention} has been warned and now has {count} {'warning' if first_warning else 'warnings'}.", color=Colour.red(), timestamp=ctx.message.created_at)
            warnEmbed.set_footer(text=f"Member warned by {ctx.author} | Warning ID: {warnID}")

            await ctx.send(embed=warnEmbed)
            await member.send(f"You have been warned in **{ctx.guild.name}** by {ctx.author}. **Reason:** {reason} Warning ID: {warnID}")
            
    @command(name='warnings', description="Shows all warnings a member has. [Moderator only] ",aliases=['warns'])
    @commands.check_any(commands.is_owner(), is_guild_owner(), commands.has_permissions(manage_messages=True))
    async def warnings(self, ctx, member: discord.Member=None):

        if member is None:
            return await ctx.send("**The member you provided couldn't be found or you did not provide one.**")

        embed = discord.Embed(title=f"Showing warnings for {member.name}#{member.discriminator} ({member.id})", description="", color=Colour.red(), timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Requested by {ctx.author}")
        try:
            i = 1
            for admin_id, reason, warnID in self.bot.warnings[ctx.guild.id][member.id][1]:
                admin = ctx.guild.get_member(admin_id)
                embed.description += f"**Warning {i}** - Given by: {admin.mention} (`{admin.id}`)\n **Reason:** `{reason}`\n **Warning ID:** `{warnID}`\n\n"
                i += 1

            await ctx.send(embed=embed)
        except KeyError: # No Warnings
            await ctx.send("This user has no warnings.")
            
    @command(name='delwarn', description="Deletes a warning a user has. [Moderator only] ",aliases=["dw"])
    @commands.check_any(commands.is_owner(), is_guild_owner(), commands.has_permissions(manage_messages=True))
    async def deletewarning(self, ctx, warnid:int):
        clearedWarns = discord.Embed(title="Warn", description=f"Deleted one warning.", color=Colour.red(), timestamp=ctx.message.created_at)
        clearedWarns.set_footer(text=f"Warning deleted by {ctx.author}")
        if warnid is None:
            return await ctx.send("**The ID you provided was not found or you did not specify one.**")
        else:
            with open(f'data/warnings/{ctx.guild.id}.txt', 'r') as f:
                lines = f.readlines()
            with open(f'data/warnings/{ctx.guild.id}.txt', 'w') as f:
                for line in lines:
                    if f'{warnid}' in line:
                        line = line.replace(f'{warnid}', '')
                    else:
                        f.write(line)
            await ctx.send(embed=clearedWarns)
        restart_program()
        
def setup(bot):
    bot.add_cog(moderation(bot))
    name = "Moderation"
    print(f"Loaded {name}")

            


