import praw
from discord.ext import commands
import discord
import random

class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id="zTZbMgpIkVleOrSGyg4BWA", client_secret="riWUWJhvyZVPyEReof7xbsDEZHaI3Q", user_agent="discord\windows:cgcbot:v1.0.0")

    @commands.command(name="meme", help="Shows a post from a subreddit. The default is r/memes!")
    async def _reddit(self, ctx, subred="memes"):
        message = await ctx.send("Please wait... Fetching them memes :-)")
        subreddit = self.reddit.subreddit(subred)
        all_subs = []

        top = subreddit.hot()
        for submission in top:
            all_subs.append(submission)

        random_sub = random.choice(all_subs)
        name = random_sub.title
        url = random_sub.url

        if random_sub.over_18:
            memeem = discord.Embed(title=name, description=f"From **r/{subred}**", color=0xff387e)
            memeem.set_image(url=url)
            memeem.set_footer(text=f"NSFW - {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=memeem)
        else:
            memeem = discord.Embed(title=name, description=f"From **r/{subred}**", color=0x38d4ff)
            memeem.set_image(url=url)
            memeem.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            memeem.set_footer(text="Hmm... I can't think of anything smart ass to say.", icon_url=ctx.author.avatar.url)
            await message.delete()
            await ctx.send(embed=memeem)