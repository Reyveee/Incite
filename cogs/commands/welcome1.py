import discord
from discord.ext import commands


class hacker11111111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Welcome commands"""
  
    def help_custom(self):
		      emoji = '<:wave:1199317327091597373>'
		      label = "Welcomer Commands"
		      description = "greet, autoroles bots, humans, welcome channel, auto reset, embed, image"
		      return emoji, label, description

    @commands.group()
    async def __Welcomer__(self, ctx: commands.Context):
        """`greet` , `greetdel` , `autorole bots add` , `autorole bots remove` , `autorole bots` , `autorole config` , `autorole humans add` , `autorole humans remove` , `autorole humans` , `autorole reset all` , `autorole reset bots` , `autorole reset humans` , `autorole reset` , `autorole`, `welcome autodel` , `welcome channel add` , `welcome channel remove`, `welcome channel` , `welcome embed` , `welcome image` , `welcome message` , `welcome footer` , `welcome ping` , `welcome test` , `welcome thumbnail`"""