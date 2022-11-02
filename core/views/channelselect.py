from code import interact
import discord

# Define a simple View that gives us a confirmation menu
class ChannelSelect(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.channel = None
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Embed should be posted in...")  # type: ignore
    async def channelSelect(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        self.channel = select.values[0].fetch()
        await interaction.response.defer()
        self.stop()

