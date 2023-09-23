import asyncio
import datetime
import json

import discord
import stripe
from discord import app_commands
from discord.ext import commands
from util.colormessage import colormsg

with open("config.json", "r") as f:
    config = json.load(f)

stripe.api_key = config["secret_key"]


async def assembleembed(bot, name, price, color):
    try:
        embed = discord.Embed(title=f"Item {name} created", color=color,
                              timestamp=datetime.datetime.now())
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        embed.add_field(name="Item ", value=name)
        embed.add_field(name="Item Price", value=f"{price.unit_amount / 100} USD")
        return embed
    except Exception as e:
        print(e)


async def assemblelistembed(bot,  color):
    embed = discord.Embed(title=f"Item List", color=color,
                          timestamp=datetime.datetime.now())
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    for item in stripe.Product.list():
        if item.active:
            price = stripe.Price.list(product=item.id).data[0]
            embed.add_field(name=f"{item.name} : {item.id}", value=f"{price.unit_amount / 100} USD")
    return embed


def find_prodid(input_list, name):
    try:
        for a in input_list:
            if a[name]:
                return a[name]
    except KeyError: # If name not found in dictionaries, return name param (product id most likely)
        return name


class itemcmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @app_commands.command(name="add-item", description="Command used to create a new item")
    async def additem(self, interaction: discord.Interaction, itemname: str, itemprice: int):
        try:
            item = stripe.Product.create(name=itemname)
            price = stripe.Price.create(
                unit_amount=itemprice * 100,
                currency='usd',
                product=item.id,
            )
            print(colormsg(f"Adding item {itemname} with price {itemprice}"))
            await interaction.response.send_message(
                embed=await assembleembed(self.bot, itemname, price, discord.Color.green()), ephemeral=True)

        except Exception as e:
            print(e)

    @commands.has_permissions(manage_channels=True)
    @app_commands.command(name="remove-item", description="Command used to remove an item")
    async def removeitem(self, interaction: discord.Interaction, itemid: str):
        print(colormsg(f"Removing item {itemid}"))
        try:
            item = stripe.Product.retrieve(itemid)
            prices = stripe.Price.list(product=itemid)
            for price in prices:
                price = stripe.Price.modify(price.id, active=False)
            item = stripe.Product.modify(item.id, active=False)
            await interaction.response.send_message(content=f"Removed item {itemid}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(content=f"Failed to remove item: {str(e)}", ephemeral=True)

    @app_commands.command(name="list-items", description="Command used to list items.")
    async def listItems(self, interaction: discord.Interaction):
        try:
            print(colormsg(f"Listing all Items"))
            await interaction.response.send_message(embed=await assemblelistembed(self.bot, discord.Color.green()), ephemeral=True)
        except Exception as e:
            print(e)

    @app_commands.command(name="buy", description="Command used to buy an item.")
    async def buyitem(self, interaction: discord.Interaction, cartitem: str):
        try:
            itemlist = []
            for item in stripe.Product.list():
                if item.active:
                    iteminfo = {item.name: item.id}  # Item information stored here
                    itemlist.append(iteminfo)

            prod = find_prodid(itemlist, cartitem)
            item = stripe.Product.retrieve(prod)
            price = stripe.Price.list(product=item).data[0]
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price.id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}',
                cancel_url=f'https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}',
            )

            embed = discord.Embed(title="StripeBot",
                                  color=0x00ff00)
            embed.add_field(name="Payment Link", value=f"[here]({session.url})")
            embed.add_field(name="Item", value=f"{item.name}")
            embed.add_field(name="Price", value=f"{price.unit_amount / 100} USD")

            await interaction.response.send_message(embed=embed, ephemeral=True)

            while session.payment_status != "paid":
                await asyncio.sleep(1)
                session = stripe.checkout.Session.retrieve(session.id)
            embed = discord.Embed(title="StripeBot",
                                  description=f"You have paid for ```{item.name}```. Thank you for your purchase!",
                                  color=0x00ff00)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(e)

    @additem.error
    @removeitem.error
    async def onerror(self, interaction: discord.Interaction, error: app_commands.MissingPermissions):
        await interaction.response.send_message(content=error,
                                                ephemeral=True)


async def setup(bot):
    await bot.add_cog(itemcmds(bot))
