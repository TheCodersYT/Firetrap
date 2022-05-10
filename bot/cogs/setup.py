import sqlite3
import nextcord as discord
import aiosqlite as sql3
import asyncio
import os
import sys
from nextcord.ext import commands
from nextcord import Colour, Embed, SlashOption, slash_command


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def config(self, ctx):
        async with sql3.connect(f"data/logging/{ctx.guild.id}.db") as db:
            async with db.cursor() as cursor: 
                await cursor.execute("CREATE TABLE IF NOT EXISTS logging (channel_id INTEGER, type TEXT)") # create table if not exists
                
                embed = Embed(title=f"Config for {ctx.guild.name}", colour=Colour.og_blurple()) # main embed

                await cursor.execute('SELECT channel_id FROM logging WHERE type = ?', ("logging",)) # check if logging is in database
                data = await cursor.fetchone()
                if data: # if there is a channel set for logging
                    channel = self.bot.get_channel(data[0])
                    embed.add_field(name="Logging channel:", value=f"✔ : {channel.mention}", inline=False)
                else: # if no logging channel is set
                    embed.add_field(name="Logging channel:", value=f"❌ : Not set", inline=False)
                    
        db1 = sqlite3.connect(f"data/prefixes/{ctx.guild.id}.db")
        cur = db1.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id INTEGER, prefix TEXT)")
        cur.execute("INSERT INTO prefixes (guild_id, prefix) VALUES (?, ?)", (ctx.guild.id, ">"))
        cur.execute(f"SELECT prefix FROM prefixes WHERE guild_id = ?", (ctx.guild.id,))
        prefix = cur.fetchone()
        
        if prefix is None or prefix == ">":
            embed.add_field(name="Prefix:", value=f"❌ : Not set - `>`", inline=False)
        else:
            embed.add_field(name="Prefix:", value=f"✔ : `{prefix[0]}`", inline=False)
        
                    
                    
        await ctx.send(embed=embed)
                
    
    @config.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def logging(self, ctx:commands.Context, channel:discord.TextChannel=None):
        if channel is not None:       
            if channel.guild.id != ctx.guild.id: # if the channel is not in the same guild
                return await ctx.send("That channel is not in this server.")
            
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                ),
                ctx.author: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                ),
                ctx.guild.me:discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                )
            }
            
            try:
                c = await channel.edit(name="kors-logging", topic="Logging channel for Kors.  -- DO NOT DELETE/RENAME! --", reason="Logging channel for Kors.  -- DO NOT DELETE/RENAME! --", overwrites=overwrites)
                async with sql3.connect(f"data/logging/{ctx.guild.id}.db") as db:
                    async with db.cursor() as cursor:
                        await cursor.execute("CREATE TABLE IF NOT EXISTS logging (channel_id INTEGER, type TEXT)")
                        await cursor.execute("INSERT INTO logging VALUES (?, ?)", (c.id, "logging",))
                        
                    await db.commit()
                        
                await ctx.send(f"Logging channel set to {c.mention}")      
            except discord.Forbidden:
                await ctx.send("I don't have the permission to edit channels. Please give me the permission.")
                return

        if channel is None:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                ),
                ctx.author: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                ),
                ctx.guild.me:discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                )
            }
            try:
                c = await ctx.guild.create_text_channel(name="kors-logging", topic="Logging channel for Kors.  -- DO NOT DELETE/RENAME! --", reason="Logging channel for Kors.  -- DO NOT DELETE/RENAME! --", overwrites=overwrites)        
                
                async with sql3.connect(f"data/logging/{ctx.guild.id}.db") as db:
                    async with db.cursor() as cursor:
                        await cursor.execute("CREATE TABLE IF NOT EXISTS logging (channel_id INTEGER, type TEXT)")
                        await cursor.execute('SELECT channel_id FROM logging WHERE type = ?', ("logging",))
                        data = await cursor.fetchone()
                        if data:
                            return await ctx.send("Logging channel is already set!")
                        else:
                            await cursor.execute("INSERT INTO logging VALUES (?, ?)", (c.id, "logging",))
                        
                    await db.commit()
                    
                
                await ctx.send(f"Logging channel set to {c.mention}")      
                
            except discord.Forbidden:
                await ctx.send("I don't have the permission to create channels. Please give me the permission.")
                return


    @config.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx:commands.Context, new_prefix:str=None):
        if new_prefix is None:
            return await ctx.send("Please specify a new prefix.")
        db = sqlite3.connect(f'data/prefixes/{ctx.guild.id}.db')
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id INTEGER, prefix TEXT)")
        cursor.execute(f"SELECT prefix FROM prefixes WHERE guild_id = {ctx.guild.id}")
        prefix = cursor.fetchone()
        
        
        if prefix is None:
            cursor.execute("INSERT INTO prefixes(guild_id, prefix) VALUES(?,?)", (ctx.guild.id, new_prefix,))
            prefixsetem = discord.Embed(title=f"✔ **{ctx.guild.name}**'s prefix set to `{new_prefix}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=prefixsetem)
            
        elif prefix is not None:
            cursor.execute("UPDATE prefixes SET prefix = ? WHERE guild_id = ?", (new_prefix, ctx.guild.id))
            prefixsetem = discord.Embed(title=f"✔ **{ctx.guild.name}**'s prefix updated to `{new_prefix}`", description=f"Updated by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=prefixsetem)

        db.commit()
        cursor.close()
        db.close()
                
                

                    
    @config.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def remove(self, ctx, channel:discord.TextChannel=None):
        if channel is None:
            return await ctx.send("Please specify a channel to remove from the logging database.")
        
        
        async with sql3.connect(f"data/logging/{ctx.guild.id}.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT channel_id FROM logging WHERE channel_id = ?', (channel.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute('DELETE FROM logging WHERE channel_id = ? AND type = ?', (channel.id, "logging",))
                    await ctx.send(f"Removed {channel.mention} from the logging database.")
                else:
                    return await ctx.send(f"There is no logging set for channel {channel.mention}.")
            
            await db.commit() 
            
    
        
                    

def setup(bot):
    bot.add_cog(Setup(bot))