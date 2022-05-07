
import aiofiles
import nextcord as discord
import os
import random
import aiosqlite as sql3
import sys
import time
import asyncio

from nextcord.ext import commands
from nextcord import Colour, Embed, SlashOption, slash_command, Interaction
from nextcord.ext import application_checks as ac
from nextcord.ext.commands.cooldowns import BucketType


guilds = 964583985214803978

class UrlButton(discord.ui.Button):
    def __init__(self, *, label, url, emoji=None):
        super().__init__(label=label, url=url, emoji=emoji)
        
def restart_program():
    sys.exit
    os.system("py main.py")
def get_random_color():
    return random.choice([0x4287f5, 0xf54242, 0xf5f242])

async def open_account(user: Interaction.user):
    db = await sql3.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * FROM main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    if result:
        return
    if not result:
        sql = "INSERT INTO main(member_id, wallet, bank) VALUES(?,?,?)"
        val = (user.id, 500, 0)

    await cursor.execute(sql, val)
    await db.commit()
    await cursor.close()
    await db.close()

async def check_bal_greater_than(user: Interaction.user, amount: int):
    db = await sql3.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * FROM main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    if result[1] >= amount:
        return True
    return False

async def add_bal(user: Interaction.user, amount: int):
    db = await sql3.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * from main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    sql = f"UPDATE main SET wallet = ? WHERE member_id = ?"
    val = (result[1] + amount, user.id)

    await cursor.execute(sql, val)
    await db.commit()
    await cursor.close()
    await db.close()

async def remove_bal(user: Interaction.user, amount: int):
    db = await sql3.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * from main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    sql = f"UPDATE main SET wallet = ? WHERE member_id = ?"
    val = (result[1] - amount, user.id)

    await cursor.execute(sql, val)
    await db.commit()
    await cursor.close()
    await db.close() 

async def remove_bank(user: Interaction.user, amount: int):
    db = await sql3.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * from main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    sql = f"UPDATE main SET bank = ? WHERE member_id = ?"
    val = (result[1] - amount, user.id)

    await cursor.execute(sql, val)
    await db.commit()
    await cursor.close()
    await db.close() 

