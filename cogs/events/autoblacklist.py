import discord
from core import Astroz, Cog
from discord.ext import commands
from utils.Tools import add_user_to_blacklist, get_db_connection

class AutoBlacklist(Cog):
    def __init__(self, client: Astroz):
      self.client = client
      self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(5, 5, commands.BucketType.member)
      self.spam_command_mapping = commands.CooldownMapping.from_cooldown(6, 10, commands.BucketType.member)

    @commands.Cog.listener()
    async def on_message(self, message):
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (message.author.id,))
      is_blacklisted = cursor.fetchone() is not None
      
      conn.close()
      
      bucket = self.spam_cd_mapping.get_bucket(message)
      astroz = f'<@{self.client.user.id}>'
      retry = bucket.update_rate_limit()

      if retry:
        if message.author.bot or is_blacklisted:
          pass
        elif message.content == astroz or message.content == f"<@!{self.client.user.id}>":
          add_user_to_blacklist(message.author.id)
          embed = discord.Embed(description="**Successfully Blacklisted {}**.\n\nReason: **Spam mentioning me**".format(message.author.mention),color=0x2f3136)
          await message.channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_command(self, ctx):
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (ctx.author.id,))
      is_blacklisted = cursor.fetchone() is not None
      
      conn.close()
      
      bucket = self.spam_command_mapping.get_bucket(ctx.message)
      retry = bucket.update_rate_limit()
      
      if ctx.author.bot or is_blacklisted:
        pass
      elif retry:
        add_user_to_blacklist(ctx.author.id)
        embed = discord.Embed(description="**Successfully blacklisted {}**.\n\nReason: **Spamming my commands**".format(ctx.author.mention),color=0x2f3136)
        await ctx.reply(embed=embed)