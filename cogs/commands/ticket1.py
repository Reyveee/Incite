import discord
from discord.ext import commands


class hacker1111111111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Tickets commands"""
  
    def help_custom(self):
		      emoji = '<:tickets:1199317358725058671> '
		      label = "Tickets Commands"
		      description = "ticket, transcripts , ticket close, reopen, panel create, panel list, user"
		      return emoji, label, description

    @commands.group()
    async def __tickets__(self, ctx: commands.Context):
        """`ticket`, `ticket transcripts`, `ticket close`, `ticket reopen`, `ticket delete`, `ticket panel create`, `ticket panel delete`, `ticket panel list`, `ticket user`, `ticket user add`, `ticket user remove`"""