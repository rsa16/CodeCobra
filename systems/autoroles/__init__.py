from .autoroles import AutoRoleSystem
from discord.ext import commands

async def setup(bot: commands.Bot) -> None:
    cog = AutoRoleSystem(bot)
    await bot.add_cog(cog)