class Slash_Commands(commands.Cog):
    """Slash commands for the bot."""
    def __init__(self, bot):
        self.bot = bot
        self.bot.warnings = {}
        self._bot = bot
    
    """
    Owner Slash Commands
    """
    
    COG_EMOJI = "💹"
    
    @slash_command(name="owner", description="Owner commands.")
    async def owner(self, interaction:Interaction):
        pass
    
    @owner.subcommand(name='restart', description="Restarts the bot.")
    @ac.is_owner()
    async def restart(self, interaction:Interaction):
        await interaction.send("Restarting...", ephemeral=True)
        restart_program()
        
    @owner.subcommand(name='reload', description="Reloads a cog.")
    @ac.is_owner()
    async def reload(self, interaction:Interaction, cog : str = SlashOption(required=True, description="The cog to reload.")):
        await interaction.send("Reloading `{}`".format(cog), ephemeral=True)
        self.bot.reload_extension(f"cogs.{cog}")
    
    @owner.subcommand(name="presence", description="Sets the bot's presence.")
    @ac.is_owner()
    async def presence(self, interaction:Interaction, *, text: str = SlashOption(required=True, description="The text to set the presence to.")):
        await self.bot.change_presence(activity=discord.Game(name=text))
        await interaction.send("Presence changed to `{}`".format(text), ephemeral=True)
        
    """
    Moderation Slash Commands
    """
    
    ###############################
    
    @slash_command(name="mod", guild_ids=[guilds])
    async def mod(self, interaction:Interaction):
        pass
    
    @mod.subcommand(name='ban', description="Bans a user.")
    async def ban(self, interaction:Interaction, member: discord.Member, reason:str=SlashOption(required=False, description="The reason for the ban.")):
        try:
            await member.ban(reason=reason)
            await interaction.send("Banned {}".format(member.mention), ephemeral=True)
        except:
            await interaction.send("Could not kick that user.", ephemeral=True)
        
    @mod.subcommand(name='kick', description="Kicks a user.")
    async def kick(self, interaction:Interaction, member: discord.Member, reason:str=SlashOption(required=False, description="The reason for the ban.")):
        try:
            await member.kick(reason=reason)
            await interaction.send("Kicking {}".format(member.mention), ephemeral=True)
        except:
            await interaction.send("Could not kick that user.", ephemeral=True)
        
        
        
        
    """
    Economy Slash Commands
    """

    @slash_command(name="economy", guild_ids=[guilds])
    async def economy(self, interaction:Interaction):
        """The main economy command."""
        pass
    


    @economy.subcommand()
    @ac.is_owner()
    async def givebal(self, interaction:Interaction, member: discord.Member, amount: int = SlashOption(required=True, description="The amount to give the user.")):
        await add_bal(member, amount)
        await interaction.send(f"added {amount} coins to {member.mention}")

    @economy.subcommand(name="bal", description="Gets the balance of a user.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def balance(self, interaction:Interaction, member: discord.Member=None):
        if member == None:
            member = interaction.user
        await open_account(member)

        db = await sql3.connect('data/bank.sqlite')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM main WHERE member_id = {member.id}")
        result = await cursor.fetchone()

        embed = discord.Embed(color=get_random_color())
        embed.set_author(name=f"{member.name}'s Balance", icon_url=member.avatar.url)
        embed.add_field(name="Wallet", value=f"{result[1]} <:money:964588593068773386>")
        embed.add_field(name="Bank", value=f"{result[2]} <:money:964588593068773386>")
        embed.set_footer(text=f"Requested by {interaction.user}")

        await interaction.send(embed=embed)
        
    @economy.subcommand(name="pay", description="Pays a user.")
    async def pay(self, interaction:Interaction, member: discord.Member, amount: int = SlashOption(required=True, description="The amount to give the user.")):
        await remove_bal(interaction.user, amount)
        await add_bal(member, amount)
        
        
        await interaction.send(f"You paid {amount} <:money:964588593068773386> to {member.mention}")

    @economy.subcommand(name="open", description="Opens an account for a user.")
    async def open(self, interaction:Interaction):
        await open_account(interaction.user)
        await interaction.send(f"Opened an account for {interaction.user.mention}")
        
    @economy.subcommand(name="buy")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def buy(self, interaction:Interaction): 
        pass

    @buy.subcommand(name="food", description="Buy food.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def food(self, interaction:Interaction):
        amount = random.randrange(1, 7)
        possibility = random.randint(1, 25)
        if possibility == 6:
            return await interaction.send(f"Somebody thought you were homeless while eating and gave you the money back!") 
        
        if possibility == 1: 
            amount = random.randint(7, 10)
            await remove_bal(interaction.user, amount)
            return await interaction.send(f"You paid {amount} <:money:964588593068773386> for some soup")
        
        await remove_bal(interaction.user, amount)
        await interaction.send(f"You paid {amount} <:money:964588593068773386> for a loaf of 🍞")
        
    @buy.subcommand(name="drink", description="Buy a drink.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def drink(self, interaction:Interaction):
        amount = random.randrange(1, 7)
        possibility = random.randint(1, 25)
        
        if possibility == 1: 
            amount = random.randrange(1, 2)
            await remove_bal(interaction.user, amount)
            return await interaction.send(f"You paid {amount} <:money:964588593068773386> for 🍼")
        
        await remove_bal(interaction.user, amount)
        await interaction.send(f"You paid {amount} <:money:964588593068773386> for a 🍺")
        
        
        
    @economy.subcommand(name="beg", description="Begs for money.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def beg(self, interaction:Interaction):
        possibility = random.randint(1, 100)
        if possibility == 3:
            return await interaction.send(
                "You begged for coins but recieved a 🩴 instead"
            )
        if possibility == 1: 
            await interaction.send(f"OMG! MRBEAST GAVE YOU **2,000,000** <:money:964588593068773386>\nYOU ARE RICH!")
            await add_bal(interaction.user, 2000000)
            return

        amount = random.randrange(60, 200)

        outcomes = [
            f"You got **{amount}** <:money:964588593068773386>",
            f"Batman gave you **{amount}** <:money:964588593068773386>",
            f"You begged your mom for **{amount}** <:money:964588593068773386>",
            f"John Cena gave you **{amount}** <:money:964588593068773386>",
            f"The Rock gave you **{amount}** <:money:964588593068773386>",
            f"I gave you **{amount}** <:money:964588593068773386>",
            f"The developers gave you **{amount}** <:money:964588593068773386>",
            f"Your computer gave you **{amount}** <:money:964588593068773386>",
            f"You begged your dad for **{amount}** <:money:964588593068773386>",
        ]

        await add_bal(interaction.user, amount)
        await interaction.send(random.choice(outcomes))
        
    @economy.subcommand(name="bankrob", description="Hack a bank.")
    @commands.cooldown(1, 21600, BucketType.user)
    async def bankrob(self, interaction:Interaction):
        if interaction.user.id == 800090448705224714 or 828681034316382218: 
            self.bot.get_command("bankrob").reset_cooldown(interaction)
            
        amount = random.randrange(3500, 5000)
        possibility = random.randint(1, 100)
        if possibility == 1:
            await add_bal(interaction.user, amount)
            await interaction.send(f"You hacked into someones bank and stole **{amount}** <:money:964588593068773386>!")
            return
        
        
        amount_possibility = random.randrange(10000, 100000)
        possibility2 = random.randint(1, 100)
        if possibility2 == 1:
            await interaction.send(f"The police found your IP address and arrested you, but you bailed yourself out for **{amount_possibility}** <:money:964588593068773386>")
            await remove_bal(interaction.user, amount_possibility)
            return
            
        await interaction.send(f"The police found your IP address and arrested you, but you bailed yourself out for **3000** <:money:964588593068773386>")
        await remove_bal(interaction.user, 3000)
        return
    
    @bankrob.error
    async def bankrob_error(self, interaction:Interaction, error): 
        if isinstance(error, commands.CommandError):
            await interaction.send(error)
        
        
    @economy.subcommand(name="removebal")
    @commands.is_owner()
    async def rev(self, interaction, member: discord.Member, amount:int=SlashOption(description="The amount you want to remove from the user's balance.", required=True)): 
        await remove_bal(member, amount)
        await interaction.send(f"added {amount} coins to {member.mention}")
    
    @economy.subcommand(name="dep", description="Deposit money into your bank account.")
    @commands.cooldown(1, 3, BucketType.user)
    async def dep(self, interaction:Interaction, amount:str = SlashOption(description="The amount you want to deposit.", required=True)):
        db = await sql3.connect('data/bank.sqlite')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * from main WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()

        if result[1] == 0:
            return await interaction.send(
                "You have 0 coins in your wallet :|"
            )
        done = False
        if amount == "all" or amount == "max":
            sql = "UPDATE main SET bank = ? WHERE member_id = ?"
            val = (result[2] + result[1], interaction.user.id)
            await interaction.send(f"Successfully deposited **{result[1]}** <:money:964588593068773386>")
            await remove_bal(interaction.user, result[1])  
            done = True
        if not done:
            try:
                amount = int(amount)
            except ValueError:
                return await interaction.send(
                    "Only `integers | max | all` will be excepted as the amount"
                )
            if result[1] < amount:
                return await interaction.send(
                    f"You cannot deposit more than **{result[1]}** <:money:964588593068773386>"
                )
                

            sql = "UPDATE main SET bank = ? WHERE member_id = ?"
            val = (result[2] + amount, interaction.user.id)
            await interaction.send(
                f"Successfully deposited **{amount}** <:money:964588593068773386>"
            )
            await remove_bal(interaction.user, amount)

        await cursor.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()

    @economy.subcommand(name='gamble', description="Gamble your money.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gamble(self, interaction:Interaction, amount: int = SlashOption(description="The amount you want to gamble.", required=True)):
        try:
            amount = int(amount)
        except ValueError:
            self.bot.get_command("gamble").reset_cooldown(interaction)
            return await interaction.send(
                "You have to give an integer small brain"
            )

        if amount < 50:
            self.bot.get_command("gamble").reset_cooldown(interaction)
            return await interaction.send(
                "At least gamble 50 coins ._."
            )

        result = check_bal_greater_than(user=interaction.user, amount=amount)
        if result == False:
            self.bot.get_command("gamble").reset_cooldown(interaction)
            return await interaction.send(
                "Your amount cannot be greater than your balance :|"
            )

        chance = random.randint(1, 4)
        if chance != 3:
            await remove_bal(interaction.user, amount)
            return await interaction.send(
                "You lost the bet!"
            )
        multiplier = random.choice([2, 2.25, 2.5, 1.25, 1.5, 1.75])
        total_wallet = int(amount * multiplier)
        await add_bal(interaction.user, total_wallet)
        await interaction.send(f"You won {total_wallet} <:money:964588593068773386>!")

    @economy.subcommand(name="with", description="Withdraw money from your bank account.")
    async def withdraw(self, interaction:Interaction, amount: int = SlashOption(description="The amount you want to withdraw.", required=True)):
        await open_account(user=interaction.user)
        db = await sql3.connect('data/bank.sqlite')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM main WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()
        if result[2] == 0:
            return await interaction.send(
                "You dont have any balance in your bank :|"
            )
        done = False
        if amount == "max" or amount == "all":
            sql = "UPDATE main SET bank = ? WHERE member_id = ?"
            val = (0, interaction.user.id)
            add_bal(interaction.user, result[2])
            await interaction.send(
                f"You successfully deposited **{result[2]}** <:money:964588593068773386> to your bank!"
            )
            done = True
        
        if not done:
            try:
                amount = int(amount)
            except ValueError:
                return await interaction.send(
                    "Only `integers | max | all` will be accepted"
                )

            if amount >= result[2]:
                sql = "UPDATE main SET bank = ? WHERE member_id = ?"
                val = (0, interaction.user.id)
                await add_bal(interaction.user, result[2])
                await interaction.send(
                    f"You successfully deposited **{result[2]}** <:money:964588593068773386> to your bank!"
                )
            else:
                sql = "UPDATE main SET bank = ? WHERE member_id = ?"
                val = (result[2] - amount, interaction.user.id)
                await add_bal(interaction.user, amount)
                await interaction.send(
                    f"You successfully deposited **{amount}** <:money:964588593068773386> to your bank!"
                )
        
        await cursor.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()

    @economy.subcommand(name='work', description="Work to earn money.")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, interaction:Interaction):
        await open_account(user=interaction.user)
        chance = [1, 4]
        if chance == 2:
            return await interaction.send(
                "You were lazy and got fired from your job!"
            )

        amount = random.randrange(400, 600)
        outcomes = [
            f"You worked in your office for **{amount}** <:money:964588593068773386>",
            f"Your boss was frustrated but you worked for him and got **{amount}** <:money:964588593068773386>",
            f"You begged your boss for **{amount}** <:money:964588593068773386>",
            f"You killed your boss and got **{amount}** <:money:964588593068773386> from his wallet",
            f"You got a promotion! You earned **{amount}** <:money:964588593068773386> today :D"
        ]

        await interaction.send(random.choice(outcomes))
        await add_bal(interaction.user, amount)
    
    
    """
    Help Slash Commands
    """





    # Main Help Commands:

    @slash_command(guild_ids=[guilds])
    async def help(self, interaction:Interaction):
        embed = discord.Embed(
            title=f"{self.bot.user.name} Help",
            description=f"`>help [category]` or `/help [category]` for more information.",
        )
        embed.set_thumbnail(url=f"{self.bot.user.display_avatar}")
        embed.add_field(
            name="Moderation:", value=f"/help moderation", inline=False
        )
        embed.add_field(
            name="Economy:", value=f"/help economy", inline=False
        )
        embed.add_field(
            name="Music:", value=f"/help music", inline=False
        )
        embed.set_footer(
            text=f"Requested by {interaction.user} | Created by: ZxlcaLT#2462 | ",
            icon_url=f"{interaction.user.display_avatar}",
        )

        await interaction.send(embed=embed, ephemeral=True)
        
    @help.subcommand(description="Moderation Help Page")
    async def moderation(self, interaction:Interaction):
        embed = discord.Embed(
            title=f"{self.bot.user.name} Moderation Commands:",
            description=f"Support Server: [Click Here!](https://discord.gg/xA3hBtujg7) || `>help [category]` or `/help [category]` for other information.",
            color=Colour.random()
        )
        for command in self.bot.get_cog("moderation").walk_commands():
            description = command.description
            if not description or description is None or description == "":
                description = "No description"
            embed.add_field(
                name=f"`/{command.name} {command.signature if command.signature is not None else ''}`",
                value=description,
            )
        await interaction.send(embed=embed, ephemeral=True)


    @help.subcommand(description="Economy Help Page")
    async def economy(self, interaction:Interaction):
        embed = discord.Embed(
            title=f"{self.bot.user.name} Economy Commands:",
            description=f"Support Server: [Click Here!](https://discord.gg/xA3hBtujg7) || `>help [category]` or `/help [category]` for other information.",
            color=Colour.random()
        )
        for command in self.bot.get_cog("economy").walk_commands():
            description = command.description
            if not description or description is None or description == "":
                description = "No description"
            embed.add_field(
                name=f"`/{command.name} {command.signature if command.signature is not None else ''}`",
                value=description,
            )
        await interaction.send(embed=embed, ephemeral=True)


    @help.subcommand(description="Music Help Page")
    async def music(self, interaction:Interaction):
        embed = discord.Embed(
            title=f"{self.bot.user.name} Music Commands:",
            description=f"Support Server: [Click Here!](https://discord.gg/xA3hBtujg7) || `>help [category]` or `/help [category]` for other information.",
            color=Colour.random()
        )
        for command in self.bot.get_cog("music").walk_commands():
            description = command.description
            if not description or description is None or description == "":
                description = "No description"
            embed.add_field(
                name=f"`/{command.name} {command.signature if command.signature is not None else ''}`",
                value=description,
            )
        await interaction.send(embed=embed, ephemeral=True)



def setup(bot):
    bot.add_cog(Slash_Commands(bot))
    name = "Slash Commands"
    print(f"Loaded {name}")