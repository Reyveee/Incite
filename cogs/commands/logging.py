import discord
from discord.ext import commands
import os
import json
import random
from utils.Tools import *
from discord.ext.commands import Cog
import datetime
from typing import List,Union,Tuple,Dict,Any
import string
import io
import asyncio
import aiohttp

def initialize_logging_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        try:
            cursor.execute("SELECT log_type FROM logs LIMIT 1")
        except:
            cursor.execute("DROP TABLE logs")
            table_exists = None
    
    if not table_exists:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            log_type TEXT NOT NULL,
            channel_id TEXT,
            webhook_url TEXT,
            UNIQUE(guild_id, log_type)
        )
        ''')
    
    conn.commit()
    conn.close()

def _fetch_perms(role):
  perms = []
  for perm in role.permissions:
    if perm[1]:
      xperm = string.capwords(perm[0])
      perms.append(xperm)
  permf = ", ".join(perms)
  if permf == ", ":
    return None
  return permf


def _channel_change(
        before: discord.abc.GuildChannel,
        after: discord.abc.GuildChannel,
        *,
        TYPE: str,
    ) -> List[Tuple[str, Any]]:
        ls = []
        if before.name != after.name:
            ls.append(("`Name Changed     :`", before.name))
        if before.position != after.position:
            ls.append(("`Position Changed :`", before.position))
        if before.overwrites != after.overwrites:
            ls.append(
                ("`Overwrite Changed:`", _overwrite_to_json(before.overwrites))
            )
        if (
            before.category
            and after.category
            and before.category.id != after.category.id
        ):
            ls.append(
                (
                    "`Category Changed :`"
                    if after.category
                    else "`Category Removed :`",
                    f"{before.category.name} ({before.category.id})",
                )
            )
        if before.permissions_synced is not after.permissions_synced:
            ls.append(("`Toggled Permissions Sync:`", after.permissions_synced))

        if "text" in TYPE.lower():
            if before.nsfw is not after.nsfw:
                ls.append(("`NSFW Toggled     :`", after.nsfw))
            if before.topic != after.topic:
                ls.append(("`Topic Changed    :`", after.topic))
            if before.slowmode_delay != after.slowmode_delay:
                ls.append(
                    (
                        "`Slowmode Delay Changed:`"
                        if after.slowmode_delay
                        else "`Slowmode Delay Removed:`",
                        after.slowmode_delay or None,
                    )
                )

        if "vc" in TYPE.lower():
            if before.user_limit != after.user_limit:
                ls.append(("`Limit Updated    :`", before.user_limit or None))
            if before.rtc_region != after.rtc_region:
                ls.append(
                    (
                        "`Region Updated   :`",
                        before.rtc_region if after.rtc_region is not None else "Auto",
                    )
                )
            if before.bitrate != after.bitrate:
                ls.append(("`Bitrate Updated  :`", before.bitrate))
        return ls
  
def _overwrite_to_json(
        overwrites: Dict[
            Union[discord.Role, discord.User], discord.PermissionOverwrite
        ],
    ) -> str:
        try:
            over = {
                f"{str(target.name)} ({'Role' if isinstance(target, discord.Role) else 'Member'})": overwrite._values
                for target, overwrite in overwrites.items()
            }
            return json.dumps(over, indent=4)
        except TypeError:
            return "{}"


def _update_role(before: discord.Role,
        after: discord.Role,
    ) -> List[Tuple[str, Union[int, str, bool, Tuple[int, int, int]]]]:
        ls = []
        if before.name != after.name:
            ls.append(("`Name Changed      :`", after.name))
        if before.position != after.position:
            ls.append(("`Position Changed  :`", after.position))
        if before.hoist is not after.hoist:
            ls.append(("`Hoist Toggled     :`", after.hoist))
        if before.color != after.color:
            ls.append(("`Color Changed     :`", after.color.to_rgb()))
        if before.permissions != after.permissions:
          ls.append(("`Permissions Changed     :`",_fetch_perms(after)))
        return ls

async def save(method, guild, channel, webhook_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO logs (guild_id, log_type, channel_id, webhook_url)
    VALUES (?, ?, ?, ?)
    ''', (int(guild), method, channel, webhook_url))
    
    conn.commit()
    conn.close()

