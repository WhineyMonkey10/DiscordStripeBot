import discord
from discord.ext import commands
import stripe
import os
import json
import requests
import click
import asyncio
import InquirerPy
import colorama

with open("config.json", "r") as f:
    config = json.load(f)

stripe.api_key = config["secret_key"]

prefix = config["prefix"]
bot_token = config["bot_token"]

bot = commands.Bot(command_prefix=f"{prefix} ", intents=discord.Intents.all())

stripebotMessage = lambda message: print(
    f"{colorama.Fore.WHITE}[{colorama.Fore.GREEN}StripeBot{colorama.Fore.WHITE}] {colorama.Fore.CYAN}{message}{colorama.Fore.WHITE}")


@bot.event
async def on_ready():
    print(stripebotMessage(f"Logged in as {bot.user}"))


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(prefix):
        await bot.process_commands(message)
    else:
        return


@bot.command()
async def addItem(ctx, name, price):
    stripebotMessage(f"Adding item {name} with price {price}")
    price = int(price)

    try:
        item = stripe.Product.create(name=name)
        price = stripe.Price.create(
            unit_amount=price * 100,
            currency='usd',
            product=item.id,
        )

        await ctx.send(
            f"Added item {name} with price {price.unit_amount / 100} USD. Item ID: {item.id}, Price ID: {price.id}")
    except Exception as e:
        await ctx.send(f"Failed to add item: {str(e)}")


@bot.command()
async def removeItem(ctx, itemID):
    stripebotMessage(f"Removing item {itemID}")
    try:
        item = stripe.Product.retrieve(itemID)
        prices = stripe.Price.list(product=itemID)
        for price in prices:
            price = stripe.Price.modify(price.id, active=False)
        item = stripe.Product.modify(item.id, active=False)
        await ctx.send(f"Removed item {itemID}")
    except stripe.error.StripeError as e:
        await ctx.send(f"Failed to remove item: {str(e)}")


@bot.command()
async def listItems(ctx):
    try:
        for item in stripe.Product.list():
            if item.active:
                await ctx.send(f"Item: {item.name}, ID: {item.id}")
    except stripe.error.StripeError as e:
        await ctx.send(f"Failed to list items: {str(e)}")


def find_prodid(input_list, name):
    try:
        for a in input_list:
            if a[name]:
                #print(a[name])
                return a[name]
    except KeyError: # If name not found in dictionaries, return name param (product id most likely)
        #print(f"Error: {name}")
        return name


@bot.command()
async def buy(ctx):
    try:
        embed = discord.Embed(title="StripeBot",
                              description="Please select an item to buy. Once you've selected your item, just send a message with the item's ID.",
                              color=0x00ff00)
        itemlist = []
        for item in stripe.Product.list():
            iteminfo = {item.name: item.id}  # Item information stored here
            itemlist.append(iteminfo)
            if item.active:
                embed.add_field(name=item.name, value=f"ID: {item.id}")
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await bot.wait_for("message", check=check)
        itemID = msg.content  # Item Name
        prod = find_prodid(itemlist, itemID)
        item = stripe.Product.retrieve(prod)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': stripe.Price.list(product=item).data[0].id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}',
            cancel_url=f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}',
        )
        message = await ctx.send(
            f"Please pay for your item [here]({session.url}). I will automatically mark your item as paid once you have paid.")

        while session.payment_status != "paid":
            await asyncio.sleep(1)
            session = stripe.checkout.Session.retrieve(session.id)
        embed = discord.Embed(title="StripeBot",
                              description=f"You have paid for ```{item.name}```. Thank you for your purchase!",
                              color=0x00ff00)
        await message.edit(content="", embed=embed)
    except stripe.error.StripeError as e:
        await ctx.send(f"Failed to buy item: {str(e)}")


bot.run(bot_token)
