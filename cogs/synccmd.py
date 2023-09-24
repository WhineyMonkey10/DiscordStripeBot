import discord
from discord.ext import commands


class bcommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sync", description="Command to sync slash commands")
    async def reload(self, ctx) -> None:
        try:
            tagged = ctx.message.mentions
            if tagged[0].id == self.bot.user.id:
                if ctx.message.author.id == 228674682889437184 or 712640311519608943:
                    print(f"Syncing commands")
                    await self.bot.tree.sync()
                    await ctx.send(f"Commands synced")
                    print(f"Commands synced")
                else:
                    await ctx.send(f"You can't run this command.")
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(bcommands(bot))
