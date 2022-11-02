"""
This cog handles giveaways
"""

from calendar import month
from code import interact
from pickle import TRUE
from click import confirm
from discord.ext import commands
import discord
from discord.ui import Modal, TextInput, View
from requests import delete
from sqlalchemy import true
from core.db import database
from core.utils import runTaskAt
from core.views import Confirm
import uuid
import asyncio
from aioscheduler import Manager
from datetime import datetime, timedelta
from typing import Any, Union
import time
import random


InteractionChannel = Union[
        discord.VoiceChannel, discord.StageChannel, discord.TextChannel, discord.ForumChannel, discord.CategoryChannel, discord.Thread, discord.PartialMessageable
    ]

class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduleManager = Manager(5, prefer_utc=False)
        self.loop = asyncio.get_event_loop()
        self.db = database.loadDatabase()
        self.scheduleManager.start()
        self.giveawayChannel = None
        self.runningGiveaways: dict[str, asyncio.Task] = {}

    @commands.command("createGiveaway")
    async def createGiveaway(self, ctx):
        """Create a giveaway interactively with this command."""
        confirmView = GiveConfirm(self)
        await ctx.send("Are you sure you want to create a giveaway?", view=confirmView)
        await confirmView.wait()

    @commands.command(help="get rid of a giveaway")
    async def deleteGiveaway(self, ctx, id_: str):
        info = database.getRow("giveaways", id_, self.db)
        confirmView = Confirm()

        await ctx.send(f"Are you sure you want to delete the giveaway **{info['name']}**?", view=confirmView)
        await confirmView.wait()
        if confirmView.value == None:
            await confirmView.interaction.response.send_message("Couldn't cancel giveaway, something went wrong. Give us time to figure it out!", ephemeral=True)
        elif confirmView.value:
            self.runningGiveaways[id_].cancel()
            if self.giveawayChannel != None:
                announcement = await self.giveawayChannel.fetch_message(info["announcement_id"])
                await announcement.delete()
            await confirmView.interaction.response.send_message(f"Giveaway **{id_}** cancelled.")
        else:
            await confirmView.interaction.response.send_message("Alright! The giveaway will continue as scheduled.", ephemeral=True)

    @commands.command(help="End a specific giveaway (will be rolled at this time)")
    async def endGiveaway(self, ctx, id_: str):
        info = database.getRow("giveaways", id_, self.db)
        confirmView = Confirm()

        await ctx.send(f"Are you sure you want to end the giveaway **{info['name']}**? Just to be sure you know, this is different from cancelling the giveaway and after ending we will immediately roll for the winners.", view=confirmView)
        await confirmView.wait()
        if confirmView.value == None:
            await confirmView.interaction.response.send_message("Couldn't end giveaway, something went wrong. Give us time to figure it out!", ephemeral=True)
        elif confirmView.value:
            await self.rollGiveaway(id_, forceEnd=True)
            await confirmView.interaction.response.send_message(f"Giveaway **{id_}** ended.", ephemeral=True)
        else:
            await confirmView.interaction.response.send_message("Alright! The giveaway will continue as scheduled.", ephemeral=True)

    async def notifyGiveaway(self, channel: InteractionChannel, id_: str):
        info = database.getRow("giveaways", id_, self.db)
        embed = discord.Embed(title=info["name"], description=f"""
        Ends: <t:{int(time.mktime(info["duration"].timetuple()))}:R>
        Hosted By: {info["created_by"]}
        Entries: **0**
        Winners: **{info["winnerCount"]}**
```
{info["desc"]}
```
        Your reward will be: {info["prize"]}
        """, color=0x36393F)

        view = GiveawayJoinView(self, id_)
        self.bot.add_view(view)
        message = await channel.send(embed=embed, view=view)  # type: ignore
        dataToChange = {"announcement_id": f"{message.id}"}
        database.updateRow("giveaways", id_, dataToChange, self.db)

        await view.wait()
        print("Hey")

    @commands.command(help="Set the channel where giveaways should be announced.")
    async def setGiveawayChannel(self, ctx, channel: discord.TextChannel):
        self.giveawayChannel = channel
        await ctx.send("set channel!")

    async def rollGiveaway(self, id_: str, forceEnd=False):
        if forceEnd:
            self.runningGiveaways[id_].cancel()
        info = database.getRow("giveaways", id_, self.db)
        winners = []
        for i in range(int(info["winnerCount"])):
            winner = random.choice(list(filter(None, info["entered_users"].split(","))))
            winners.append(winner)

        newVar: str = info["entered_users"]
        embed = discord.Embed(title=info["name"], description=f"""
        Ended: <t:{int(time.mktime(datetime.now().timetuple()))}:R>
        Hosted By: {info["created_by"]}
        Entries: **{len(newVar.split(","))-1}**
        Winners: {','.join([f"<@{winner}>" for winner in winners])}
```
{info["desc"]}
```
        Your reward is: {info["prize"]}
        """, color=0x36393F)
        
        print("hopp")
        for winner in winners:
            print(winner)
            winner_user = self.bot.get_user(int(winner))
            print("did it work?")
            print("winner user", winner_user)
            print("channel", self.giveawayChannel)
            if self.giveawayChannel != None:
                print("wtf")
                annoucement = await self.giveawayChannel.fetch_message(info["announcement_id"])
                print("wtff")
                view = discord.ui.View()
                print("wtfff")
                view.add_item(discord.ui.Button(label="Giveaway ended...", disabled=True))
                print("wtffff")
                await annoucement.edit(embed=embed, view=view)
                print("wtffff")
                await self.giveawayChannel.send(f"Congrautlations <@{winner}>! You've won yourself some **{info['prize']}**! Please DM rsa16#9311 to claim your reward.")  # type: ignore

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

    
class GiveawayJoinView(discord.ui.View):
    def __init__(self, cog: Giveaway, uuid: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.uuid = uuid

    @discord.ui.button(label="Join Giveaway!", style=discord.ButtonStyle.grey, custom_id="giveawayjoin:btn")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        info: dict[str, Any] = database.getRow("giveaways", self.uuid, self.cog.db)
        if (str(interaction.user.id) not in info["entered_users"]):
            info["entered_users"] += (str(interaction.user.id) + ',')
            
            database.updateRow("giveaways", self.uuid, info, self.cog.db)
            print("prize is: " + info["prize"])

            allEntered = info["entered_users"].split(",")
            # change number of entries
            embed = discord.Embed(title=info["name"], description=f"""
            Ends: <t:{int(time.mktime(info["duration"].timetuple()))}:R>
            Hosted By: {info["created_by"]}
            Entries: **{len(allEntered)-1}**
            Winners: **{info["winnerCount"]}**
```
{info["desc"]}
```
            Your reward will be: {info["prize"]}
            """, color=0x36393F)
            if self.cog.giveawayChannel != None:
                annoucementChannel = await self.cog.giveawayChannel.fetch_message(info["announcement_id"])
                await annoucementChannel.edit(embed=embed)

            # send interaction response
            await interaction.response.send_message("You just joined a giveaway!", ephemeral=True)
        else:
            info["entered_users"] = info["entered_users"].replace(str(interaction.user.id) + ',', "")

            allEntered = info["entered_users"].split(",")
            # change number of entries
            embed = discord.Embed(title=info["name"], description=f"""
            Ends: <t:{int(time.mktime(info["duration"].timetuple()))}:R>
            Hosted By: {info["created_by"]}
            Entries: **{len(allEntered)-1}**
            Winners: **{info["winnerCount"]}**
```
{info["desc"]}
```
            Your reward will be: {info["prize"]}
            """, color=0x36393F)

            view = discord.ui.View()

            class LeaveBtn(discord.ui.Button):
                def __init__(self, uuid, cog):
                    super().__init__(label="Leave Giveaway", style=discord.ButtonStyle.red)
                    self.uuid = uuid
                    self.cog = cog

                async def callback(self, interaction: discord.Interaction):
                    self.view.stop()
                    database.updateRow("giveaways", self.uuid, info, self.cog.db)
                    if self.cog.giveawayChannel != None:
                        annoucementChannel = await self.cog.giveawayChannel.fetch_message(info["announcement_id"])
                        await annoucementChannel.edit(embed=embed)
                    await interaction.response.send_message("Giveaway left.")

            view.add_item(LeaveBtn(self.uuid, self.cog))
            await interaction.response.send_message("You're already in this giveaway! Leave?", view=view, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception, item) -> None:
        print(error)
        await interaction.response.send_message("Oops... something went wrong when clicking this button. Let us investigate!", ephemeral=True)


# Define a simple View that gives us a confirmation menu
class GiveConfirm(discord.ui.View):
    def __init__(self, cog: Giveaway):
        super().__init__()
        self.cog = cog

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("hello")
        await interaction.response.send_modal(GiveawayModal(self.cog))
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='No', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling...', ephemeral=True)
        self.stop()

class GiveawayModal(discord.ui.Modal, title='Create Giveaway'):
    def __init__(self, cog: Giveaway):
        super().__init__()
        self.cog = cog

    giveawayDuration = discord.ui.TextInput(
        label='Giveaway Duration',
        placeholder='Ex: 5m, 10h, 30d, 1mo, 2y, 3w',
        default="1m"
    )

    winnerCount = discord.ui.TextInput(
        label='Amount Of Possible Winners',
        default="1"
    )

    giveawayName = discord.ui.TextInput(
        label="Name of giveaway",
        default="test"
    )

    prize = discord.ui.TextInput(
        label='prize',
        default="nitro"
    )

    description = discord.ui.TextInput(
        label='description',
        default="get nitro"
    )

    async def on_submit(self, interaction: discord.Interaction):
        id = uuid.uuid4()
        delta = timedelta()
        durationValue = self.giveawayDuration.value

        # calculate time delta
        if durationValue.endswith("m"):
            delta = timedelta(minutes=float(self.giveawayDuration.value[:1]))
        elif durationValue.endswith("h"):
            delta = timedelta(hours=float(self.giveawayDuration.value[:1]))
        elif durationValue.endswith("d"):
            delta = timedelta(days=float(self.giveawayDuration.value[:1]))
        elif durationValue.endswith("mo"):
            delta = timedelta(days=float(self.giveawayDuration.value[:1]) * 30)
        elif durationValue.endswith("y"):
            delta = timedelta(days=float(self.giveawayDuration.value[:1]) * 365)
        elif durationValue.endswith("w"):
            delta = timedelta(weeks=float(self.giveawayDuration.value[:1]))
        elif durationValue.endswith("s"):
            delta = timedelta(seconds=float(self.giveawayDuration.value[:1]))

        duration = datetime.now() + delta

        table = {
            "giveaways": [
                {
                    "uuid": [str(id), "text"],
                    "name": [self.giveawayName.value, "text"],
                    "duration": [duration, "timestamp"],
                    "winnerCount": [self.winnerCount.value, "integer"],
                    "prize": [self.prize.value, "text"],
                    "desc": [self.description.value, "text"],
                    "created_by": [interaction.user.mention, "text"],
                    "entered_users": ['', "text"],
                    "announcement_id": ['', "text"]
                }
            ]
        }

        database.updateDb(table, self.cog.db)
        await interaction.response.send_message(f"You just created a giveaway! This is the ID in case you need it: `{str(id)}`", ephemeral=True)
        if (interaction.channel != None):
            self.cog.loop.create_task(self.cog.notifyGiveaway(interaction.channel, str(id)))

        task = self.cog.loop.create_task(reward(delta, self.cog, id))
        self.cog.runningGiveaways.update({str(id): task})

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        print(error)
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        

async def reward(dt, cog, id_):
    await asyncio.sleep(dt.total_seconds())
    await cog.rollGiveaway(str(id_))

      

