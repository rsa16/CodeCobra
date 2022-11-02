import discord
import re

async def validateMessage(message: discord.Message):
        role = discord.utils.get(message.guild.roles, name="Member") # type: ignore
        if re.match(r"(https?:\/\/)?(www.)?(discord.(gg|io|me|li)|discordapp.com\/invite)\/[^\s/]+?(?=\b)", message.content):
            if role in message.author.roles:  # type: ignore
                await message.delete()
                return False
        
        if len(message.content.split()) >= 100:
            await message.delete()
            await message.author.send("Please do not send extremely long messages!")
            return False
        
        return True