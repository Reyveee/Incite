import discord
from discord.ext import commands


class hacker111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Moderation commands"""
  
    def help_custom(self):
		      emoji = '<:hammer:1199317344820920433>'
		      label = "Moderation Commands"
		      description = "snipe, roleicon kick, ban, purge, mute, warn, clone, nick, hide, role, clear"
		      return emoji, label, description

    @commands.group()
    async def __Moderation__(self, ctx: commands.Context):
        """`purge` , `purge contains` , `purge startswith` , `purge invites` , `purge user` , `mute` , `unmute` , `kick` , `warn` , `ban` , `unban` , `clone` , `nick` , `slowmode` ,  `unslowmode` , `roleicon` ,  `clear` , `clear all` , `clear bots` , `clear embeds` , `clear files` , `clear mentions` , `clear images` , `clear contains` , `clear reactions` , `nuke` , `lock` , `unlock` , `hide` , `unhide` , `hideall` , `unhideall` , `audit` , `sticker` , `emojisearch` , `stickersearch` , `role` , `role temp` , `role remove` , `role delete` , `role create` , `role rename` , `enlarge` , `role humans` , `role tokens` , `role bots` , `make embed`"""