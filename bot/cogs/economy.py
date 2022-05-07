import datetime
import os 
import aiofiles
import pickle
import nextcord as discord

import aiosqlite as sql
import urllib
import random
from nextcord.ext import ipc, commands
from nextcord.ext.commands.cooldowns import BucketType





def get_random_color():
    return random.choice([0x4287f5, 0xf54242, 0xf5f242])

async def open_account(user: discord.Member):
    db = await sql.connect('data/bank.sqlite')
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

async def check_bal_greater_than(user: discord.Member, amount: int):
    db = await sql.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * FROM main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    if result[1] >= amount:
        return True
    return False

async def add_bal(user: discord.Member, amount: int):
    db = await sql.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * from main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    sql = f"UPDATE main SET wallet = ? WHERE member_id = ?"
    val = (result[1] + amount, user.id)

    await cursor.execute(sql, val)
    await db.commit()
    await cursor.close()
    await db.close()

async def remove_bal(user: discord.Member, amount: int):
    db = await sql.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * from main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    sql = f"UPDATE main SET wallet = ? WHERE member_id = ?"
    val = (result[1] - amount, user.id)

    await cursor.execute(sql, val)
    await db.commit()
    await cursor.close()
    await db.close() 

async def remove_bank(user: discord.Member, amount: int):
    db = await sql.connect('data/bank.sqlite')
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * from main WHERE member_id = {user.id}")
    result = await cursor.fetchone()

    sql = f"UPDATE main SET bank = ? WHERE member_id = ?"
    val = (result[1] - amount, user.id)

    await cursor.execute(sql, val)
    await db.commit()
    await cursor.close()
    await db.close() 


