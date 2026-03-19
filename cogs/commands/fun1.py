import discord
from discord.ext import commands


class hacker111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Fun commands"""
  
    def help_custom(self):
		      emoji = '<:fun:1199317334532309084>'
		      label = "Fun Commands"
		      description = "tickle, slap, howgay, slots, meme, memory-game, chess, typerace"
		      return emoji, label, description

    @commands.group()
    async def __Fun__(self, ctx: commands.Context):
        """**__Fun__**
        ` tickle` , `kiss` , `hug` , `slap` , `pat` , `feed` , `pet` , `howgay` , `slots` , ` penis` , `meme` , `cat` , `iplookup`"""