from .levelSystem import LevelSystem
from discord.ext import commands

async def setup(bot: commands.Bot) -> None:
    cog = LevelSystem(bot)
    await bot.add_cog(cog)