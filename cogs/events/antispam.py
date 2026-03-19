import discord
from discord.ext import commands
import datetime
import re
import json
from core import Astroz, Cog
from utils.Tools import getConfig


class AntiSpam(Cog):
    def __init__(self, client: Astroz):
        self.client = client
        self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(4, 7, commands.BucketType.member)
        self.spam_punish_cooldown_cd_mapping = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.member)

    @commands.Cog.listener()    
    async def on_message(self, message):
      if not message.guild or message.author.bot:
        return
      
      mem = message.author
      invite_regex = re.compile(r"(?:https?://)?(?:www\.)?(?:discord(?:app)?\.(?:com/invite|gg)|dsc\.gg)/[a-zA-Z0-9]+/?")
      link_regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
      
      invite_matches = invite_regex.findall(message.content)
      link_matches = link_regex.findall(message.content)
      
      data = getConfig(message.guild.id)
      antiSpam = data["antiSpam"]
      antiLink = data["antiLink"]
      wled = data["whitelisted"]
      whitelisted_roles = data.get("whitelisted_roles", [])
      whitelisted_channels = data.get("whitelisted_channels", [])
      
      hacker = message.guild.get_member(message.author.id)
      
      is_exempt = False
      if (mem.guild_permissions.administrator or 
          str(message.author.id) in wled or 
          str(message.channel.id) in whitelisted_channels):
          is_exempt = True
      
      if not is_exempt and whitelisted_roles:
          for role_id in whitelisted_roles:
              if message.guild.get_role(int(role_id)) in hacker.roles:
                  is_exempt = True
                  break
      
      try:
          if antiSpam is True and not is_exempt:
              bucket = self.spam_cd_mapping.get_bucket(message)
              retry = bucket.update_rate_limit()

              if retry:
                  punishment = data["punishment"]
                  if punishment == "kick":
                      await message.author.kick(reason="Incite | Anti Spam")
                      hacker = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully kicked {message.author.mention} for spamming.")
                      #hacker.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker.set_footer(text="Automod punishment: Kick")
                      await message.channel.send(embed=hacker, delete_after=5)

                  elif punishment == "ban":
                      await message.author.ban(reason="Incite | Anti Spam")
                      hacker1 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully banned {message.author.mention} for spamming.")
                      #hacker1.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker1.set_footer(text="Automod punishment: Ban")
                      await message.channel.send(embed=hacker1, delete_after=5)

                  else:  # Default to timeout if punishment is "none" or invalid
                      now = discord.utils.utcnow()
                      await message.author.timeout(now + datetime.timedelta(minutes=15), reason="Incite | Anti Spam")
                      hacker2 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully muted {message.author.mention} for spamming.")
                      #hacker2.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker2.set_footer(text="Automod punishment: None=Mute")
                      await message.channel.send(embed=hacker2, delete_after=5)

          if antiLink is True and not is_exempt:
              if invite_matches:
                  await message.delete()
                  punishment = data["punishment"]

                  if punishment == "kick":
                      await message.author.kick(reason="Incite | Anti Discord Invites")
                      hacker3 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully kiccked {message.author.mention} for sending Discord server invites.")
                      #hacker3.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker3.set_footer(text="Automod punishment: Kick")
                      await message.channel.send(embed=hacker3, delete_after=5)

                  elif punishment == "ban":
                      await message.author.ban(reason="Incite | Anti Discord Invites")
                      hacker4 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully banned {message.author.mention} for sending Discord server invites.")
                      #hacker4.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker4.set_footer(text="Automod punishment: Ban")
                      await message.channel.send(embed=hacker4, delete_after=5)

                  else:  # Default to timeout
                      now = discord.utils.utcnow()
                      await message.author.timeout(now + datetime.timedelta(minutes=15), reason="Incite | Anti Discord Invites")
                      hacker5 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully muted {message.author.mention} for sending Discord server invites.")
                      #hacker5.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker5.set_footer(text="Automod punishment: None=Mute")
                      await message.channel.send(embed=hacker5, delete_after=5)
              
              elif link_matches and not is_exempt:
                  await message.delete()  # Delete the message with links
                  punishment = data["punishment"]
                  
                  if punishment == "kick":
                      await message.author.kick(reason="Incite | Anti Link")
                      hacker6 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully kicked {message.author.mention} for sending links.")
                      #hacker6.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker6.set_footer(text="Automod punishment: Kick")
                      await message.channel.send(embed=hacker6, delete_after=5)

                  elif punishment == "ban":
                      await message.author.ban(reason="Incite | Anti Link")
                      hacker7 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully banned {message.author.mention} for sending links.")
                      #hacker7.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker7.set_footer(text="Automod punishment: Ban")
                      await message.channel.send(embed=hacker7, delete_after=5)

                  else:  # Default to timeout
                      now = discord.utils.utcnow()
                      await message.author.timeout(now + datetime.timedelta(minutes=15), reason="Incite | Anti Link")
                      hacker8 = discord.Embed(color=0x2f3136,description=f"<:whitecheck:1243577701638475787> | Successfully muted {message.author.mention} for sending links.")
                      #hacker8.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar}")
                      #hacker8.set_footer(text="Automod punishment: None=Mute")
                      await message.channel.send(embed=hacker8, delete_after=5)
                  
      except Exception as error:
        pass
          #print(f"AntiSpam/AntiLink Error: {error}")