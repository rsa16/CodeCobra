from .giveaway import Giveaway
from discord.ext import commands

async def setup(bot: commands.Bot) -> None:
    cog = Giveaway(bot)
    await bot.add_cog(cog)