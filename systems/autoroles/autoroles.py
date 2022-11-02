from code import interact
from discord.ext import commands
import discord
from core.db import database
from core.views import ChannelSelect, RoleSelect

class AutoRoleSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.db = database.loadDatabase()
        self.bot = bot

    @commands.command()
    async def createAutoRole(self, ctx):
        view = discord.ui.View()
        btn = discord.ui.Button(label="Create Auto Role")
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_modal(AutoRoleCreate())
        btn.callback = callback
        view.on_error = self.on_error

        view.add_item(btn)
        await ctx.send("Click the button below to create a role!", view=view)
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

    async def on_error(self, interaction: discord.Interaction, error: Exception, item) -> None:
        print(error)
        await interaction.response.send_message("Oops... something went wrong when clicking this button. Let us investigate!", ephemeral=True)

class AutoRoleCreate(discord.ui.Modal, title="Create Auto Roles"):
    embed_title = discord.ui.TextInput(
        label="What do you autorole embed to be titled?", 
        required=True
    )

    embed_desc = discord.ui.TextInput(
        label="What do you want the auto roles to be?",
        required=True,
        style = discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        view = ChannelSelect()
        roleview = RoleSelect()

        await interaction.response.send_message("What channel would you like the auto role to posted in?", view=view)
        await view.wait()

        await interaction.response.send_message(f"Alright then. We'll post it in {view.channel}. What roles do you want to autorole? (You can't have more than 25 at once by the way)", view=roleview)
        await roleview.wait()

        roles = '\n'.join([f"{numWithRole[0]}. {numWithRole[1].name}" for numWithRole in enumerate(roleview.roles)])
        print(roles)



        