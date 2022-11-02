from typing import Any
from discord.ext import commands
import discord
from sqlalchemy import desc

class Help(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        """
        This is triggered when !help is invoked.

        This example demonstrates how to list the commands that the member invoking the help command can run.
        """
        # filtered = await self.filter_commands(self.context.bot.commands, sort=True) # returns a list of command objects
        # names = [command.name for command in filtered] # iterating through the commands objects getting names
        # available_commands = "\n".join(names) # joining the list of names by a new line
        # embed  = discord.Embed(description=available_commands)
        # await self.context.send(embed=embed)

        self.pageNumber = 0
        commandsPerPage = (3, 3) # 3 rows, and 3 columns
        commandsPerPageNum = commandsPerPage[0] * commandsPerPage[1]
        commandNum = len(self.context.bot.commands)

        self.totalPages = commandNum / (commandsPerPageNum)

        if int(self.totalPages) != self.totalPages and isinstance(self.totalPages, float):
            self.totalPages = int(self.totalPages)+1

        print(self.totalPages)
        
        allCommandsFirstPage = discord.Embed(
            title="All CodeCobra Commands",
            description=f"""
            Total Commands: **{commandNum}**
            ```diff
- [] = optional argument
- <> = required argument
+ Type >help [category] for more help on a specific category!
+ Alternatively, type >help [command] for more help on a specific command!```
**Categories**
```yaml
- Image, Moderation, Giveaways, Levels, Custom Commands
```
            [Support](https://youtube.com)  |  [Vote](https://youtube.com)  |  [Invite](https://dsc.gg/bluecobra)  |  [Website](https://youtube.com)
            """,
            color=0x37393F
        )
        allCommandsFirstPage.set_footer(text=f"Page {self.pageNumber+1}/{self.totalPages+1}")
        view = HelpView(self)
        msg = await self.context.send(embed=allCommandsFirstPage, view=view)
        view.message = msg  # type: ignore

    async def send_command_help(self, command):
        """This is triggered when !help <command> is invoked."""
        embed = discord.Embed(title=f"{self.context.prefix}{command.name} help", description=f"""
        **Description**
        ```{command.help}```
        **Usage**
        ```{self.context.prefix}{command.name} {command.signature}```
        """)
        embed.set_footer(text="Usage Syntax: <required> [optional]")
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        """This is triggered when !help <group> is invoked."""
        await self.context.send("This is the help page for a group command")

    async def send_cog_help(self, cog):
        """This is triggered when !help <cog> is invoked."""
        await self.context.send("This is the help page for a cog")

    async def send_error_message(self, error):
        """If there is an error, send a embed containing the error."""
        channel = self.get_destination() # this defaults to the command context channel
        await channel.send(error)

class HelpView(discord.ui.View):
    def __init__(self, ctx: Help):
        super().__init__(timeout=None)
        self.context = ctx
        self.newEmbed = None
        self.message: discord.Message = None

    async def refresh(self):
        ctx = self.context
        if ctx.pageNumber != 0:
            nextPageEmbed = discord.Embed(title="All CodeCobra Commands")
            filteredCommands = await ctx.filter_commands(ctx.context.bot.commands, sort=True)  # type: ignore
            commandsToShow = filteredCommands[(ctx.pageNumber-1)*9:ctx.pageNumber*9]

            i = 1
            for command in commandsToShow:
                nextPageEmbed.add_field(name=command.name, value=command.help, inline=False)
                i += 1
        
            nextPageEmbed.set_footer(text=f"Page {ctx.pageNumber+1}/{ctx.totalPages+1}")
            self.newEmbed = nextPageEmbed
            await self.message.edit(embed=self.newEmbed, view=self)
        else:
            allCommandsFirstPage = discord.Embed(
                title="All CodeCobra Commands",
                description=f"""
                Total Commands: **{len(ctx.context.bot.commands)}**
                ```diff
- [] = optional argument
- <> = required argument
+ Type >help [category] for more help on a specific category!
+ Alternatively, type >help [command] for more help on a specific command!```
**Categories**
```yaml
- Stuff
```
                [Support](https://youtube.com)  |  [Vote](https://youtube.com)  |  [Invite](https://dsc.gg/bluecobra)  |  [Website](https://youtube.com)
                """,
                color=0x37393F
            )
            allCommandsFirstPage.set_footer(text=f"Page {ctx.pageNumber+1}/{ctx.totalPages+1}")
            newView = HelpView(ctx)
            newView.message = self.message

            await self.message.edit(embed=allCommandsFirstPage, view=newView)

    @discord.ui.button(label='<<', style=discord.ButtonStyle.blurple)
    async def firstPage(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = self.context
        print("this workking???")
        ctx.pageNumber = 0
        await interaction.response.defer()
        await self.refresh()

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def prevPage(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = self.context
        if ctx.pageNumber != 0:
            ctx.pageNumber -= 1
        else:
            ctx.pageNumber = ctx.totalPages  # type: ignore

        await interaction.response.defer()
        await self.refresh()

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def nextPage(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = self.context
        if ctx.pageNumber != ctx.totalPages:
            ctx.pageNumber += 1
        else:
            await self.firstPage.callback(interaction)
        await interaction.response.defer()
        await self.refresh()

    @discord.ui.button(label='>>', style=discord.ButtonStyle.blurple)
    async def lastPage(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = self.context
        ctx.pageNumber = ctx.totalPages  # type: ignore
        await interaction.response.defer()
        await self.refresh()

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item[Any], /) -> None:
        print(error)