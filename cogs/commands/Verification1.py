import discord
from discord.ext import commands


class hacker111111111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Verification commands"""
  
    def help_custom(self):
		      emoji = '<:verify:1199317322054242334>'
		      label = "Verification Commands"
		      description = "verification, verification on, giveroleaftercaptcha"
		      return emoji, label, description

    @commands.group()
    async def __verification__(self, ctx: commands.Context):
        """`verification`, `verification on`, `verification off`, `giveroleaftercaptcha`"""