from __future__ import annotations
import discord
import asyncio
import os
import logging
from discord.ext import commands
from utils.Tools import *
from discord.ext.commands import Context
from discord import app_commands
import time
import datetime
import re
from typing import *
from time import strftime
from core import Cog, Astroz, Context
from discord.ext import commands

logging.basicConfig(
  level=logging.INFO,
  format=
  "\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
  datefmt="%H:%M:%S",
)


def load_premium():
  with open('premium.json', 'r') as file:
    data = json.load(file)
  return data["premium_list"]


class Welcomer(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  def is_premium(ctx):
    premium_users = load_premium()
    return ctx.author.id in premium_users

  @commands.hybrid_group(name="autorole", invoke_without_command=True)
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @blacklist_check()
  @ignore_check()
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole(self, ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  @_autorole.command(name="config")
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(administrator=True)
  async def _ar_config(self, ctx):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      # Drop existing autorole table if it exists
      cursor.execute('DROP TABLE IF EXISTS autorole')
      
      # Create autorole table with the correct structure
      cursor.execute('''
        CREATE TABLE IF NOT EXISTS autorole (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          guild_id INTEGER NOT NULL,
          role_id INTEGER NOT NULL,
          type TEXT NOT NULL
        )
      ''')
      conn.commit()
      
      # Get human roles
      cursor.execute('SELECT role_id FROM autorole WHERE guild_id = ? AND type = ?', 
                    (ctx.guild.id, 'human'))
      human_roles = cursor.fetchall()
      
      # Get bot roles
      cursor.execute('SELECT role_id FROM autorole WHERE guild_id = ? AND type = ?', 
                    (ctx.guild.id, 'bot'))
      bot_roles = cursor.fetchall()
      
      conn.close()
      
      fetched_humans = []
      fetched_bots = []

      for role_data in human_roles:
        role = ctx.guild.get_role(int(role_data[0]))
        if role is not None:
          fetched_humans.append(role)

      for role_data in bot_roles:
        role = ctx.guild.get_role(int(role_data[0]))
        if role is not None:
          fetched_bots.append(role)

      hums = "\n".join(i.mention for i in fetched_humans)
      if not hums:
        hums = " Humans Autorole Not Set."

      bots = "\n".join(i.mention for i in fetched_bots)
      if not bots:
        bots = " Bots Autorole Not Set."

      emb = discord.Embed(color=0x2f3136,
                          title=f"Autorole of - {ctx.guild.name}").add_field(
                            name="__Humans__", value=hums,
                            inline=False).add_field(name="__Bots__",
                                                    value=bots,
                                                    inline=False)

      await ctx.send(embed=emb)
    except Exception as e:
      print(f"Error in autorole config: {e}")
      await ctx.send(f"An error occurred: {e}")

  @_autorole.group(name="reset", help="Clear autorole config for the server .")
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(administrator=True)
  async def _autorole_reset(self, ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  @_autorole_reset.command(name="humans",
                           help="Clear autorole config for the server .")
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(administrator=True)
  async def _autorole_humans_reset(self, ctx):
    data = getDB(ctx.guild.id)
    rl = data["autorole"]["humans"]
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
      if rl == []:
        embed = discord.Embed(
          description=
          "<:alert:1199317330790993960> | This server does not have any autoroles set up.",
          color=0x2f3136)
        await ctx.send(embed=embed)
      else:
        if rl != []:
          data["autorole"]["humans"] = []
          updateDB(ctx.guild.id, data)
          hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Successfully cleared all human autoroles for {ctx.guild.name}.",
            color=0x2f3136)
          await ctx.send(embed=hacker)
    else:
      hacker5 = discord.Embed(
        description=
        """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
        color=0x2f3136)
      hacker5.set_author(name=f"{ctx.author.name}",
                         icon_url=f"{ctx.author.avatar}")

      await ctx.send(embed=hacker5)

  @_autorole_reset.command(name="bots")
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(administrator=True)
  async def _autorole_bots_reset(self, ctx):
    data = getDB(ctx.guild.id)
    rl = data["autorole"]["bots"]
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
      if rl == []:
        embed = discord.Embed(
          description=
          f"<:alert:1199317330790993960> | This server does not have any autoroles set up.",
          color=0x2f3136)
        await ctx.send(embed=embed)
      else:
        if rl != []:
          data["autorole"]["bots"] = []
          updateDB(ctx.guild.id, data)
          hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Successfully cleared all bots autoroles for {ctx.guild.name}.",
            color=0x2f3136)
          await ctx.send(embed=hacker)
    else:
      hacker5 = discord.Embed(
        description=
        """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
        color=0x2f3136)
      hacker5.set_author(name=f"{ctx.author.name}",
                         icon_url=f"{ctx.author.avatar}")

      await ctx.send(embed=hacker5)

  @_autorole_reset.command(name="all")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole_reset_all(self, ctx):
    data = getDB(ctx.guild.id)
    brl = data["autorole"]["bots"]
    hrl = data["autorole"]["humans"]
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
      if len(brl) == 0 and len(hrl) == 0:
        embed = discord.Embed(
          description=
          f"<:alert:1199317330790993960> | This server does not have any autoroles set up.",
          color=0x2f3136)
        await ctx.send(embed=embed)
      else:
        if hrl != []:
          data["autorole"]["bots"] = []
          data["autorole"]["humans"] = []
          updateDB(ctx.guild.id, data)
          hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Succesfully cleared all autoroles settings for this server.",
            color=0x2f3136)
          await ctx.send(embed=hacker)
    else:
      hacker5 = discord.Embed(
        description=
        """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
        color=0x2f3136)
      hacker5.set_author(name=f"{ctx.author.name}",
                         icon_url=f"{ctx.author.avatar}")

      await ctx.send(embed=hacker5)

  @_autorole.group(name="humans", help="Setup autoroles for human users.")
  @blacklist_check()
  @ignore_check()
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole_humans(self, ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  @_autorole_humans.command(name="add",
                            help="Add role to list of autorole humans users.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole_humans_add(self, ctx, role: discord.Role):
    try:
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the role is already in autorole humans
        cursor.execute('SELECT COUNT(*) FROM autorole WHERE guild_id = ? AND role_id = ? AND type = ?', 
                      (ctx.guild.id, role.id, 'human'))
        count = cursor.fetchone()[0]
        
        # Count total human roles
        cursor.execute('SELECT COUNT(*) FROM autorole WHERE guild_id = ? AND type = ?', 
                      (ctx.guild.id, 'human'))
        total_roles = cursor.fetchone()[0]
        
        if total_roles >= 5:
          embed = discord.Embed(
            description=
            f"<:alert:1199317330790993960> | You have reached the maximum channel limit for autorole humans, which is five.",
            color=0x2f3136)
          await ctx.send(embed=embed)
        elif count > 0:
          embed1 = discord.Embed(
            description=
            "<:alert:1199317330790993960> | {} is already in human autoroles."
            .format(role.mention),
            color=0x2f3136)
          await ctx.send(embed=embed1)
        else:
          cursor.execute('INSERT INTO autorole (guild_id, role_id, type) VALUES (?, ?, ?)', 
                        (ctx.guild.id, role.id, 'human'))
          conn.commit()
          
          hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | {role.mention} has been added to human autoroles.",
            color=0x2f3136)
          await ctx.send(embed=hacker)
        
        conn.close()
      else:
        hacker5 = discord.Embed(
          description=
          """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
          color=0x2f3136)
        hacker5.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker5)
    except Exception as e:
      print(f"Error in autorole humans add: {e}")
      await ctx.send(f"An error occurred: {e}")

  @_autorole_humans.command(
    name="remove", help="Remove a role from autoroles for human users.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole_humans_remove(self, ctx, role: discord.Role):
    try:
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if there are any human roles
        cursor.execute('SELECT COUNT(*) FROM autorole WHERE guild_id = ? AND type = ?', 
                      (ctx.guild.id, 'human'))
        count = cursor.fetchone()[0]
        
        if count == 0:
          embed = discord.Embed(
            description=
            f"<:alert:1199317330790993960> | This server does not have any autoroles humans set up.",
            color=0x2f3136)
          await ctx.send(embed=embed)
        else:
          # Check if the role exists in autorole humans
          cursor.execute('SELECT COUNT(*) FROM autorole WHERE guild_id = ? AND role_id = ? AND type = ?', 
                        (ctx.guild.id, role.id, 'human'))
          role_exists = cursor.fetchone()[0]
          
          if role_exists == 0:
            embed1 = discord.Embed(
              description="{} is not in human autoroles.".format(role.mention),
              color=0x2f3136)
            await ctx.send(embed=embed1)
          else:
            cursor.execute('DELETE FROM autorole WHERE guild_id = ? AND role_id = ? AND type = ?', 
                          (ctx.guild.id, role.id, 'human'))
            conn.commit()
            
            hacker = discord.Embed(
              description=
              f"<:whitecheck:1243577701638475787> | {role.mention} has been removed from human autoroles.",
              color=0x2f3136)
            await ctx.send(embed=hacker)
        
        conn.close()
      else:
        hacker5 = discord.Embed(
          description=
          """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
          color=0x2f3136)
        hacker5.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker5)
    except Exception as e:
      print(f"Error in autorole humans remove: {e}")
      await ctx.send(f"An error occurred: {e}")

  @_autorole.group(name="bots", help="Setup autoroles for bots.")
  @blacklist_check()
  @ignore_check()
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole_bots(self, ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  @_autorole_bots.command(name="add",
                          help="Add role to list of autorole bot users.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole_bots_add(self, ctx, role: discord.Role):
    data = getDB(ctx.guild.id)
    rl = data["autorole"]["bots"]
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
      if len(rl) == 5:
        embed = discord.Embed(
          description=
          f"<:alert:1199317330790993960> | You have reached the maximum channel limit for autorole bots, which is five.",
          color=0x2f3136)
        await ctx.send(embed=embed)
      else:
        if str(role.id) in rl:
          embed1 = discord.Embed(
            description=
            "<:alert:1199317330790993960> | {} is already in bot autoroles."
            .format(role.mention),
            color=0x2f3136)
          await ctx.send(embed=embed1)
        else:
          rl.append(str(role.id))
          updateDB(ctx.guild.id, data)
          hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | {role.mention} has been added to bot autoroles.",
            color=0x2f3136)
          await ctx.send(embed=hacker)
    else:
      hacker5 = discord.Embed(
        description=
        """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
        color=0x2f3136)
      hacker5.set_author(name=f"{ctx.author.name}",
                         icon_url=f"{ctx.author.avatar}")

      await ctx.send(embed=hacker5)

  @_autorole_bots.command(name="remove",
                          help="Remove a role from autoroles for bot users.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _autorole_bots_remove(self, ctx, role: discord.Role):
    data = getDB(ctx.guild.id)
    rl = data["autorole"]["bots"]
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
      if len(rl) == 0:
        embed = discord.Embed(
          description=
          f"<:alert:1199317330790993960> | This server dose not have any autoroles humans set up.",
          color=0x2f3136)
        await ctx.send(embed=embed)
      else:
        if str(role.id) not in rl:
          embed1 = discord.Embed(
            description=
            "<:alert:1199317330790993960> | {} is not in bot autoroles.".
            format(role.mention),
            color=0x2f3136)
          await ctx.send(embed=embed1)
        else:
          rl.remove(str(role.id))
          updateDB(ctx.guild.id, data)
          hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | {role.mention} has been removed from bot autoroles.",
            color=0x2f3136)
          await ctx.send(embed=hacker)
    else:
      hacker5 = discord.Embed(
        description=
        """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
        color=0x2f3136)
      hacker5.set_author(name=f"{ctx.author.name}",
                         icon_url=f"{ctx.author.avatar}")

      await ctx.send(embed=hacker5)

  @commands.hybrid_group(name="greet",
                  aliases=['welcome'],
                  invoke_without_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet(self, ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  



  @_greet.command(name="thumbnail", help="Setups welcome thumbnail.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  
  async def _greet_thumbnail(self, ctx, thumbnail_link):
    data = getDB(ctx.guild.id)
    streamables = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        if streamables.search(thumbnail_link):
            data["welcome"]["thumbnail"] = thumbnail_link
            updateDB(ctx.guild.id, data)
            hacker = discord.Embed(
                color=0x2f3136,
                description="<:whitecheck:1243577701638475787> | Successfully updated the welcome thumbnail URL."
            )
            hacker.set_author(
                name=f"{ctx.author.name}",
                icon_url=f"{ctx.author.avatar}"
            )
            await ctx.send(embed=hacker)
        else:
            await ctx.send("Oops, kindly provide a valid link.")
    else:
        hacker5 = discord.Embed(
            description="""```diff
- You must have Administrator permission. - Your top role should be above my top role.
```""",
            color=0x2f3136
        )
        hacker5.set_author(
            name=f"{ctx.author.name}",
            icon_url=f"{ctx.author.avatar}"
        )
        await ctx.send(embed=hacker5)

  @_greet.command(name="image", help="Setups welcome image.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  
  async def _greet_image(self, ctx, *, image_link):
    data = getDB(ctx.guild.id)
    streamables = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )

    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        if streamables.search(image_link):
            data["welcome"]["image"] = image_link
            updateDB(ctx.guild.id, data)
            hacker = discord.Embed(
                color=0x2f3136,
                description="<:whitecheck:1243577701638475787> | Successfully updated the welcome image URL."
            )
            hacker.set_author(
                name=f"{ctx.author.name}",
                icon_url=f"{ctx.author.avatar}"
            )
            await ctx.send(embed=hacker)
        else:
            await ctx.send("Oops, kindly provide a valid link.")
    else:
        hacker5 = discord.Embed(
            description="""```diff
- You must have Administrator permission. - Your top role should be above my top role.
```""",
            color=0x2f3136
        )
        hacker5.set_author(
            name=f"{ctx.author.name}",
            icon_url=f"{ctx.author.avatar}"
        )
        await ctx.send(embed=hacker5)


  @_greet_thumbnail.error
  async def greet_thumbnail_error(self, ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            description="This command is for premium users only. Click [here](https://discord.gg/encoders-community-1058660812182519921) to subscribe to premium.",
            color=0x2f3136
        )
        button1 = discord.ui.Button(label="Premium",
                               style=discord.ButtonStyle.url,
                               url="https://discord.gg/encoders-community-1058660812182519921")
        view = discord.ui.View()
        view.add_item(button1)
        await ctx.send(embed=embed, view=view)

  @_greet_image.error
  async def greet_image_error(self, ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            description="This command is for premium users only. Click [here](https://discord.gg/encoders-community-1058660812182519921) to subscribe to premium.",
            color=0x2f3136
        )
        button1 = discord.ui.Button(label="Premium",
                               style=discord.ButtonStyle.url,
                               url="https://discord.gg/encoders-community-1058660812182519921")
        view = discord.ui.View()
        view.add_item(button1)
        await ctx.send(embed=embed, view=view)

  @_greet.command(name="autodel", help="Automatically delete message after x seconds.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet_autodel(self, ctx, autodelete_second: int):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('''
        CREATE TABLE IF NOT EXISTS welcome (
          guild_id INTEGER PRIMARY KEY,
          channel TEXT DEFAULT '[]',
          message TEXT DEFAULT '<<user.mention>> Welcome To <<server.name>>',
          embed INTEGER DEFAULT 1,
          ping INTEGER DEFAULT 0,
          image TEXT DEFAULT '',
          thumbnail TEXT DEFAULT '',
          footer TEXT DEFAULT '',
          autodel INTEGER DEFAULT 0
        )
      ''')
      
      cursor.execute('''
        CREATE TABLE IF NOT EXISTS autorole (
          guild_id INTEGER PRIMARY KEY,
          humans TEXT DEFAULT '[]',
          bots TEXT DEFAULT '[]'
        )
      ''')
      
      cursor.execute('SELECT * FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
      result = cursor.fetchone()
      
      if result:
        cursor.execute('UPDATE welcome SET autodel = ? WHERE guild_id = ?', 
                      (autodelete_second, ctx.guild.id))
      else:
        cursor.execute('''
          INSERT INTO welcome (guild_id, channel, message, embed, ping, image, thumbnail, footer, autodel)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ctx.guild.id, '[]', '<<user.mention>> Welcome To <<server.name>>', 1, 0, '', '', '', autodelete_second))
      
      conn.commit()
      conn.close()
      
      hacker = discord.Embed(
        color=0x2f3136,
        description=
        f"<:whitecheck:1243577701638475787> | Successfully updated the welcome autodelete second to {autodelete_second}.\n From now on, Welcome message will be deleted after {autodelete_second} seconds.",
        timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author.name}",
                        icon_url=f"{ctx.author.avatar}")
      await ctx.send(embed=hacker)
    except Exception as e:
      print(f"Error in autodel: {e}")
      await ctx.send(f"An error occurred: {e}")

  @_greet.command(name="message", help="Setups welcome message.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet_message(self, ctx: commands.Context):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('''
        CREATE TABLE IF NOT EXISTS welcome (
          guild_id INTEGER PRIMARY KEY,
          channel TEXT DEFAULT '[]',
          message TEXT DEFAULT '<<user.mention>> Welcome To <<server.name>>',
          embed INTEGER DEFAULT 1,
          ping INTEGER DEFAULT 0,
          image TEXT DEFAULT '',
          thumbnail TEXT DEFAULT '',
          footer TEXT DEFAULT '',
          autodel INTEGER DEFAULT 0
        )
      ''')
      
      def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        msg = discord.Embed(
          color=0x2f3136,
          description=
          """Here are some keywords you can use in your welcome message.\n\nSend your welcome message in this channel now.\n\n\n```xml\n<<server.member_count>> = server member count\n<<server.name>> = server name\n<<user.name>> = username of new member\n<<user.mention>> = mention of the new user\n<<user.created_at>> = creation time of account of user\n<<user.joined_at>> = joining time of the user.\n```"""
        )
        await ctx.send(embed=msg)
        try:
          welcmsg = await self.bot.wait_for('message', check=check, timeout=40.0)
        except asyncio.TimeoutError:
          await ctx.send("Oops, you took so long to respond. Please run the command again and be faster.")
          return
        else:
          cursor.execute('SELECT * FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
          result = cursor.fetchone()
          
          if result:
            cursor.execute('UPDATE welcome SET message = ? WHERE guild_id = ?', 
                          (welcmsg.content, ctx.guild.id))
          else:
            cursor.execute('''
              INSERT INTO welcome (guild_id, channel, message, embed, ping, image, thumbnail, footer, autodel)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ctx.guild.id, '[]', welcmsg.content, 1, 0, '', '', '', 0))
          
          conn.commit()
          conn.close()
          
          hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | Successfully updated the welcome message."
          )
          hacker.set_author(name=f"{ctx.author.name}",
                            icon_url=f"{ctx.author.avatar}")
          await ctx.send(embed=hacker)
      else:
        hacker5 = discord.Embed(description="""```diff
 - You must have Administrator permission. - Your top role should be above my top role. 
```""",
                                color=0x2f3136)
        hacker5.set_author(name=f"{ctx.author.name}",
                           icon_url=f"{ctx.author.avatar}")

        await ctx.send(embed=hacker5)
    except Exception as e:
      print(f"Error in greet message: {e}")
      await ctx.send(f"An error occurred: {e}")
      
  @_greet.command(name="footer", help="Set greet footer message.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def set_greet_footer(self, ctx, *, footer_message):
    data = getDB(ctx.guild.id)

    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        data["welcome"]["footer"] = footer_message
        updateDB(ctx.guild.id, data)

        response = discord.Embed(
            color=0x2f3136,
            description="<:whitecheck:1243577701638475787> | Successfully updated the greet footer message."
        )
        response.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar
        )
        await ctx.send(embed=response)
    else:
        response = discord.Embed(
            description="""```diff
- You must have Administrator permission.
- Your top role should be above my top role.
```""",
            color=0x2f3136
        )
        response.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar
        )
        await ctx.send(embed=response)

  @_greet.command(name="embed", help="Toggle embed for greet message .")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet_embed(self, ctx):
    data = getDB(ctx.guild.id)
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
      if data["welcome"]["embed"] == True:
        data["welcome"]["embed"] = False
        updateDB(ctx.guild.id, data)
        hacker = discord.Embed(
          color=0x2f3136,
          description=
          f"<:whitecheck:1243577701638475787> | Successfully disabled message embed, welcome message will be a plain message."
        )
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker)
      elif data["welcome"]["embed"] == False:
        data["welcome"]["embed"] = True
        updateDB(ctx.guild.id, data)
        hacker1 = discord.Embed(
          color=0x2f3136,
          description=
          f"<:whitecheck:1243577701638475787> | Successfully enabled message embed, welcome message will be an embeded message now."
        )
        hacker1.set_author(name=f"{ctx.author.name}",
                           icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker1)
    else:
      hacker5 = discord.Embed(description="""```diff
 - You must have Administrator permission. - Your top role should be above my top role. 
```""",
                              color=0x2f3136)
      hacker5.set_author(name=f"{ctx.author.name}",
                         icon_url=f"{ctx.author.avatar}")

      await ctx.send(embed=hacker5)

  @_greet.command(name="ping", help="Toggle embed ping for welcomer.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet_ping(self, ctx):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT ping FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
      result = cursor.fetchone()
      
      if not result:
        cursor.execute('''
          INSERT INTO welcome (guild_id, channel, message, embed, ping, image, thumbnail, footer, autodel)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ctx.guild.id, '[]', '<<user.mention>> Welcome To <<server.name>>', 1, 0, '', '', '', 0))
        conn.commit()
        current_ping = 0
      else:
        current_ping = result[0]
      
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        if current_ping == 1:
          cursor.execute('UPDATE welcome SET ping = ? WHERE guild_id = ?', (0, ctx.guild.id))
          conn.commit()
          
          hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | Successfully disabled embed ping. I won't mention users now."
          )
          hacker.set_author(name=f"{ctx.author.name}",
                            icon_url=f"{ctx.author.avatar}")
          await ctx.send(embed=hacker)
        else:
          cursor.execute('UPDATE welcome SET ping = ? WHERE guild_id = ?', (1, ctx.guild.id))
          conn.commit()
          
          hacker1 = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | Successfully enabled embed ping, I will mention new users outside the embed."
          )
          hacker1.set_author(name=f"{ctx.author.name}",
                             icon_url=f"{ctx.author.avatar}")
          await ctx.send(embed=hacker1)
      else:
        hacker5 = discord.Embed(description="""```diff
 - You must have Administrator permission. - Your top role should be above my top role. 
```""",
                                color=0x2f3136)
        hacker5.set_author(name=f"{ctx.author.name}",
                           icon_url=f"{ctx.author.avatar}")

        await ctx.send(embed=hacker5)
      
      conn.close()
    except Exception as e:
      print(f"Error in greet ping: {e}")
      await ctx.send(f"An error occurred: {e}")

  @_greet.group(name="channel", help="Setups welcome channel.")
  @blacklist_check()
  @ignore_check()
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet_channel(self, ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  @_greet_channel.command(name="add",
                          help="Add a channel to the welcome channels list.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet_channel_add(self, ctx, channel: discord.TextChannel):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT channel FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
      result = cursor.fetchone()
      
      chh = json.loads(result[0]) if result else []
      
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        if len(chh) >= 1:
          hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:alert:1199317330790993960> | You have reached the maximum channel limit for channels, which is one."
          )
          hacker.set_author(name=f"{ctx.author.name}",
                            icon_url=f"{ctx.author.avatar}")
          await ctx.send(embed=hacker)
        else:
          if str(channel.id) in chh:
            hacker1 = discord.Embed(
              color=0x2f3136,
              description=
              f"<:alert:1199317330790993960> | This channel is already in the welcome channels list."
            )
            hacker1.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=hacker1)
          else:
            chh.append(str(channel.id))
            cursor.execute('UPDATE welcome SET channel = ? WHERE guild_id = ?', (json.dumps(chh), ctx.guild.id))
            conn.commit()
            
            hacker4 = discord.Embed(
              color=0x2f3136,
              description=
              f"<:whitecheck:1243577701638475787> | Successfully added {channel.mention} to welcome channel list. I will greet new users in {channel.mention}.")
            hacker4.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=hacker4)
      
      conn.close()
    except Exception as e:
      print(f"Error in greet channel add: {e}")
      await ctx.send(f"An error occurred: {e}")

  @_greet_channel.command(name="remove",
                          help="Remove a channel from welcome channels list.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def _greet_channel_remove(self, ctx, channel: discord.TextChannel):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT channel FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
      result = cursor.fetchone()
      
      chh = json.loads(result[0]) if result else []
      
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        if len(chh) == 0:
          hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:alert:1199317330790993960> | This server does not have any welcome channel set up."
          )
          hacker.set_author(name=f"{ctx.author.name}",
                            icon_url=f"{ctx.author.avatar}")
          await ctx.send(embed=hacker)
        else:
          if str(channel.id) not in chh:
            hacker1 = discord.Embed(
              color=0x2f3136,
              description=
              f"<:alert:1199317330790993960> | This channel is not in the welcome channels list."
            )
            hacker1.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=hacker1)
          else:
            chh.remove(str(channel.id))
            cursor.execute('UPDATE welcome SET channel = ? WHERE guild_id = ?', (json.dumps(chh), ctx.guild.id))
            conn.commit()
            
            hacker3 = discord.Embed(
              color=0x2f3136,
              description=
              f"<:whitecheck:1243577701638475787> | Successfully removed {channel.mention} from welcome channel list."
            )
            hacker3.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=hacker3)
      
      conn.close()
    except Exception as e:
      print(f"Error in greet channel remove: {e}")
      await ctx.send(f"An error occurred: {e}")

  @_greet.command(name="test", help="Test the welcome message how it will look like.")
  @blacklist_check()
  @ignore_check()
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def welctestt(self, ctx):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT * FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
      result = cursor.fetchone()
      
      if not result:
        await ctx.send(embed=discord.Embed(
          color=0x2f3136,
          description=":warning: Uh oh, It looks like this server does not have any welcome channel set up."
        ).set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}"))
        return
      
      msg = result[2]
      chan = json.loads(result[1])
      emtog = bool(result[3])
      emping = bool(result[4])
      emimage = result[5]
      emthumbnail = result[6]
      emfooter = result[7]
      emautodel = result[8]
      user = ctx.author

      placeholders_msg = {
        "<<server.name>>": ctx.guild.name,
        "<<server.member_count>>": ctx.guild.member_count,
        "<<user.name>>": str(user),
        "<<user.mention>>": user.mention,
        "<<user.created_at>>": f"<t:{int(user.created_at.timestamp())}:F>",
        "<<user.joined_at>>": f"<t:{int(user.joined_at.timestamp())}:F>"
      }
      for placeholder, value in placeholders_msg.items():
        msg = msg.replace(placeholder, str(value))

      placeholders_footer = {
        "<<server.member_count>>": ctx.guild.member_count,
        "<<server.name>>": ctx.guild.name,
        "<<user.name>>": str(user)
      }
      for placeholder, value in placeholders_footer.items():
        emfooter = emfooter.replace(placeholder, str(value))

      if emping:
        emping = f"{user.mention}"
      else:
        emping = ""

      em = discord.Embed(description=msg, color=0x2f3136)
      em.set_author(name=user.name, icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
      em.timestamp = discord.utils.utcnow()

      if emimage:
        em.set_image(url=emimage)

      if emthumbnail:
        em.set_thumbnail(url=emthumbnail)

      if ctx.guild.icon:
        em.set_footer(text=emfooter, icon_url=ctx.guild.icon.url)

      for channel_id in chan:
        channel = self.bot.get_channel(int(channel_id))
        if channel:
          if emtog:
            sent = await channel.send(emping, embed=em)
          else:
            sent = await channel.send(msg)

      if emautodel:
        await sent.delete(delay=int(emautodel))

      conn.close()

    except Exception as e:
      print(f"Error in welctestt: {e}")

  @_greet.command(name="config", help="Get greet config for the server.")
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(administrator=True)
  async def _config(self, ctx):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT * FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
      result = cursor.fetchone()
      
      if not result:
        await ctx.reply(
          "First, set up your greet channel by running `greet channel add #channel/id`."
        )
        return
      
      msg = result[2]
      emfooter = result[7]
      chan = json.loads(result[1])
      emtog = bool(result[3])
      emping = bool(result[4])
      emimage = result[5]
      emthumbnail = result[6]
      emautodel = result[8]

      embed = discord.Embed(color=0x2f3136,
                            title=f"Welcome Config For {ctx.guild.name}")
      em = "Enabled" if emtog else "Disabled"
      ping = "Enabled" if emping else "Disabled"
        
      ch_mentions = []
      for chh in chan:
        channel = self.bot.get_channel(int(chh))
        if channel:
          ch_mentions.append(channel.mention)
      
      channel_display = ", ".join(ch_mentions) if ch_mentions else "None"
      embed.add_field(name="**Welcome Channel:**", value=channel_display)
      embed.add_field(name="**Welcome Message:**", value=f"{msg}")
      embed.add_field(name="**Welcome Footer:**", value=f"{emfooter if emfooter else 'Not set'}")
      embed.add_field(name="**Welcome Embed:**", value=em)
      embed.add_field(name="**Welcome Ping:**", value=f"{ping}")
      embed.add_field(name="**Welcome Image:**", value=emimage if emimage else "Not set")
      embed.add_field(name="**Welcome Thumbnail:**", value=emthumbnail if emthumbnail else "Not set")
      embed.add_field(name="**Auto Delete After:**", value=f"{emautodel} seconds" if emautodel else "Not set")
      
      if ctx.guild.icon is not None:
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.set_thumbnail(url=ctx.guild.icon.url)

      await ctx.send(embed=embed)

      conn.close()

    except Exception as e:
      print(f"Error in greet config: {e}")

  @_greet.command(name="reset", help="Clear greet config for the server.")
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(administrator=True)
  async def _reset(self, ctx):
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      
      cursor.execute('SELECT * FROM welcome WHERE guild_id = ?', (ctx.guild.id,))
      result = cursor.fetchone()
      
      if not result or json.loads(result[1]) == []:
        embed = discord.Embed(
          description=
          "<:alert:1199317330790993960> | This server does not have any greet channel set up.",
          color=0x2f3136)
        await ctx.send(embed=embed)
      else:
        cursor.execute('UPDATE welcome SET channel = ?, image = ?, message = ?, thumbnail = ?, footer = ? WHERE guild_id = ?', 
                      ('[]', '', '<<user.mention>> Welcome to <<server.name>>', '', '', ctx.guild.id))
        conn.commit()
        
        hacker = discord.Embed(
          description=
          "<:whitecheck:1243577701638475787> | Successfully cleared all greet config for this server.",
          color=0x2f3136)
        await ctx.send(embed=hacker)

      conn.close()

    except Exception as e:
      print(f"Error in _reset: {e}")