class economy(commands.Cog, name="economy"):
    """An economy system in the bot"""
    def __init__(self, bot):
        self.bot = bot


        
    @commands.command()
    @commands.is_owner()
    async def givebal(self, ctx, member: discord.Member, amount: int):
        await add_bal(member, amount)
        await ctx.reply(f"added {amount} coins to {member.mention}")

    @commands.command(name="bal", aliases=['balance'], description="Shows a users balance.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def balance(self, ctx, member: discord.Member=None):
        if member == None:
            member = ctx.author
        await open_account(member)

        db = await sql.connect('data/bank.sqlite')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM main WHERE member_id = {member.id}")
        result = await cursor.fetchone()

        embed = discord.Embed(color=get_random_color(), timestamp=ctx.message.created_at)
        embed.set_author(name=f"{member.name}'s Balance", icon_url=member.avatar.url)
        embed.add_field(name="Wallet", value=f"{result[1]} <:money:964588593068773386>")
        embed.add_field(name="Bank", value=f"{result[2]} <:money:964588593068773386>")
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)
        
    @commands.group(name="buy", invoke_without_command=True, description="Buy something.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def buy(self, ctx): 
        pass

    @buy.command(name="food", description="Buy some food")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def food(self, ctx):
        amount = random.randrange(1, 7)
        possibility = random.randint(1, 25)
        if possibility == 6:
            return await ctx.reply(f"Somebody thought you were homeless while eating and gave you the money back!") 
        
        if possibility == 1: 
            amount = random.randint(7, 10)
            await remove_bal(ctx.author, amount)
            return await ctx.reply(f"You paid {amount} <:money:964588593068773386> for some soup")
        
        await remove_bal(ctx.author, amount)
        await ctx.reply(f"You paid {amount} <:money:964588593068773386> for a loaf of 🍞")
        
    @buy.command(name="drink", description="Buy a drink")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def drink(self, ctx):
        amount = random.randrange(1, 7)
        possibility = random.randint(1, 25)
        
        if possibility == 1: 
            amount = random.randrange(1, 2)
            await remove_bal(ctx.author, amount)
            return await ctx.reply(f"You paid {amount} <:money:964588593068773386> for 🍼")
        
        await remove_bal(ctx.author, amount)
        await ctx.reply(f"You paid {amount} <:money:964588593068773386> for a 🍺")
        
    @commands.command(name="pay", description="Pays a user.")
    async def pay(self, ctx, member: discord.Member=None, amount: int=None):
        if amount == None:
            return await ctx.send("You need to specify an amount to pay a user.")
        if member == None:
            return await ctx.send("You need to specify a user to pay.")
        
        await remove_bal(ctx.author, amount)
        await add_bal(member, amount)
        
        
        await ctx.send(f"You paid {amount} <:money:964588593068773386> to {member.mention}")

    @commands.command(name="open", description="Opens an account for a user.")
    async def open(self, ctx:commands.Context):
        await open_account(ctx.author)
        await ctx.send(f"Opened an account for {ctx.author.mention}")
        
    @commands.command(name="beg", description="Beg for money.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def beg(self, ctx):
        possibility = random.randint(1, 100)
        if possibility == 3:
            return await ctx.send(
                "You begged for coins but recieved a 🩴 instead"
            )
        if possibility == 1: 
            await ctx.reply(f"OMG! MRBEAST GAVE YOU **2,000,000** <:money:964588593068773386>\nYOU ARE RICH!")
            await add_bal(ctx.author, 2000000)
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

        await add_bal(ctx.author, amount)
        await ctx.send(random.choice(outcomes))
        
    @commands.command(name="bankrob", description="Hack a bank.")
    @commands.cooldown(1, 21600, BucketType.user)
    async def bankrob(self, ctx):
        if ctx.author.id == 800090448705224714 or 828681034316382218: 
            self.bot.get_command("bankrob").reset_cooldown(ctx)
            
        amount = random.randrange(3500, 5000)
        possibility = random.randint(1, 100)
        if possibility == 1:
            await add_bal(ctx.author, amount)
            await ctx.reply(f"You hacked into someones bank and stole **{amount}** <:money:964588593068773386>!")
            return
        
        
        amount_possibility = random.randrange(10000, 100000)
        possibility2 = random.randint(1, 100)
        if possibility2 == 1:
            await ctx.reply(f"The police found your IP address and arrested you, but you bailed yourself out for **{amount_possibility}** <:money:964588593068773386>")
            remove_bal(ctx.author, amount_possibility)
            return
            
        await ctx.reply(f"The police found your IP address and arrested you, but you bailed yourself out for **3000** <:money:964588593068773386>")
        await remove_bal(ctx.author, 3000)
        return
    
    @bankrob.error
    async def bankrob_error(self, ctx, error): 
        if isinstance(error, commands.CommandError):
            await ctx.reply(error)
        
        
    @commands.command(name="removebal")
    @commands.is_owner()
    async def rev(self, ctx, member: discord.Member, amount:int): 
        await remove_bal(member, amount)
        await ctx.reply(f"added {amount} coins to {member.mention}")
    
    @commands.command(name="dep", aliases=['deposit'], description="Deposit money.")
    @commands.cooldown(1, 3, BucketType.user)
    async def dep(self, ctx, amount):
        db = await sql.connect('data/bank.sqlite')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * from main WHERE member_id = {ctx.author.id}")
        result = await cursor.fetchone()

        if result[1] == 0:
            return await ctx.send(
                "You have 0 coins in your wallet :|"
            )
        done = False
        if amount == "all" or amount == "max":
            sql = "UPDATE main SET bank = ? WHERE member_id = ?"
            val = (result[2] + result[1], ctx.author.id)
            await ctx.send(f"Successfully deposited **{result[1]}** <:money:964588593068773386>")
            await remove_bal(ctx.author, result[1])  
            done = True
        if not done:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send(
                    "Only `integers | max | all` will be excepted as the amount"
                )
            if result[1] < amount:
                return await ctx.send(
                    f"You cannot deposit more than **{result[1]}** <:money:964588593068773386>"
                )
                

            sql = "UPDATE main SET bank = ? WHERE member_id = ?"
            val = (result[2] + amount, ctx.author.id)
            await ctx.send(
                f"Successfully deposited **{amount}** <:money:964588593068773386>"
            )
            await remove_bal(ctx.author, amount)

        await cursor.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(name='gamble', description="Gamble some money.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gamble(self, ctx, amount):
        try:
            amount = int(amount)
        except ValueError:
            self.bot.get_command("gamble").reset_cooldown(ctx)
            return await ctx.send(
                "You have to give an integer small brain"
            )

        if amount < 50:
            self.bot.get_command("gamble").reset_cooldown(ctx)
            return await ctx.send(
                "At least gamble 50 coins ._."
            )

        result = check_bal_greater_than(user=ctx.author, amount=amount)
        if result == False:
            self.bot.get_command("gamble").reset_cooldown(ctx)
            return await ctx.send(
                "Your amount cannot be greater than your balance :|"
            )

        chance = random.randint(1, 4)
        if chance != 3:
            await remove_bal(ctx.author, amount)
            return await ctx.send(
                "You lost the bet!"
            )
        multiplier = random.choice([2, 2.25, 2.5, 1.25, 1.5, 1.75])
        total_wallet = int(amount * multiplier)
        await add_bal(ctx.author, total_wallet)
        await ctx.send(f"You won {total_wallet} <:money:964588593068773386>!")

    @commands.command(name="with", aliases=['withdraw'], description="Withdraw money from your bank")
    async def withdraw(self, ctx, amount: str):
        await open_account(user=ctx.author)
        db = await sql.connect('data/bank.sqlite')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM main WHERE member_id = {ctx.author.id}")
        result = await cursor.fetchone()
        if result[2] == 0:
            return await ctx.send(
                "You dont have any balance in your bank :|"
            )
        done = False
        if amount == "max" or amount == "all":
            sql = "UPDATE main SET bank = ? WHERE member_id = ?"
            val = (0, ctx.author.id)
            add_bal(ctx.author, result[2])
            await ctx.send(
                f"You successfully deposited **{result[2]}** <:money:964588593068773386> to your bank!"
            )
            done = True
        
        if not done:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send(
                    "Only `integers | max | all` will be accepted"
                )

            if amount >= result[2]:
                sql = "UPDATE main SET bank = ? WHERE member_id = ?"
                val = (0, ctx.author.id)
                await add_bal(ctx.author, result[2])
                await ctx.send(
                    f"You successfully deposited **{result[2]}** <:money:964588593068773386> to your bank!"
                )
            else:
                sql = "UPDATE main SET bank = ? WHERE member_id = ?"
                val = (result[2] - amount, ctx.author.id)
                await add_bal(ctx.author, amount)
                await ctx.send(
                    f"You successfully deposited **{amount}** <:money:964588593068773386> to your bank!"
                )
        
        await cursor.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(name='work', description="Work to earn money")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        await open_account(user=ctx.author)
        chance = [1, 4]
        if chance == 2:
            return await ctx.reply(
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

        await ctx.send(random.choice(outcomes))
        await add_bal(ctx.author, amount)
    



def setup(bot):
    bot.add_cog(economy(bot))
    name = "Economy"
    print(f"Loaded {name}")