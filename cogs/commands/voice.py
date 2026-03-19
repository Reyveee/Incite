import discord
from discord.ext import commands


class hacker1111111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Voice commands"""
  
    def help_custom(self):
		      emoji = '<:voice:1199317325309030440>'
		      label = "Voice Commands"
		      description = "voice kick, voice muteall, unmute, deafen, vcroles, humans, reset"
		      return emoji, label, description

    @commands.group()
    async def __Voice__(self, ctx: commands.Context):
        """**__Voice__**
        `voice` , `voice kick` , `voice kickall` , `voice mute` , `voice muteall` , `voice unmute` , `voice unmuteall` , `voice deafen` , `voice deafenall` , `voice undeafen` , `voice undeafenall` , `voice moveall`
        
        **__VC autorole__**
        `vcrole bots add` , `vcrole bots remove` , `vcrole bots` , `vcrole config` , `vcrole humans add` , `vcrole humans remove` , `vcrole humans` , `vcrole reset` , `vcrole`"""