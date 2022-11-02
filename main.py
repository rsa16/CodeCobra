from discord.ext.commands import Bot
import discord
from dotenv import load_dotenv
import os
import asyncio
import json
from commands.help import Help

# set intents
intents = discord.Intents.default()
intents.message_content = True

# create bot
bot = Bot(command_prefix='-', intents=intents)
bot.help_command = Help()

# helper func
async def load_extensions(bot: Bot) -> None:
    await bot.load_extension("systems.giveaway")
    await bot.load_extension("commands.image")
    await bot.load_extension("systems.moderation")
    await bot.load_extension("commands.custom")
    await bot.load_extension("systems.levelsys")
    await bot.load_extension("systems.autoroles")

# main
async def main():
    await load_extensions(bot)

    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN != None:
        await bot.start(TOKEN)

asyncio.run(main())