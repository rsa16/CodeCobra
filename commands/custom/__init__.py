from .customCmds import CustomCommands
from discord.ext import commands

async def setup(bot: commands.Bot) -> None:
    cog = CustomCommands(bot)
    await bot.add_cog(cog)