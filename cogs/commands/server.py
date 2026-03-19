import discord
from discord.ext import commands

class hacker11111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Welcome commands"""
  
    def help_custom(self):
		      emoji = '<:globe:1199317341129949234>'
		      label = "Server Commands"
		      description = "setup staff, role, vanity roles,, sticky, unsticky, autorespond"
		      return emoji, label, description

    @commands.group()
    async def __Server__(self, ctx: commands.Context):
        """`setup` , `setup staff` , `setup girl` , `setup friend` , `setup vip` , `setup guest` , `setup config` , `staff` , `girl` , `friend` , `vip` , `guest` , `remove staff` , `remove girl` , `remove friend` , `remove vip` , `remove guest` , `sticky`, `unsticky`, `stickylist`, `autorespond` , `autorespond create` , `autorespond delete` , `autorespond edit` , `autorespond config`, `vanityroles setup` , `vanityroles show` , `vanityroles reset`"""

