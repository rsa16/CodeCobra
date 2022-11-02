from discord.ext import commands
import discord
import re
from core.db import database
from systems.moderation.utils import validateMessage

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = database.loadDatabase()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await validateMessage(message)

    