async def save_alls(guild, channel, webhook_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for log_type in ["msg", "member", "server", "channel", "role", "mod"]:
        cursor.execute('''
        INSERT OR REPLACE INTO logs (guild_id, log_type, channel_id, webhook_url)
        VALUES (?, ?, ?, ?)
        ''', (int(guild), log_type, channel, webhook_url))
    
    conn.commit()
    conn.close()

def difference_list(li1: List, li2: List) -> List:
        return [i for i in li1 + li2 if i not in li1 or i not in li2]

def _member_change(before, after):
        ls = []
        if before.nick != after.nick:
            ls.append(["`Nickname Changed:`", before.nick])
        if before.name != after.name:
            ls.append(["`Name changed:`", before.name])
        if before.discriminator != after.discriminator:
            ls.append(["`Discriminator:`", before.discriminator])
        if before.display_avatar.url != after.display_avatar.url:
            ls.append(["`Avatar Changed:`", f"<{before.display_avatar.url}>"])
        if before.roles != after.roles:
            ls.append((
                "`Role Update:`",
                ", ".join(
                    [
                        role.name
                        for role in difference_list(before.roles, after.roles)
                    ]
                ),
            ))
        return ls

def _server_change(before,after):
  if after.premium_tier != before.premium_tier:
    return "False"
  ls = []
  if before.name != after.name:
    ls.append(f"Name Changed: {before.name}")
  if before.icon != after.icon:
    ls.append(f"Icon Changed: {before.icon.url if before.icon else 'None'}")
  if before.description != after.description:
    ls.append(f"Description Changed: {before.description}")
  if before.banner != after.banner:
    ls.append(f"Banner Changed: {before.banner.url if before.banner else 'None'}")
  if before.owner_id != after.owner_id:
    ls.append(f"Ownership Transferred: {before.owner.mention}")
  if after.features != before.features:
    ls.append("Features Changed")
  if "VANITY_URL" in after.features:
    if before.vanity_url_code != after.vanity_url_code:
      ls.append(f"Vanity Code Changed: {before.vanity_url_code}")
  if before.verification_level != after.verification_level:
    ls.append(f"Verification Level Changed: {before.verification_level}")
  if before.system_channel != after.system_channel:
    ls.append(f"System Channel Changed: {before.system_channel.mention if before.system_channel else 'None'}")
  if before.rules_channel != after.rules_channel:
    ls.append(f"Rules Channel Changed: {before.rules_channel.mention if before.rules_channel else 'None'}")
  if after.afk_channel != before.afk_channel:
    ls.append(f"AFK Channel Changed: {before.afk_channel.mention if before.afk_channel else 'None'}")
  if after.afk_timeout != before.afk_timeout:
    ls.append(f"AFK Timeout: {before.afk_timeout}")
  return ls

def _server_change_(bef,aft):
  before = aft
  after = bef
  if after.premium_tier != before.premium_tier:
    return "False"
  ls = []
  if before.name != after.name:
    ls.append(f"Name Changed: {before.name}")
  if before.icon != after.icon:
    ls.append(f"Icon Changed: {before.icon.url if before.icon else 'None'}")
  if before.description != after.description:
    ls.append(f"Description Changed: {before.description}")
  if before.banner != after.banner:
    ls.append(f"Banner Changed: {before.banner.url if before.banner else 'None'}")
  if before.owner_id != after.owner_id:
    ls.append(f"Ownership Transferred: {before.owner.mention}")
  if after.features != before.features:
    ls.append("Features Changed")
  if "VANITY_URL" in after.features:
    if before.vanity_url_code != after.vanity_url_code:
      ls.append(f"Vanity Code Changed: {before.vanity_url_code}")
  if before.verification_level != after.verification_level:
    ls.append(f"Verification Level Changed: {before.verification_level}")
  if before.system_channel != after.system_channel:
    ls.append(f"System Channel Changed: {before.system_channel.mention if before.system_channel else 'None'}")
  if before.rules_channel != after.rules_channel:
    ls.append(f"Rules Channel Changed: {before.rules_channel.mention if before.rules_channel else 'None'}")
  if after.afk_channel != before.afk_channel:
    ls.append(f"AFK Channel Changed: {before.afk_channel.mention if before.afk_channel else 'None'}")
  if after.afk_timeout != before.afk_timeout:
    ls.append(f"AFK Timeout: {before.afk_timeout}")
  for item in ls:
    newitem = f"{item}".replace("Changed", "")
    ls.remove(item)
    ls.append(newitem)
  return ls


def get_data(guild):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT log_type, channel_id, webhook_url FROM logs WHERE guild_id = ?', (int(guild),))
    results = cursor.fetchall()
    
    conn.close()
    
    if not results:
        return None
    
    data = {}
    data["webhooks"] = {}
    
    for log_type, channel_id, webhook_url in results:
        data[log_type] = channel_id
        if webhook_url:
            data["webhooks"][log_type] = webhook_url
    
    return data


def save_all(guild, channel):
  xc = str(channel)
  dat = {"msg": xc, "member": xc, "server": xc, "channel": xc, "role": xc, "mod": xc}
  with open("logs.json","r") as f:
    idk = json.load(f)
  idk[str(guild)] = dat
  with open("logs.json","w") as f:
    json.dump(idk,f,indent=4)


def save_g(guild):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM logs WHERE guild_id = ?', (int(guild),))
    count = cursor.fetchone()[0]
    
    if count == 0:
        for log_type in ["msg", "member", "server", "channel", "role", "mod"]:
            cursor.execute('''
            INSERT OR IGNORE INTO logs (guild_id, log_type, channel_id, webhook_url)
            VALUES (?, ?, NULL, NULL)
            ''', (int(guild), log_type))
    
    conn.commit()
    conn.close()


class Logging(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      initialize_logging_database()

  def em_g(self, title, description, footer, author, author_avatar, clr):
      embed = discord.Embed(title=title, description=description, color=clr)
      embed.set_author(name=str(author), icon_url=author_avatar)
      embed.set_footer(text=footer, icon_url=self.bot.user.avatar)
      embed.timestamp = discord.utils.utcnow()
      return embed

  async def _check(self, ctx):
      return int(ctx.message.author.top_role.position) > int(ctx.guild.me.top_role.position)

  async def send_webhook_message(self, webhook_url, embed):
      try:
          async with aiohttp.ClientSession() as session:
              webhook = discord.Webhook.from_url(webhook_url, session=session)
              await webhook.send(embed=embed)
              return True
      except Exception as e:
          print(f"Error sending webhook message: {e}")
          return False

  @Cog.listener()
  async def on_ready(self):
      for guild in self.bot.guilds:
          save_g(str(guild.id))

  @commands.Cog.listener()
  async def on_guild_join(self, guild):
      save_g(str(guild.id))

    
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  @commands.hybrid_group(name="logging", description="List all log commands.", aliases=['logs', 'log'])
  async def logging(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    #embed = discord.Embed(title="Log Commands", description="<...> Required | [...] Optional", color=0x2f3136)
    #embed.add_field(name="messages", value="Logs message actions, on delete, on edited & bluk delete.", inline=False)
    #embed.add_field(name="members", value="Logs members action, on join, on leave, on member update.", inline=False)
    #embed.add_field(name="server", value="Logs server actions, on emoji update, name update, icon update.", inline=False)
    #embed.add_field(name="channels", value="Logs channel actions, on create, on edit, on delete.", inline=False)
    #embed.add_field(name="roles", value="Logs role actions, on create, on edit, on delete.", inline=False)
    #embed.add_field(name="mod", value="Logs moderator actions, on member ban, on member kick, on member timeout.", inline=False)
    #embed.add_field(name="all enable", value="Enables all type of logs.", inline=False)
    #embed.add_field(name="all disable", value="Disables all type of logs.", inline=False)
  
    #message = await ctx.send(embed=embed)
    #await asyncio.sleep(5)
    #await message.delete()


  @logging.command(name="messages", description="Set up a channel for message logging (edit, delete, bulk delete)")
  async def _msglog(self, ctx, channel: discord.TextChannel):
      if channel is None:
          return await ctx.send("Please mention a valid channel to set message logs.")
        
      channel_id = str(channel.id)

      if not await self._check(ctx):
        return await ctx.reply("<:whitecross:1243852723753844736> | Your top role should be above my top role.")
        
      webhook = await channel.create_webhook(name="Incite Message Logs")
      webhook_url = webhook.url
      await save("msg", str(ctx.guild.id), str(channel_id), webhook_url)

      embed = discord.Embed(description=f"<:whitecheck:1243577701638475787> | Message log channel updated to {channel.mention}", color=0x2f3136)
      await ctx.send(embed=embed)
    
    
  @logging.command(name="members", description="Set up a channel for member logging (join, leave, update)")
  async def __msglog(self, ctx, channel: discord.TextChannel):
    if channel is None:
      return await ctx.send("Please mention a valid channel to set message logs.")
    
    channel_id = str(channel.id)


    if not await self._check(ctx):
      return await ctx.reply("<:whitecross:1243852723753844736> | Your top role should be above my top role.")

    webhook = await channel.create_webhook(name="Incite Member Logs")
    webhook_url = webhook.url
    await save("member", str(ctx.guild.id), str(channel_id), webhook_url)
    embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Member log channel updated to {channel.mention}", color=0x2f3136)
    await ctx.send(embed=embed)


  @logging.command(name="server", description="Set up a channel for server logging (name, icon, settings changes)")
  async def ___msglog(self, ctx, channel: discord.TextChannel):
    if channel is None:
      return await ctx.send("Please mention a valid channel to set message logs.")
    
    channel_id = str(channel.id)

    if not await self._check(ctx):
      return await ctx.reply("<:whitecross:1243852723753844736> | Your top role should be above my top role.")

    webhook = await channel.create_webhook(name="Incite Server Logs")
    webhook_url = webhook.url
    await save("server", str(ctx.guild.id), str(channel_id), webhook_url)

    embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Server log channel updated to {channel.mention}", color=0x2f3136)
    await ctx.send(embed=embed)

  @logging.command(name="channels", description="Set up a channel for channel logging (create, delete, update)")
  async def ___msglog_(self, ctx, channel: discord.TextChannel):
    if channel is None:
      return await ctx.send("Please mention a valid channel to set message logs.")
    
    channel_id = str(channel.id)

    if not await self._check(ctx):
      return await ctx.reply("<:whitecross:1243852723753844736> | Your top role should be above my top role.")

    webhook = await channel.create_webhook(name="Incite Channels Logs")
    webhook_url = webhook.url
    await save("channel", str(ctx.guild.id), str(channel_id), webhook_url)

    embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Channel log channel updated to {channel.mention}", color=0x2f3136)
    await ctx.send(embed=embed)


  @logging.command(name="roles", description="Set up a channel for role logging (create, delete, update)")
  async def __msglog__(self, ctx, channel: discord.TextChannel):
    if channel is None:
        return await ctx.send("Please mention a valid channel to set message logs.")
    
    channel_id = str(channel.id)

    if not await self._check(ctx):
      return await ctx.reply("<:whitecross:1243852723753844736> | Your top role should be above my top role.")

    webhook = await channel.create_webhook(name="Incite Roles Logs")
    webhook_url = webhook.url
    await save("role", str(ctx.guild.id), str(channel_id), webhook_url)

    embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Role log channel updated to {channel.mention}", color=0x2f3136)
    await ctx.send(embed=embed)


  @logging.command(name="mod", description="Set up a channel for moderator action logging (kick, ban, timeout)")
  async def teccnobetamsglog(self, ctx, channel: discord.TextChannel):
    if channel is None:
        return await ctx.send("Please mention a valid channel to set message logs.")
    
    channel_id = str(channel.id)

    if not await self._check(ctx):
      return await ctx.reply("<:whitecross:1243852723753844736> | Your top role should be above my top role.")

    webhook = await channel.create_webhook(name="Incite Mod Logs")
    webhook_url = webhook.url
    await save("mod", str(ctx.guild.id), str(channel_id), webhook_url)
    
    embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Mod log channel updated to {channel.mention}", color=0x2f3136)
    await ctx.send(embed=embed)


  @logging.group(name="all", description="Enable or disable all logging channels at once")
  async def _teknobeta(self, ctx):
    embed = discord.Embed(title="Logall Commands", description="<...> Duty | [...] Optional", color=0x2f3136)
    embed.add_field(name="logall enable", value="Enables all type of logs.")
    embed.add_field(name="logall disable", value="Disables all type of logs.")
    embed.set_footer(icon_url=ctx.bot.user.avatar, text="Thanks For Selecting Incite!")
    await ctx.send(embed=embed)

  @_teknobeta.command(name="enable", description="Enable all logging channels at once")
  async def logallenable(self, ctx, channel: discord.TextChannel):
      if channel is None:
          return await ctx.send("Please mention a valid channel to set message logs.")
      
      channel_id = str(channel.id)
  
      if not await self._check(ctx):
          return await ctx.reply("<:whitecross:1243852723753844736> | Your top role should be above my top role.")
      
      avatar_url = self.bot.user.display_avatar.url
      async with aiohttp.ClientSession() as session:
          async with session.get(avatar_url) as resp:
              avatar_bytes = await resp.read()
 
      webhook = await channel.create_webhook(name="Incite", avatar=avatar_bytes)
      webhook_url = webhook.url
      
      await save_alls(str(ctx.guild.id), str(channel.id), webhook_url)
      
      embed = discord.Embed(description="", color=0x2f3136)
      await ctx.send(f"<:whitecheck:1243577701638475787> | Successfully enabled all logs channels to {channel.mention}")



  @_teknobeta.command(name="disable", description="Disable all logging channels at once")
  async def _dis(self, ctx):
      if not await self._check(ctx):
          return await ctx.send("<:whitecross:1243852723753844736> | Your top role should be above my top role.")
      
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('DELETE FROM logs WHERE guild_id = ?', (ctx.guild.id,))
      
      for log_type in ["msg", "member", "server", "channel", "role", "mod"]:
          cursor.execute('''
          INSERT INTO logs (guild_id, log_type, channel_id, webhook_url)
          VALUES (?, ?, NULL, NULL)
          ''', (ctx.guild.id, log_type))
      
      conn.commit()
      conn.close()
      
      embed = discord.Embed(description="", color=0x2f3136)
      await ctx.send("<:whitecheck:1243577701638475787> | Successfully disabled all the logs for this server.")


      


  @Cog.listener()
  async def on_raw_bulk_message_delete(self, payload):
      try:
          guild = self.bot.get_guild(payload.guild_id)
          msgs = list(payload.message_ids)
          
          embed = discord.Embed(
              title="Bulk Messages Deleted",
              description=f"Multiple messages were deleted in <#{payload.channel_id}>",
              color=0x2f3136
          )
          embed.add_field(name="Channel", value=f"<#{payload.channel_id}>", inline=True)
          embed.add_field(name="Message Count", value=f"{len(msgs)}", inline=True)
          embed.set_author(name=f"{guild.name}", icon_url=guild.icon.url if guild.icon else self.bot.user.avatar)
          embed.set_footer(text=f"Server ID: {guild.id} • Channel ID: {payload.channel_id}")
          embed.timestamp = discord.utils.utcnow()
          
          data = get_data(str(payload.guild_id))
          if not data or "msg" not in data or not data["msg"]:
              return
  
          config = get_data(str(guild.id))
          
          if "webhooks" in config and "msg" in config["webhooks"]:
              webhook_url = config["webhooks"]["msg"]
              success = await self.send_webhook_message(webhook_url, embed)
              if success:
                  return
  
          channel = self.bot.get_channel(int(config["msg"]))
          if channel:
              await channel.send(embed=embed)
      except Exception as e:
          pass

  @Cog.listener()
  async def on_message_edit(self, before, after):
      try:
          msgobj = after
          author = after.author
          channel = after.channel
          if author.bot or (before.content is None and after.content is None):
              return
  
          conf = get_data(str(after.guild.id))
          if not conf or "msg" not in conf or not conf["msg"]:
              return
          
          # Truncate content if too long
          before_content = before.content[:1000] + "..." if len(before.content) > 1000 else before.content
          after_content = after.content[:1000] + "..." if len(after.content) > 1000 else after.content
          
          embed = discord.Embed(
              title="Message Edited",
              description=f"A message was edited in {channel.mention}",
              color=0x2f3136
          )
          embed.add_field(name="Before", value=f"```{before_content or 'No content'}```", inline=False)
          embed.add_field(name="After", value=f"```{after_content or 'No content'}```", inline=False)
          embed.add_field(name="Author", value=f"{author.mention} (`{author.name}` • `{author.id}`)", inline=True)
          embed.add_field(name="Channel", value=f"{channel.mention}", inline=True)
          embed.add_field(name="Jump to Message", value=f"[Click Here]({msgobj.jump_url})", inline=True)
          embed.set_author(name=f"{author.name}", icon_url=author.avatar.url if author.avatar else author.default_avatar.url)
          embed.set_footer(text=f"User ID: {author.id} • Message ID: {after.id}")
          embed.timestamp = discord.utils.utcnow()
  
          guild = after.guild
          config = get_data(str(guild.id))
          
          if "webhooks" in config and "msg" in config["webhooks"]:
              webhook_url = config["webhooks"]["msg"]
              success = await self.send_webhook_message(webhook_url, embed)
              if success:
                  return
  
          channel = self.bot.get_channel(int(config["msg"]))
          if channel:
              await channel.send(embed=embed)
  
      except Exception as e:
          pass


  @Cog.listener()
  async def on_message_delete(self, message):
      try:
          author = message.author
          guild = message.guild
          if author.bot or message.content is None:
              return

          config = get_data(str(guild.id))
          if not config or "msg" not in config or not config["msg"]:
              return
          
          # Truncate content if too long
          content = message.content[:1000] + "..." if len(message.content) > 1000 else message.content
          
          embed = discord.Embed(
              title="Message Deleted",
              description=f"A message was deleted in {message.channel.mention}",
              color=0x2f3136
          )
          embed.add_field(name="Content", value=f"```{content or 'No content'}```", inline=False)
          embed.add_field(name="Author", value=f"{author.mention} (`{author.name}` • `{author.id}`)", inline=True)
          embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=True)
          
          # Add attachments if any
          if message.attachments:
              attachment_list = "\n".join([f"[{a.filename}]({a.proxy_url})" for a in message.attachments[:5]])
              if len(message.attachments) > 5:
                  attachment_list += f"\n+{len(message.attachments) - 5} more attachments"
              embed.add_field(name="Attachments", value=attachment_list, inline=False)
              
          embed.set_author(name=f"{author.name}", icon_url=author.avatar.url if author.avatar else author.default_avatar.url)
          embed.set_footer(text=f"User ID: {author.id} • Message ID: {message.id}")
          embed.timestamp = discord.utils.utcnow()
        
          if "webhooks" in config and "msg" in config["webhooks"]:
              webhook_url = config["webhooks"]["msg"]
              success = await self.send_webhook_message(webhook_url, embed)
              if success:
                return

          channel = self.bot.get_channel(int(config["msg"]))
          if channel:
              await channel.send(embed=embed)
              
      except Exception as e:
          pass


  @Cog.listener()
  async def on_member_join(self, member: discord.Member):
      try:
          guild = member.guild
          
          # Calculate account age
          account_age = discord.utils.utcnow() - member.created_at
          account_age_str = f"{account_age.days} days"
          
          embed = discord.Embed(
              title="Member Joined",
              description=f"{member.mention} has joined the server",
              color=0x2f3136
          )
          
          embed.add_field(name="User", value=f"`{member.name}` • `{member.id}`", inline=True)
          embed.add_field(name="Account Created", value=f"{discord.utils.format_dt(member.created_at, 'R')}", inline=True)
          embed.add_field(name="Account Age", value=account_age_str, inline=True)
          
          # Add server member count
          embed.add_field(name="Member Count", value=f"{guild.member_count}", inline=True)
          
          # Check if account is new (less than 7 days)
          if account_age.days < 7:
              embed.add_field(name="⚠️ Notice", value="This account was created recently", inline=False)
          
          embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
          embed.set_author(name=f"{member.name}", icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
          embed.set_footer(text=f"User ID: {member.id}")
          embed.timestamp = discord.utils.utcnow()
          
          if member.bot:
              embed.title = "Bot Added"
              embed.description = f"A bot has been added to the server"
              async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                  mem = entry.user
                  embed.add_field(name="Added By", value=f"{mem.mention} (`{mem.name}` • `{mem.id}`)", inline=False)
          
          config = get_data(str(guild.id))
          if not config or "member" not in config or not config["member"]:
              return
          
          if "webhooks" in config and "member" in config["webhooks"]:
              webhook_url = config["webhooks"]["member"]
              success = await self.send_webhook_message(webhook_url, embed)
              if success:
                return

          channel = self.bot.get_channel(int(config["member"]))
          if channel:
              await channel.send(embed=embed)
                
      except Exception as e:
          pass
                
      except Exception as e:
          pass
          #print(f"Error in logging member join: {e}")

  @Cog.listener()
  async def on_member_remove(self, member):
      try:
          guild = member.guild
          kick = None
          mem = None
          reason = None
          
          # Calculate time spent in server
          joined_at = member.joined_at if member.joined_at else discord.utils.utcnow()
          time_in_server = discord.utils.utcnow() - joined_at
          time_in_server_str = f"{time_in_server.days} days"
  
          # Check if member was kicked
          async for logs in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
              stamp = datetime.datetime.now() - datetime.timedelta(seconds=30)
              if logs.target.id == member.id and stamp.timestamp() <= logs.created_at.timestamp():
                  kick = True
                  mem = logs.user
                  reason = logs.reason
  
          # Get config and check if logging is enabled
          config = get_data(str(guild.id))
          if not config or "member" not in config or not config["member"]:
              return
  
          # Base embed for both kick and leave
          if kick:
              embed = discord.Embed(
                  title="Member Kicked",
                  description=f"{member.mention} was kicked from the server",
                  color=0x2f3136
              )
              if mem:
                  embed.add_field(name="Kicked By", value=f"{mem.mention} (`{mem.name}` • `{mem.id}`)", inline=True)
              if reason:
                  embed.add_field(name="Reason", value=reason, inline=True)
          else:
              embed = discord.Embed(
                  title="Member Left",
                  description=f"{member.mention} has left the server",
                  color=0x2f3136
              )
          
          embed.add_field(name="User", value=f"`{member.name}` • `{member.id}`", inline=True)
          embed.add_field(name="Joined Server", value=f"{discord.utils.format_dt(joined_at, 'R')}", inline=True)
          embed.add_field(name="Time in Server", value=time_in_server_str, inline=True)
          
          # Add roles if member had any
          if len(member.roles) > 1:  # More than just @everyone
              roles = [role.mention for role in member.roles if role.name != "@everyone"]
              roles_str = ", ".join(roles[:10])
              if len(roles) > 10:
                  roles_str += f" (+{len(roles) - 10} more)"
              embed.add_field(name="Roles", value=roles_str, inline=False)
          
          embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
          embed.set_author(name=f"{member.name}", icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
          embed.set_footer(text=f"User ID: {member.id} • Server Member Count: {guild.member_count}")
          embed.timestamp = discord.utils.utcnow()
  
          if "webhooks" in config and "member" in config["webhooks"]:
              webhook_url = config["webhooks"]["member"]
              success = await self.send_webhook_message(webhook_url, embed)
              if success:
                return
  
          channel = self.bot.get_channel(int(config["member"]))
          if channel:
              await channel.send(embed=embed)
  
      except Exception as e:
          pass

  @Cog.listener()
  async def on_user_update(self, before, after):
      try:
          # Check if username or discriminator changed
          if before.name != after.name or before.discriminator != after.discriminator:
              # Find mutual guilds with this user
              for guild in self.bot.guilds:
                  member = guild.get_member(after.id)
                  if member:
                      # Get config for this guild
                      config = get_data(str(guild.id))
                      if not config or "member" not in config or not config["member"]:
                          continue
                      
                      # Create embed for username change
                      embed = discord.Embed(
                          title="Username Changed",
                          description=f"{after.mention} has changed their username",
                          color=0x2f3136
                      )
                      
                      if before.name != after.name:
                          embed.add_field(name="Old Username", value=f"`{before.name}`", inline=True)
                          embed.add_field(name="New Username", value=f"`{after.name}`", inline=True)
                      
                      if before.discriminator != after.discriminator and before.discriminator != "0" and after.discriminator != "0":
                          embed.add_field(name="Old Discriminator", value=f"`#{before.discriminator}`", inline=True)
                          embed.add_field(name="New Discriminator", value=f"`#{after.discriminator}`", inline=True)
                      
                      embed.add_field(name="User ID", value=f"`{after.id}`", inline=False)
                      
                      embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)
                      embed.set_author(name=f"{after.name}", icon_url=after.avatar.url if after.avatar else after.default_avatar.url)
                      embed.set_footer(text=f"User ID: {after.id}")
                      embed.timestamp = discord.utils.utcnow()
                      
                      if "webhooks" in config and "member" in config["webhooks"]:
                          webhook_url = config["webhooks"]["member"]
                          success = await self.send_webhook_message(webhook_url, embed)
                          if success:
                              continue
                      
                      channel = self.bot.get_channel(int(config["member"]))
                      if channel:
                          await channel.send(embed=embed)
      except Exception as e:
          pass

  @Cog.listener()
  async def on_guild_update(self, before, after):
      try:
          changes = _server_change(before, after)
          bec = _server_change_(before, after)
          
          if changes == "False" or not changes:
              return
              
          async for logs in after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
              mem = logs.user
              reason = logs.reason
          
          # Enhanced server update embed
          embed = discord.Embed(
              title="Server Updated",
              description=f"Server settings have been modified",
              color=0x2f3136
          )
          
          # Add moderator info
          embed.add_field(name="Updated By", value=f"{mem.mention} (`{mem.name}` • `{mem.id}`)", inline=True)
          
          # Add reason if available
          if reason:
              embed.add_field(name="Reason", value=reason, inline=True)
          
          # Format changes in a cleaner way
          if changes:
              formatted_changes = "\n".join(changes)
              embed.add_field(name="Before Changes", value=f"```{formatted_changes}```", inline=False)
          
          if bec:
              formatted_after = "\n".join(bec)
              embed.add_field(name="After Changes", value=f"```{formatted_after}```", inline=False)
          
          # Add server info
          embed.add_field(name="Server ID", value=f"`{after.id}`", inline=True)
          
          # Set author and thumbnail
          embed.set_author(name=f"{after.name}", icon_url=after.icon.url if after.icon else mem.default_avatar.url)
          if after.icon:
              embed.set_thumbnail(url=after.icon.url)
          
          embed.set_footer(text=f"Server ID: {after.id}")
          embed.timestamp = discord.utils.utcnow()
          
          config = get_data(str(after.id))
          if not config or "server" not in config or not config["server"]:
              return
          
          if "webhooks" in config and "server" in config["webhooks"]:
              webhook_url = config["webhooks"]["server"]
              success = await self.send_webhook_message(webhook_url, embed)
              if success:
                return
  
          # Fallback to channel send if webhook fails
          channel = self.bot.get_channel(int(config["server"]))
          if channel:
              await channel.send(embed=embed)
                
      except Exception as e:
          pass

  @Cog.listener()
  async def on_guild_role_create(self, role):
      try:
          guild = role.guild
          async for logs in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
              if logs.target.id == role.id:
                  # Enhanced role creation embed
                  embed = discord.Embed(
                      title="Role Created",
                      description=f"A new role has been created in the server",
                      color=0x2f3136
                  )
                  
                  # Add role details
                  embed.add_field(name="Role Name", value=f"{role.mention} (`{role.name}`)", inline=True)
                  embed.add_field(name="Role ID", value=f"`{role.id}`", inline=True)
                  embed.add_field(name="Created By", value=f"{logs.user.mention} (`{logs.user.name}`)", inline=True)
                  
                  # Add role properties
                  embed.add_field(name="Color", value=f"`{role.color}`", inline=True)
                  embed.add_field(name="Position", value=f"`{role.position}`", inline=True)
                  
                  # Add role settings
                  settings = []
                  settings.append(f"Mentionable: `{role.mentionable}`")
                  settings.append(f"Displayed Separately: `{role.hoist}`")
                  embed.add_field(name="Settings", value="\n".join(settings), inline=False)
                  
                  # Add permissions if any
                  permissions = _fetch_perms(role)
                  if permissions:
                      embed.add_field(name="Permissions", value=f"```{permissions}```", inline=False)
                  
                  # Set author and timestamp
                  embed.set_author(name=f"{logs.user.name}", icon_url=logs.user.avatar.url if logs.user.avatar else logs.user.default_avatar.url)
                  embed.set_footer(text=f"Role ID: {role.id} • Server ID: {guild.id}")
                  embed.timestamp = discord.utils.utcnow()
                  
                  # Add color indicator
                  if role.color != discord.Color.default():
                      embed.color = role.color
                  
                  data = get_data(str(guild.id))
                  if not data or "role" not in data or not data["role"]:
                      return
                  
                  if "webhooks" in data and "role" in data["webhooks"]:
                      webhook_url = data["webhooks"]["role"]
                      success = await self.send_webhook_message(webhook_url, embed)
                      if success:
                          return
  
                  # Fallback to channel send if webhook fails
                  channel = self.bot.get_channel(int(data["role"]))
                  if channel:
                      await channel.send(embed=embed)
                    
      except Exception as e:
          pass

  @Cog.listener()
  async def on_guild_role_delete(self, role):
      try:
          guild = role.guild
          async for logs in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
              if logs.target.id == role.id:
                  # Enhanced role deletion embed
                  embed = discord.Embed(
                      title="Role Deleted",
                      description=f"A role has been removed from the server",
                      color=0x2f3136
                  )
                  
                  # Add role details
                  embed.add_field(name="Role Name", value=f"`{role.name}`", inline=True)
                  embed.add_field(name="Role ID", value=f"`{role.id}`", inline=True)
                  embed.add_field(name="Deleted By", value=f"{logs.user.mention} (`{logs.user.name}`)", inline=True)
                  
                  # Add role properties
                  embed.add_field(name="Color", value=f"`{role.color}`", inline=True)
                  embed.add_field(name="Position", value=f"`{role.position}`", inline=True)
                  embed.add_field(name="Member Count", value=f"`{len(role.members)}`", inline=True)
                  
                  # Add role settings
                  settings = []
                  settings.append(f"Mentionable: `{role.mentionable}`")
                  settings.append(f"Displayed Separately: `{role.hoist}`")
                  embed.add_field(name="Settings", value="\n".join(settings), inline=False)
                  
                  # Add permissions if any
                  permissions = _fetch_perms(role)
                  if permissions:
                      embed.add_field(name="Permissions", value=f"```{permissions}```", inline=False)
                  
                  # Set author and timestamp
                  embed.set_author(name=f"{logs.user.name}", icon_url=logs.user.avatar.url if logs.user.avatar else logs.user.default_avatar.url)
                  embed.set_footer(text=f"Role ID: {role.id} • Server ID: {guild.id}")
                  embed.timestamp = discord.utils.utcnow()
                  
                  # Use role color for embed
                  if role.color != discord.Color.default():
                      embed.color = role.color
                  
                  data = get_data(str(guild.id))
                  if not data or "role" not in data or not data["role"]:
                      return
                  
                  if "webhooks" in data and "role" in data["webhooks"]:
                      webhook_url = data["webhooks"]["role"]
                      success = await self.send_webhook_message(webhook_url, embed)
                      if success:
                          return
  
                  # Fallback to channel send if webhook fails
                  channel = self.bot.get_channel(int(data["role"]))
                  if channel:
                      await channel.send(embed=embed)
                    
      except Exception as e:
          pass

  @Cog.listener()
  async def on_guild_role_update(self, before, after):
      try:
          async for logs in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
              if after.id == logs.target.id:
                  user = logs.user
                  ls = _update_role(before, after)
                  
                  if not ls:  # No changes detected
                      return
                  
                  # Enhanced role update embed
                  embed = discord.Embed(
                      title="Role Updated",
                      description=f"Role {after.mention} has been modified",
                      color=0x2f3136
                  )
                  
                  # Add role details
                  embed.add_field(name="Role Name", value=f"`{after.name}`", inline=True)
                  embed.add_field(name="Role ID", value=f"`{after.id}`", inline=True)
                  embed.add_field(name="Updated By", value=f"{user.mention} (`{user.name}`)", inline=True)
                  
                  # Format changes in a cleaner way
                  changes_text = ""
                  for change_type, change_value in ls:
                      changes_text += f"{change_type} {change_value}\n"
                  
                  embed.add_field(name="Changes Made", value=f"```{changes_text}```", inline=False)
                  
                  # Add current role properties
                  embed.add_field(name="Current Position", value=f"`{after.position}`", inline=True)
                  embed.add_field(name="Member Count", value=f"`{len(after.members)}`", inline=True)
                  
                  # Set author and timestamp
                  embed.set_author(name=f"{user.name}", icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
                  embed.set_footer(text=f"Role ID: {after.id} • Server ID: {after.guild.id}")
                  embed.timestamp = discord.utils.utcnow()
                  
                  # Use new role color for embed
                  if after.color != discord.Color.default():
                      embed.color = after.color
                  
                  data = get_data(str(after.guild.id))
                  if not data or "role" not in data or not data["role"]:
                      return
                  
                  if "webhooks" in data and "role" in data["webhooks"]:
                      webhook_url = data["webhooks"]["role"]
                      success = await self.send_webhook_message(webhook_url, embed)
                      if success:
                          return
  
                  # Fallback to channel send if webhook fails
                  channel = self.bot.get_channel(int(data["role"]))
                  if channel:
                      await channel.send(embed=embed)
                    
      except Exception as e:
          pass

  @Cog.listener()
  async def on_guild_channel_create(self, channel):
      try:
          async for logs in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
              if logs.target.id == channel.id:
                  user = logs.user
                  reason = logs.reason
                  channel_type = str(channel.type)
                  TYPE = channel_type.replace("_", " ").title() + " Channel"
                  
                  # Enhanced channel creation embed
                  embed = discord.Embed(
                      title="Channel Created",
                      description=f"A new {TYPE.lower()} has been created",
                      color=0x2f3136
                  )
                  
                  # Add channel details
                  embed.add_field(name="Channel Name", value=f"{channel.mention} (`{channel.name}`)", inline=True)
                  embed.add_field(name="Channel ID", value=f"`{channel.id}`", inline=True)
                  embed.add_field(name="Created By", value=f"{user.mention} (`{user.name}`)", inline=True)
                  
                  # Add channel properties
                  embed.add_field(name="Type", value=f"`{TYPE}`", inline=True)
                  embed.add_field(name="Position", value=f"`{channel.position}`", inline=True)
                  
                  # Add category if exists
                  if channel.category:
                      embed.add_field(name="Category", value=f"`{channel.category.name}`", inline=True)
                  else:
                      embed.add_field(name="Category", value="`None`", inline=True)
                  
                  # Add reason if available
                  if reason:
                      embed.add_field(name="Reason", value=f"`{reason}`", inline=False)
                  
                  # Add channel-specific details based on type
                  if hasattr(channel, 'topic') and channel.topic:
                      embed.add_field(name="Topic", value=f"`{channel.topic}`", inline=False)
                  
                  if hasattr(channel, 'slowmode_delay') and channel.slowmode_delay > 0:
                      embed.add_field(name="Slowmode", value=f"`{channel.slowmode_delay}s`", inline=True)
                  
                  if hasattr(channel, 'nsfw'):
                      embed.add_field(name="NSFW", value=f"`{channel.nsfw}`", inline=True)
                  
                  # Set author and timestamp
                  embed.set_author(name=f"{user.name}", icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
                  embed.set_footer(text=f"Channel ID: {channel.id} • Server ID: {channel.guild.id}")
                  embed.timestamp = discord.utils.utcnow()
                  
                  data = get_data(str(channel.guild.id))
                  if not data or "channel" not in data or not data["channel"]:
                      return
                  
                  if "webhooks" in data and "channel" in data["webhooks"]:
                      webhook_url = data["webhooks"]["channel"]
                      success = await self.send_webhook_message(webhook_url, embed)
                      if success:
                          return
  
                  # Fallback to channel send if webhook fails
                  log_channel = self.bot.get_channel(int(data["channel"]))
                  if log_channel:
                      await log_channel.send(embed=embed)
                    
      except Exception as e:
          pass

  @Cog.listener()
  async def on_guild_channel_delete(self, channel):
      try:
          async for logs in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
              if logs.target.id == channel.id:
                  user = logs.user
                  reason = logs.reason
                  channel_type = str(channel.type)
                  TYPE = channel_type.replace("_", " ").title() + " Channel"
                  
                  # Enhanced channel deletion embed
                  embed = discord.Embed(
                      title="Channel Deleted",
                      description=f"A {TYPE.lower()} has been deleted",
                      color=0x2f3136
                  )
                  
                  # Add channel details
                  embed.add_field(name="Channel Name", value=f"`{channel.name}`", inline=True)
                  embed.add_field(name="Channel ID", value=f"`{channel.id}`", inline=True)
                  embed.add_field(name="Deleted By", value=f"{user.mention} (`{user.name}`)", inline=True)
                  
                  # Add channel properties
                  embed.add_field(name="Type", value=f"`{TYPE}`", inline=True)
                  embed.add_field(name="Position", value=f"`{channel.position}`", inline=True)
                  
                  # Add category if exists
                  if channel.category:
                      embed.add_field(name="Category", value=f"`{channel.category.name}`", inline=True)
                  else:
                      embed.add_field(name="Category", value="`None`", inline=True)
                  
                  # Add reason if available
                  if reason:
                      embed.add_field(name="Reason", value=f"`{reason}`", inline=False)
                  
                  # Add channel-specific details based on type
                  if hasattr(channel, 'topic') and channel.topic:
                      embed.add_field(name="Topic", value=f"`{channel.topic}`", inline=False)
                  
                  # Set author and timestamp
                  embed.set_author(name=f"{user.name}", icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
                  embed.set_footer(text=f"Channel ID: {channel.id} • Server ID: {channel.guild.id}")
                  embed.timestamp = discord.utils.utcnow()
                  
                  data = get_data(str(channel.guild.id))
                  if not data or "channel" not in data or not data["channel"]:
                      return
                  
                  if "webhooks" in data and "channel" in data["webhooks"]:
                      webhook_url = data["webhooks"]["channel"]
                      success = await self.send_webhook_message(webhook_url, embed)
                      if success:
                          return
  
                  # Fallback to channel send if webhook fails
                  log_channel = self.bot.get_channel(int(data["channel"]))
                  if log_channel:
                      await log_channel.send(embed=embed)
                    
      except Exception as e:
          pass

  @Cog.listener()
  async def on_guild_channel_update(self, before, after):
      try:
          async for logs in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
              if after.id == logs.target.id:
                  user = logs.user
                  channel_type = str(after.type)
                  TYPE = channel_type.replace("_", " ").title() + " Channel"
                  changes = _channel_change(before, after, TYPE=channel_type)
                  
                  if not changes:  # No changes detected
                      return
                  
                  # Enhanced channel update embed
                  embed = discord.Embed(
                      title="Channel Updated",
                      description=f"Channel {after.mention} has been modified",
                      color=0x2f3136
                  )
                  
                  # Add channel details
                  embed.add_field(name="Channel Name", value=f"`{after.name}`", inline=True)
                  embed.add_field(name="Channel ID", value=f"`{after.id}`", inline=True)
                  embed.add_field(name="Updated By", value=f"{user.mention} (`{user.name}`)", inline=True)
                  
                  # Format changes in a cleaner way
                  changes_text = ""
                  for change_type, change_value in changes:
                      changes_text += f"{change_type} {change_value}\n"
                  
                  embed.add_field(name="Changes Made", value=f"```{changes_text}```", inline=False)
                  
                  # Add current channel properties
                  embed.add_field(name="Type", value=f"`{TYPE}`", inline=True)
                  embed.add_field(name="Position", value=f"`{after.position}`", inline=True)
                  
                  # Add category if exists
                  if after.category:
                      embed.add_field(name="Category", value=f"`{after.category.name}`", inline=True)
                  else:
                      embed.add_field(name="Category", value="`None`", inline=True)
                  
                  # Add channel-specific details based on type
                  if hasattr(after, 'topic') and after.topic:
                      embed.add_field(name="Current Topic", value=f"`{after.topic}`", inline=False)
                  
                  if hasattr(after, 'slowmode_delay') and after.slowmode_delay > 0:
                      embed.add_field(name="Current Slowmode", value=f"`{after.slowmode_delay}s`", inline=True)
                  
                  if hasattr(after, 'nsfw'):
                      embed.add_field(name="Current NSFW", value=f"`{after.nsfw}`", inline=True)
                  
                  # Set author and timestamp
                  embed.set_author(name=f"{user.name}", icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
                  embed.set_footer(text=f"Channel ID: {after.id} • Server ID: {after.guild.id}")
                  embed.timestamp = discord.utils.utcnow()
                  
                  data = get_data(str(after.guild.id))
                  if not data or "channel" not in data or not data["channel"]:
                      return
                  
                  if "webhooks" in data and "channel" in data["webhooks"]:
                      webhook_url = data["webhooks"]["channel"]
                      success = await self.send_webhook_message(webhook_url, embed)
                      if success:
                          return
  
                  # Fallback to channel send if webhook fails
                  log_channel = self.bot.get_channel(int(data["channel"]))
                  if log_channel:
                      await log_channel.send(embed=embed)
                    
      except Exception as e:
          pass

  @commands.Cog.listener()
  async def on_member_update(self, before: discord.Member, after: discord.Member):
      if before.guild is None:
          return

      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute('SELECT channel_id, webhook_url FROM logs WHERE guild_id = ? AND log_type = "member"', (before.guild.id,))
      result = cursor.fetchone()
      conn.close()

      if not result:
          return
    
      channel_id, webhook_url = result
      if not channel_id or not webhook_url:
          return

      async with aiohttp.ClientSession() as session:
          webhook = discord.Webhook.from_url(webhook_url, session=session)
        
          if before.nick != after.nick:
              embed = discord.Embed(title="Member Nickname Updated", color=0x2f3136)
              embed.set_author(name=str(after), icon_url=after.display_avatar.url)
              embed.add_field(name="Before", value=before.nick or "None", inline=True)
              embed.add_field(name="After", value=after.nick or "None", inline=True)
              embed.set_footer(text=f"User ID: {after.id}")
              embed.timestamp = datetime.datetime.utcnow()
              await webhook.send(embed=embed)

          if before.roles != after.roles:
              added_roles = [role for role in after.roles if role not in before.roles]
              removed_roles = [role for role in before.roles if role not in after.roles]

              if added_roles or removed_roles:
                  embed = discord.Embed(title="Member Roles Updated", color=0x2f3136)
                  embed.set_author(name=str(after), icon_url=after.display_avatar.url)
                
                  if added_roles:
                      embed.add_field(name="Added Roles", value="\n".join([role.mention for role in added_roles]), inline=False)
                  if removed_roles:
                      embed.add_field(name="Removed Roles", value="\n".join([role.mention for role in removed_roles]), inline=False)
                
                  embed.set_footer(text=f"User ID: {after.id}")
                  embed.timestamp = datetime.datetime.utcnow()
                  await webhook.send(embed=embed)
          try:
            if before.avatar != after.avatar:
                embed = discord.Embed(title="Member Avatar Updated", color=0x2f3136)
                embed.set_author(name=str(after), icon_url=after.display_avatar.url)
                embed.add_field(name="Old Avatar", value=f"[Click Here]({before.display_avatar.url})")
                embed.add_field(name="New Avatar", value=f"[Click Here]({after.display_avatar.url})")
                embed.set_thumbnail(url=after.display_avatar.url)
                embed.set_footer(text=f"User ID: {after.id}")
                embed.timestamp = datetime.datetime.utcnow()
                await webhook.send(embed=embed)
          except Exception as e:
            print(f"Error sending avatar update log: {e}")
