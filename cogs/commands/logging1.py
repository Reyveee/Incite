import discord
from discord.ext import commands

class hacker11111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Raidmode commands"""
  
    def help_custom(self):
		      emoji = '<:alert:1199317330790993960>'
		      label = "Raidmode Commands"
		      description = "automod, antispam, antilink, logging, serverlog, moderatorlog, logall"
		      return emoji, label, description

    @commands.group()
    async def __Raidmode__(self, ctx: commands.Context):
        """`automod` , `automod antispam on` , `automod antispam off` , `automod antilink off` ,  `automod antilink on` , `automod whitelist add` , `automod whitelist remove`, `automod whitelist list`, `automod whitelist reset`, `automod punishment set` , `automod punishment show`

        **__Antiraid__**
        `antiraid` , `antiraid enable` , `antiraid disable` , `antiraid age` , `antiraid nopfp` , `antiraid config` , `antiraid massban` , `antiraid logs` , `antiraid removelogs` , `antiraid punishment`

        **__Logging__**
        `logging`, `logging messages`, `logging members`, `logging server`, `logging channels`, `logging roles`, `logging mod`, `logging all on`, `logging all off`"""