from discord.ext import commands
from util.colormessage import colormsg


class onready(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.bot.wait_until_ready()
            print(colormsg(f"Logged in as {self.bot.user}"))
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(onready(bot))
