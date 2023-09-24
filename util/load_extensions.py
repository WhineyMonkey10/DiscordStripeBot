import os


async def load_extensions(bot):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"Loading cog: {filename[:-3]}")
            await bot.load_extension(f"cogs.{filename[:-3]}")
