import discord
from discord.ext import commands


class hacker1111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Automoderation commands"""
  
    def help_custom(self):
		      emoji = '<:hammer:1199317344820920433>'
		      label = "Automoderation Commands"
		      description = "Show You Automoderation Commands"
		      return emoji, label, description

    @commands.group()
    async def __Automoderation__(self, ctx: commands.Context):
        """`automod` , `antispam on` , `antispam off` , `antilink off` ,  `antilink on`"""