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

from util.load_extensions import load_extensions

with open("config.json", "r") as f:
    config = json.load(f)

prefix = config["prefix"]
bot_token = config["bot_token"]

bot = commands.Bot(command_prefix=f"{prefix}", intents=discord.Intents.all())


async def main():
    async with bot:
        try:
            await load_extensions(bot)
            print("Bot Ready!")
            await bot.start(bot_token)
        except KeyboardInterrupt:
            pass


asyncio.run(main())  # Runs main function above
