from .image import Image
from discord.ext import commands

async def setup(bot: commands.Bot) -> None:
    cog = Image(bot)
    await bot.add_cog(cog)