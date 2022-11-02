from discord.ext import commands
import discord

YT_QUERIES = [["youtube", "channel"], ["yt", "server"], ["yt", "channel"]]
MEMBER_COUNT_QUERIES = [["how many", "people"], ["amount of", "members"]]
OWNER_QUERIES = [["who", "owner"]]
FOUNDER_QUERIES = [["who", "founder"]]
BOT_CREATOR_QUERIES = [["who", "made", "bot"]]

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: #if message's author is a bot, then ignore it.
            return

        view = discord.ui.View()
        for query in YT_QUERIES:
            if -1 not in [message.content.find(squery) for squery in query]:
                view.add_item(discord.ui.Button(label="Click here!", style=discord.ButtonStyle.blurple, url="https://www.youtube.com/channel/UCP9wWgR7M82vClGwEsaFjWA"))
                await message.channel.send("Are you looking for the server's youtube channel? If you are:", view=view)
                return

        for query in MEMBER_COUNT_QUERIES:
            if -1 not in [message.content.find(squery) for squery in query]:
                if message.guild != None and message.guild.member_count != None:
                    await message.channel.send(f"If you're curious, the server has **{message.guild.member_count}** {'member' if message.guild.member_count <= 1 else 'members'}'")
                return

        for query in OWNER_QUERIES:
            if -1 not in [message.content.find(squery) for squery in query]:
                await message.channel.send("The current server owner is <@817434098829230110>.")
                return

        for query in FOUNDER_QUERIES:
            if -1 not in [message.content.find(squery) for squery in query]:
                await message.channel.send("The current server founder (he gave his owner status away as he is not active anymore) is <@752446932571521075>.")
                return

        for query in BOT_CREATOR_QUERIES:
            if -1 not in [message.content.find(squery) for squery in query]:
                await message.channel.send("The person who made this bot is <@457211156621295616>!")
                return

    @commands.command(help="the server has a yt channel??")
    async def serverChannel(self, ctx):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Click here!", style=discord.ButtonStyle.blurple, url="https://www.youtube.com/channel/UCP9wWgR7M82vClGwEsaFjWA"))
        await ctx.send("Are you looking for the server's youtube channel? If you are:", view=view)

    @commands.command(help="imagine counting the members by hand? couldn't be me")
    async def memberCount(self, ctx):
        if ctx.guild != None and ctx.guild.member_count != None:
            await ctx.send(f"If you're curious, the server has **{ctx.guild.member_count}** {'member' if ctx.guild.member_count <= 1 else 'members'}'")

    @commands.command(help="i really wonder who that owner is...")
    async def owner(self, ctx):
        await ctx.send("Server owner is currently <@817434098829230110> and the creator of this bot is <@457211156621295616>!")

    @commands.command(help="what's the difference between owner and founder..")
    async def founder(self, ctx):
        await ctx.send("Server founder is currently <@752446932571521075> and the creator of this bot is <@457211156621295616>!")

        

        


