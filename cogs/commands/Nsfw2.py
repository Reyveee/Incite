import discord
from discord.ext import commands

class hacker11111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Media commands"""
  
    def help_custom(self):
		      emoji = '<:anxMedia:1108780220007333948>'
		      label = "Media Commands"
		      description = "Show You Media Commands"
		      return emoji, label, description

    @commands.group()
    async def __Media__(self, ctx: commands.Context):
        """`media` , `media setup` , `media remove` , `media config` , `media reset`"""