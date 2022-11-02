import discord

# Define a simple View that gives us a confirmation menu
class RoleSelect(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.roles: list[discord.Role] = []
    
    @discord.ui.select(cls=discord.ui.RoleSelect, max_values=25, placeholder="Roles to autorole")  # type: ignore
    async def channelSelect(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        self.roles = select.values
        await interaction.response.defer()
        self.stop()

