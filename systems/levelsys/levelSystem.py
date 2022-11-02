import random
from discord.ext import commands
import discord
import json
from core.db import database
from systems.moderation.utils import validateMessage

LUCK_RANGE = [1, 10]
KARMA = 5
EXPERIENCE_GAIN = 5

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = database.loadDatabase()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_data(member)

    @commands.Cog.listener()
    async def on_message(self, message):
        valid = await validateMessage(message)
        if message.author.bot == False and valid:
            await self.update_data(message.author)
            await self.add_experience(message, EXPERIENCE_GAIN)
            await self.level_up(message.author, message)


    async def update_data(self, user):
        user_ids = database.getColumn("levels", "uuid", self.db)
        if not f'{user.id}' in user_ids:
            print(f"added {user.id}")
            data = {
                "levels": [
                    {
                        "uuid": [str(user.id), "text primary key"],
                        "experience": [0, "integer"],
                        "level": [1, "integer"]
                    }
                ]
            }
            database.updateDb(data, self.db)
            return

    async def add_experience(self, msg: discord.Message, exp):
        print("added experience")
        row = database.getRow("levels", str(msg.author.id), self.db)
        msg_word_amt = len(msg.content.split())
        randomness = (msg_word_amt * random.randint(LUCK_RANGE[0], LUCK_RANGE[1])) // KARMA

        row["experience"] += (exp + randomness)

        database.updateRow("levels", str(msg.author.id), row, self.db)


    async def level_up(self, user, message):
        print("tried to level up")
        row = database.getRow("levels", str(user.id), self.db)
        experience = row['experience']
        lvl_start = row['level']
        lvl_end = int(experience ** (1 / 4))
        if lvl_start < lvl_end:
            await message.channel.send(f'{user.mention} has leveled up to level {lvl_end}')
            row['level'] = lvl_end
        database.updateRow("levels", str(user.id), row, self.db)

    @commands.command(help="what level am i??")
    async def level(self, ctx, member: discord.Member = None):
        if not member:
            id = ctx.message.author.id
            row = database.getRow("levels", str(id), self.db)
            lvl = row['level']
            await ctx.send(f'You are at level {lvl}!')
        else:
            id = member.id
            row = database.getRow("levels", str(id), self.db)
            lvl = row['level']
            await ctx.send(f'{member} is at level {lvl}!')
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)