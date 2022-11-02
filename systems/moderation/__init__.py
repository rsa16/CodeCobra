from .automod import AutoMod
from discord.ext import commands

async def setup(bot: commands.Bot) -> None:
    cog = AutoMod(bot)
    await bot.add_cog(cog)