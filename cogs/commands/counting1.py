import discord
from discord.ext import commands


class counting1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Counting commands"""
  
    def help_custom(self):
		      emoji = '<:channels:1199720810852659251>'
		      label = "Counting Commands"
		      description = "counting, setchannel, setcount, stats, disablemaths, points, memory-game, leaderboard, removechannel"
		      return emoji, label, description

    @commands.group()
    async def __Counting__(self, ctx: commands.Context):
        """`counting` , `counting setchannel` , `counting setcount` , `counting stats` , `counting removechannel` , `counting disablemaths` , `counting points` , `counting leaderboard`"""