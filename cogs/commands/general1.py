import discord
from discord.ext import commands


class hacker111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """General commands"""
  
    def help_custom(self):
		      emoji = '<:general_clipboard:1199317349308825670>'
		      label = "General Commands"
		      description = "afk, avatar, banner, servericon, snipe, shorten, urban, hash, rickroll"
		      return emoji, label, description

    @commands.group()
    async def __General__(self, ctx: commands.Context):
        """`afk` , `avatar` , `banner` , `servericon` , `membercount` , `poll` , `hack` , `token` , `users` , `italicize` , `strike` , `quote` , `code` , `bold` , `censor` , `underline` , `gender` , `wizz` , `pikachu` , `shorten` , `urban` , `rickroll` , `hash` , `snipe` , `roleall`"""