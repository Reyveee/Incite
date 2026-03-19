import discord
from discord.ext import commands


class hacker11111111111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Giveaway commands"""
  
    def help_custom(self):
		      emoji = '<:tada:1199317356334301264>'
		      label = "Giveaway Commands"
		      description = "gw, gstart, gend, greroll"
		      return emoji, label, description

    @commands.group()
    async def __Giveaway__(self, ctx: commands.Context):
        """`gstart`, `gend`, `greroll`"""