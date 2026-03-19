import discord
import asyncio
import datetime
from discord import User, errors
import re
import typing
import sqlite3
import typing as t
from typing import *
from discord.ext.commands import has_permissions, MissingPermissions, has_role, has_any_role
from discord.ext.commands.cooldowns import BucketType
from utils.Tools import *
from core import Cog, Astroz, Context
from discord.ext.commands import Converter
from discord.ext.commands import Context
from discord.ext import commands, tasks
from discord.ui import Button, View
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator


time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def convert(argument):
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for key, value in matches:
        try:
            time += time_dict[value] * float(key)
        except KeyError:
            raise commands.BadArgument(
                f"{value} is an invalid time key! h|m|s|d are valid arguments")
        except ValueError:
            raise commands.BadArgument(f"{key} is not a number!")
    return round(time)


class Lower(Converter):

    async def convert(self, ctx: Context, argument: str):
        return argument.lower()

class PaginatorView(discord.ui.View):
    def __init__(self, embeds):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = 0
        self.message = None
    
    @discord.ui.button(label="Back", style=discord.ButtonStyle.success)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.success)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])
        else:
            await interaction.response.defer()
    
    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.tasks = []
        self.conn = sqlite3.connect('punishments.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bans (
                user_id INTEGER,
                guild_id INTEGER,
                reason TEXT,
                unban_time TIMESTAMP,
                status TEXT,
                PRIMARY KEY (user_id, guild_id)
            )
        ''')
        self.conn.commit()
        self.bot.loop.create_task(self.check_unbans())

    async def check_unbans(self):
        while True:
            await asyncio.sleep(60)
            now = datetime.datetime.utcnow()
            self.cursor.execute('SELECT user_id, guild_id FROM bans WHERE unban_time <= ? AND status = ?', (now, 'banned'))
            rows = self.cursor.fetchall()
            for row in rows:
                user_id, guild_id = row
                user = await self.bot.fetch_user(user_id)
                guild = self.bot.get_guild(guild_id)
                if guild:
                    await guild.unban(user, reason="Automatic unban")
                    self.cursor.execute('UPDATE bans SET status = ? WHERE user_id = ? AND guild_id = ?', ('unbanned', user_id, guild_id))
                    self.conn.commit()

    def convert(self, time):
        pos = ["s", "m", "h", "d"]
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
        unit = time[-1]
        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2
        return val * time_dict[unit]

    @commands.command()
    async def enlarge(self, ctx, emoji: discord.Emoji):
        ''' Enlarge any emoji '''
        url = emoji.url
        await ctx.send(url)

    
    @commands.hybrid_command(name="unlockall",
                      help="Unlocks down the server.",
                      usage="unlockall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def unlockall(self,
                        ctx,
                        server: discord.Guild = None,
                        *,
                        reason=None):
        hacker = discord.Embed(
            color=0x2f3136,
            description=
            "<:whitecheck:1243577701638475787> | Unlocking all channels in few seconds .")
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        await ctx.reply(embed=hacker)
        if server is None: server = ctx.guild
        try:
            for channel in server.channels:
                await channel.set_permissions(
                    ctx.guild.default_role,
                    overwrite=discord.PermissionOverwrite(send_messages=True,
                                                          read_messages=True),
                    reason=reason)
        except:
            embed = discord.Embed(
                color=0x2f3136, description=f"**Failed to unlock, {server}.**")
            embed.set_author(name=f"{ctx.author.name}",
                             icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)
        else:
            pass

    @commands.hybrid_command(name="lockall",
                      help="Locks down the server.",
                      usage="lockall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def lockall(self, ctx, server: discord.Guild = None, *, reason=None):
        hacker = discord.Embed(
            color=0x2f3136,
            description=
            "<:whitecheck:1243577701638475787> | Locking all channels in few seconds .")
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        await ctx.reply(embed=hacker)
        if server is None: server = ctx.guild
        try:
            for channel in server.channels:
                await channel.set_permissions(
                    ctx.guild.default_role,
                    overwrite=discord.PermissionOverwrite(send_messages=False,
                                                          read_messages=True),
                    reason=reason)
        except:
            embed = discord.Embed(
                color=0x2f3136,
                description=f"**Failed to lockdown, {server}.**")
            embed.set_author(name=f"{ctx.author.name}",
                             icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)
        else:
            pass



    @commands.hybrid_command(name="give",
                      help="Gives the mentioned user a role.",
                      usage="give <user> <role>",
                      aliases=["addrole"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def give(
        self,
        ctx,
        member: discord.Member,
        role: discord.Role,
    ):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            if role not in member.roles:
                try:
                    hacker1 = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Changed roles for {member.name}, added {role.name}",
                color=0x2f3136)
                    await member.add_roles(role,reason=f"{ctx.author} (ID: {ctx.author.id})")
                    await ctx.send(embed=hacker1)
                except:
                    pass
            elif role in member.roles:
                try:
                    hacker = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Changed roles for {member.name}, removed {role.name}",
                color=0x2f3136)
                    await member.remove_roles(role,reason=f"{ctx.author} (ID: {ctx.author.id})")
                    await ctx.send(embed=hacker)
                except:
                    pass
        else:
            hacker5 = discord.Embed(
                description=
                """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.avatar}")

            await ctx.send(embed=hacker5)

    @commands.hybrid_command(name="hideall", help="Hides all the channels .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def _hideall(self, ctx):
        hacker = discord.Embed(
            color=0x2f3136,
            description=
            "<:whitecheck:1243577701638475787> | Hiding all channels in few seconds .")
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        #hacker.set_thumbnail(url =f"{ctx.author.avatar}")
        await ctx.reply(embed=hacker)
        for x in ctx.guild.channels:
            await x.set_permissions(ctx.guild.default_role, view_channel=False)

    @commands.hybrid_command(name="unhideall", help="Unhides all the channels .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def _unhideall(self, ctx):
        hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | Unhiding all channels in few seconds .")
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        #hacker.set_thumbnail(url =f"{ctx.author.avatar}")
        await ctx.reply(embed=hacker)
        for x in ctx.guild.channels:
            await x.set_permissions(ctx.guild.default_role, view_channel=True)

    @commands.hybrid_command(name="hide", help="Hides the channel")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _hide(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role,
                                      overwrite=overwrite,
                                      reason=f"Channel Hidden By {ctx.author}")
        hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | Succefully Hidden {channel.mention} .")
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        
        await ctx.reply(embed=hacker)

    @commands.hybrid_command(name="unhide", help="Unhides the channel")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _unhide(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = True
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite,
            reason=f"Channel Unhidden By {ctx.author}")
        hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | Succefully Unhidden {channel.mention} .")
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        
        await ctx.reply(embed=hacker)

    @commands.hybrid_command(
        name="audit", help="See recents audit log action in the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(view_audit_log=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def auditlog(self, ctx, limit: int):
        if limit >= 31:
            await ctx.reply(
                "Action rejected, you are not allowed to fetch more than `30` entries.",
                mention_author=False)
            return
        idk = []
        str = ""
        async for entry in ctx.guild.audit_logs(limit=limit):
            idk.append(f'''User: `{entry.user}`
Action: `{entry.action}`
Target: `{entry.target}`
Reason: `{entry.reason}`\n\n''')
        for n in idk:
            str += n
        str = str.replace("AuditLogAction.", "")
        embed = discord.Embed(title=f"Audit Logs Of {ctx.guild.name}",
                              description=f">>> {str}",
                              color=0x2f3136)
        embed.set_footer(text=f"Audit Log Actions For {ctx.guild.name}")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="prefix",
        aliases=["setprefix", "prefixset"],
        help="Allows you to change prefix of the bot for this server")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _prefix(self, ctx: commands.Context, prefix):
      data = getConfig(ctx.guild.id)
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:         
          data["prefix"] = str(prefix)
          updateConfig(ctx.guild.id, data)
          await ctx.reply(embed=discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Successfully Changed Prefix For **{ctx.guild.name}**\nNew Prefix for **{ctx.guild.name}** is : `{prefix}`\nUse `{prefix}help` For More info .",
            color=0x2f3136))
      else:
          hacker5 = discord.Embed(
                description=
                """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
                color=0x2f3136)
          hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")

          await ctx.send(embed=hacker5)
            



    @commands.hybrid_group(invoke_without_command=True,
                    help="Clears the messages",
                    usage="purge <amount>")
    @commands.has_guild_permissions(manage_messages=True)
    @blacklist_check()
    @ignore_check()
    async def purge(self, ctx, amount: int = 10):
        if amount > 1000:
            return await ctx.send(
                "Purge limit exceeded. Please provide an integer which is less than or equal to 1000."
            )
        deleted = await ctx.channel.purge(limit=amount + 1)
        message = await ctx.send(f"**<:whitecheck:1243577701638475787> Deleted {len(deleted)-1} message(s)**")
        await asyncio.sleep(4)
        await message.delete()

              

  

    @purge.command(help="Clears the messages starts with the given letters",
                   usage="purge startswith <text>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def startswith(self, ctx, key, amount: int = 10):
        if amount > 1000:
            return await ctx.send(
                "Purge limit exceeded. Please provide an integer which is less than or equal to 1000."
            )
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.content.startswith(key):
                counter += 1
                return True
            else:
                return False

        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(
            f"**<:whitecheck:1243577701638475787> Deleted {len(deleted)}/{amount} message(s) which started with the given keyword**"
        )

    @purge.command(help="Clears the messages ends with the given letter",
                   usage="purge endswith <text>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def endswith(self, ctx, key, amount: int = 10):
        if amount > 1000:
            return await ctx.send(
                "Purge limit exceeded. Please provide an integer which is less than or equal to 1000."
            )
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.content.endswith(key):
                counter += 1
                return True
            else:
                return False

        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(
            f"**<:whitecheck:1243577701638475787> Deleted {len(deleted)}/{amount} message(s) which ended with the given keyword**"
        )

    @purge.command(help="Clears the messages contains with the given argument",
                   usage="purge contains <message>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def contains(self, ctx, key, amount: int = 10):
        if amount > 1000:
            return await ctx.send(
                "Purge limit exceeded. Please provide an integer which is less than or equal to 1000."
            )
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if key in m.content:
                counter += 1
                return True
            else:
                return False

        deleted = await ctx.channel.purge(limit=100, check=check)
        message = await ctx.send(
            f"**<:whitecheck:1243577701638475787> Deleted {len(deleted)}/{amount} message(s) which contained the given keyword**"
        )
        await asyncio.sleep(4)
        await message.delete()

    @purge.command(help="Clears the messages of the given user",
                   usage="purge <user>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def user(self, ctx, user: discord.Member, amount: int = 10):
        if amount > 1000:
            return await ctx.send(
                "Purge limit exceeded. Please provide an integer which is less than or equal to 1000."
            )
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.author.id == user.id:
                counter += 1
                return True
            else:
                return False

        deleted = await ctx.channel.purge(limit=100, check=check)
        message = await ctx.send(
            f"**<:whitecheck:1243577701638475787> Deleted {len(deleted)}/{amount} message(s) which were sent by the mentioned user**"
        )
        await asyncio.sleep(4)
        await message.delete()

    @purge.command(help="Clears the messages containing invite links",
                   usage="purge invites")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def invites(self, ctx, amount: int = 10):
        if amount > 1000:
            return await ctx.send(
                "Purge limit exceeded. Please provide an integer which is less than or equal to 1000."
            )
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if "discord.gg/" in m.content.lower():
                counter += 1
                return True
            else:
                return False

        deleted = await ctx.channel.purge(limit=100, check=check)
        message = await ctx.send(
            f"**<:whitecheck:1243577701638475787> Deleted {len(deleted)}/{amount} message(s) which contained invites**"
        )
        await asyncio.sleep(4)
        await message.delete()

    @commands.hybrid_command(name="mute",
                             description="Timeouts someone for specific time.",
                             usage="mute <member> <time>",
                             aliases=["timeout", "to", "stfu"])
    @commands.cooldown(1, 20, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(moderate_members=True)
    async def _mute(self, ctx, member: discord.Member, duration):
        try:
            ok = duration[:-1]
            tame = self.convert(duration)
            till = duration[-1]
            if tame == -1:
                hacker3 = discord.Embed(
                color=0x2f3136,
                description=
                f"<:alert:1199317330790993960> | Invalid time unit. Please enter correct time.\n\nExamples:\n{ctx.prefix}mute{ctx.author} 1h",
                timestamp=ctx.message.created_at)
                await ctx.reply(embed=hacker3, mention_author=False)
            elif tame == -2:
                hacker4 = discord.Embed(
                color=0x2f3136,
                description=
                f"<:alert:1199317330790993960> | Time must be an integer!",
                timestamp=ctx.message.created_at)
                await ctx.reply(embed=hacker4, mention_author=False)
            else:
                if till.lower() == "d":
                    t = datetime.timedelta(seconds=tame)
                    hacker = discord.Embed(
                    color=0x2f3136,
                    description=
                    "<:whitecheck:1243577701638475787> | Successfully Muted {0.mention} For {1} Day(s)"
                    .format(member, ok))
                elif till.lower() == "m":
                    t = datetime.timedelta(seconds=tame)
                    hacker = discord.Embed(
                    color=0x2f3136,
                    description=
                    "<:whitecheck:1243577701638475787> | Successfully Muted {0.mention} For {1} Minute(s)"
                    .format(member, ok))
                
                elif till.lower() == "s":
                    t = datetime.timedelta(seconds=tame)
                    hacker = discord.Embed(
                    color=0x2f3136,
                    description=
                    "<:whitecheck:1243577701638475787> | Successfully Muted {0.mention} For {1} Second(s)"
                    .format(member, ok))
                
                elif till.lower() == "h":
                    t = datetime.timedelta(seconds=tame)
                    hacker = discord.Embed(
                    color=0x2f3136,
                    description=
                    "<:whitecheck:1243577701638475787> | Successfully Muted {0.mention} For {1} Hour(s)"
                    .format(member, ok))
            try:
                if member.guild_permissions.administrator:
                    hacker1 = discord.Embed(
                    color=0x2f3136,
                    description=
                    "<:alert:1199317330790993960> | Administrators cannot be muted.")
                    await ctx.reply(embed=hacker1)
                else:
                    timestamp = int(datetime.datetime.utcnow().timestamp())
                    reason = f"Timeout by {ctx.author} ({ctx.author.id})"
                    
                    self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS timeouts (
                        user_id INTEGER,
                        guild_id INTEGER,
                        reason TEXT,
                        duration TEXT,
                        timestamp INTEGER
                    )
                    ''')
                    
                    self.cursor.execute(
                        'INSERT INTO timeouts (user_id, guild_id, reason, duration, timestamp) VALUES (?, ?, ?, ?, ?)',
                        (member.id, ctx.guild.id, reason, duration, timestamp)
                    )
                    self.conn.commit()
                    
                    await member.timeout(discord.utils.utcnow() + t,
                                     reason="Mute command by: {0}".format(
                                         ctx.author))
                    await ctx.send(embed=hacker)
                    
            except:
                pass
        except discord.NotFound:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> User not found.")
            await ctx.send(embed=error, delete_after=10)

        except discord.Forbidden:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> I do not have necessary permissions to `timeout` members.")
            await ctx.send(embed=error, delete_after=5)

        except:
            pass
            

    @commands.hybrid_command(name="unmute",
                             description="Unmutes a member .",
                             aliases=["removetimeout", "rto"],
                             usage="unmute <member>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 20, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        try:
            if member.is_timed_out():
                try:
                    await member.edit(timed_out_until=None)
                    hacker5 = discord.Embed(
                    color=0x2f3136,
                    description=
                    f"<:whitecheck:1243577701638475787> | Successfully Unmuted {member.name}")
                    await ctx.reply(embed=hacker5)
                except Exception as e:
                    hacker = discord.Embed(
                    color=0x2f3136,
                    description=
                    "<:alert:1199317330790993960> | Unable to Remove Timeout:\n```py\n{}```"
                    .format(e))
                    await ctx.send(embed=hacker)
            else:
                hacker1 = discord.Embed(
                color=0x2f3136,
                description="<:alert:1199317330790993960> | {} Is Not Muted".
                format(member.mention),
                timestamp=ctx.message.created_at)
                await ctx.send(embed=hacker1)
        except discord.NotFound:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> User not found.")
            await ctx.send(embed=error, delete_after=10)

        except discord.Forbidden:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> I do not have necessary permissions to `timeout` members.")
            await ctx.send(embed=error, delete_after=5)

        except:
            pass

    @commands.hybrid_command(
        name="kick",
        help=
        "Kick a user from the server.",
        usage="kick <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(kick_members=True)
    async def _kick(self,
                    ctx: commands.Context,
                    member: discord.Member,
                    *,
                    reason=None):

        if member == self.bot:
            await ctx.reply(f"dont just kick me like that :pray:", delete_after=5)
            return
        
        if not ctx.guild.me.guild_permissions.kick_members:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> Bot does not have the necessary permissions to kick this user.")
            error.set_author(name="Error!", icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=error, delete_after=10)
        
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kicks (
                user_id INTEGER,
                guild_id INTEGER,
                reason TEXT,
                timestamp INTEGER
            )
            ''')
            
            timestamp = int(datetime.datetime.utcnow().timestamp())
            kick_reason = reason or "No reason provided"
            
            self.cursor.execute(
                'INSERT INTO kicks (user_id, guild_id, reason, timestamp) VALUES (?, ?, ?, ?)',
                (member.id, ctx.guild.id, kick_reason, timestamp)
            )
            self.conn.commit()
            
            await member.kick(reason=reason)
            
            embed = discord.Embed(
                title="Kick result:",
                description=f"Reason: {reason or 'No reason provided'}\nModerator: {ctx.author.mention}\n\n<:whitecheck:1243577701638475787> Successfully kicked {member.mention} from the server.",
                color=0x2f3136
            )
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)

            try:
                dm_embed = discord.Embed(
                    title=f"<:alert:1199317330790993960> You have been kicked from {ctx.guild.name}",
                    description=f"Reason: {reason or 'No reason provided'}\nModerator: {ctx.author.mention}",
                    color=0x2f3136
                )
                dm_embed.timestamp = discord.utils.utcnow()
                await member.send(embed=dm_embed)
            except:
                # User might have DMs closed
                pass

        except discord.NotFound:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> User not found.")
            await ctx.send(embed=error, delete_after=10)

        except Exception as e:
            print(f"Error kicking: {e}")
            error_embed = discord.Embed(
                color=0x2f3136,
                description=f"<:alert:1199317330790993960> An error occurred: {e}"
            )
            await ctx.send(embed=error_embed)
            
            
    @commands.hybrid_command(name="warn",
                             help="Warn a server member.",
                             usage="warn <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(moderate_members=True)
    async def _warn(self,ctx: commands.Context,member: discord.Member,*,reason=None):
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER,
                guild_id INTEGER,
                reason TEXT,
                timestamp INTEGER
            )
            ''')
            
            timestamp = int(datetime.datetime.utcnow().timestamp())
            warn_reason = reason or "No reason provided"

            self.cursor.execute(
                'INSERT INTO warnings (user_id, guild_id, reason, timestamp) VALUES (?, ?, ?, ?)',
                (member.id, ctx.guild.id, warn_reason, timestamp)
            )
            self.conn.commit()
            
            hacker = discord.Embed(
            color=0x2f3136,
            description=f"<:whitecheck:1243577701638475787> | {member.display_name} has been warned for: {reason}")
            hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=hacker)

            hacker1 = discord.Embed(
            color=0x886ad1,
            description=f"<:alert:1199317330790993960> | You have been warned in {ctx.guild.name} for: {reason} By [{ctx.author}](https://discord.com/users/{ctx.author.id})")
            await member.send(embed=hacker1)
        except discord.Forbidden:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> I do not have necessary permissions to `warn` members.")
            error.set_author(name="Error!", icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=error)

        except:
            pass

    @commands.hybrid_command(
        name='ban',
        aliases=['fuckoff'],
        help="Permanently ban a user from the server.",
        usage="ban <member/id> [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(ban_members=True)
    async def _ban(self,
                   ctx: commands.Context,
                   user: discord.Member | discord.User,
                   *,
                   reason: str = None):
        
        if user == self.bot.user:
            return await ctx.reply(f"no :pray:", delete_after=5)
            
        if isinstance(user, discord.Member):
            if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                embed = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> You cannot ban {user.mention} as their role is higher than or equal to yours.")
                return await ctx.send(embed=embed)
                
            if user.top_role.position >= ctx.guild.me.top_role.position:
                embed = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> I cannot ban {user.mention} as their role is higher than mine.")
                return await ctx.send(embed=embed)

        delete_message_days = 0
        
        if not reason:
            reason = "No reason provided"
            
        ban_reason = f"{reason} | Banned by {ctx.author} (ID: {ctx.author.id})"
        
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bans (
                user_id INTEGER,
                guild_id INTEGER,
                reason TEXT,
                unban_time TEXT,
                status TEXT,
                PRIMARY KEY (user_id, guild_id)
            )
            ''')
            
            self.cursor.execute('SELECT * FROM bans WHERE user_id = ? AND guild_id = ?', (user.id, ctx.guild.id))
            existing_ban = self.cursor.fetchone()

            if existing_ban:
                self.cursor.execute('UPDATE bans SET reason = ?, unban_time = ?, status = ? WHERE user_id = ? AND guild_id = ?', 
                                   (reason, None, 'banned', user.id, ctx.guild.id))
            else:
                self.cursor.execute('INSERT INTO bans (user_id, guild_id, reason, unban_time, status) VALUES (?, ?, ?, ?, ?)', 
                                   (user.id, ctx.guild.id, reason, None, 'banned'))
            
            self.conn.commit()

            await ctx.guild.ban(user, reason=ban_reason, delete_message_days=delete_message_days)
            
            embed = discord.Embed(
                title="Ban result:",
                description=f"Reason: {reason}\nModerator: {ctx.author.mention}\nDuration: Permanent\n\n<:whitecheck:1243577701638475787> Successfully banned {user.mention} permanently.",
                color=0x2f3136
            )
            embed.timestamp = discord.utils.utcnow()

            try:
                dm_embed = discord.Embed(
                    title=f"<:alert:1199317330790993960> You have been banned from {ctx.guild.name}.",
                    description=f"Reason: {reason}\nModerator: {ctx.author.mention}\nDuration: Permanent",
                    color=0x2f3136
                )
                dm_embed.timestamp = discord.utils.utcnow()
                await user.send(embed=dm_embed)
            except:
                # User might have DMs closed
                pass
            
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error banning: {e}")
            error_embed = discord.Embed(
                color=0x2f3136,
                description=f"<:alert:1199317330790993960> An error occurred: {e}"
            )
            await ctx.send(embed=error_embed)

    @commands.hybrid_command(
        name='tempban',
        help="Temporarily ban a user from the server.",
        usage="tempban <member/id> <duration> [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(ban_members=True)
    async def _tempban(self,
                   ctx: commands.Context,
                   user: discord.Member | discord.User,
                   duration: str,
                   *,
                   reason: str = None):
        
        if user == self.bot.user:
            return await ctx.reply(f"no :pray:", delete_after=5)
            
        if isinstance(user, discord.Member):
            if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                embed = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> You cannot ban {user.mention} as their role is higher than or equal to yours.")
                return await ctx.send(embed=embed)
                
            if user.top_role.position >= ctx.guild.me.top_role.position:
                embed = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> I cannot ban {user.mention} as their role is higher than mine.")
                return await ctx.send(embed=embed)

        delete_message_days = 0
        unban_time = None
        
        if not re.match(r'^\d+[smhd]$', duration):
            embed = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> Invalid duration format. Use something like 1d, 12h, 30m, etc.")
            return await ctx.send(embed=embed)
        
        unban_seconds = self.convert(duration)
        if unban_seconds <= 0:
            embed = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> Invalid duration. Please provide a valid time.")
            return await ctx.send(embed=embed)
            
        unban_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=unban_seconds)
        time_text = f" for {duration}"
        
        if not reason:
            reason = "No reason provided"
            
        ban_reason = f"{reason} | Temp banned by {ctx.author} (ID: {ctx.author.id})"
        
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bans (
                user_id INTEGER,
                guild_id INTEGER,
                reason TEXT,
                unban_time TEXT,
                status TEXT,
                PRIMARY KEY (user_id, guild_id)
            )
            ''')
            
            self.cursor.execute('SELECT * FROM bans WHERE user_id = ? AND guild_id = ?', (user.id, ctx.guild.id))
            existing_ban = self.cursor.fetchone()

            if existing_ban:
                self.cursor.execute('UPDATE bans SET reason = ?, unban_time = ?, status = ? WHERE user_id = ? AND guild_id = ?', 
                                   (reason, unban_time, 'banned', user.id, ctx.guild.id))
            else:
                self.cursor.execute('INSERT INTO bans (user_id, guild_id, reason, unban_time, status) VALUES (?, ?, ?, ?, ?)', 
                                   (user.id, ctx.guild.id, reason, unban_time, 'banned'))
            
            self.conn.commit()

            await ctx.guild.ban(user, reason=ban_reason, delete_message_days=delete_message_days)
            
            embed = discord.Embed(
                title="Ban result:",
                description=f"Reason: {reason}\nModerator: {ctx.author.mention}\nDuration: {duration}\n\n<:whitecheck:1243577701638475787> Successfully banned {user.mention}{time_text}.",
                color=0x2f3136
            )
            embed.timestamp = discord.utils.utcnow()

            try:
                dm_embed = discord.Embed(
                    title=f"<:alert:1199317330790993960> You have been temporarily banned from {ctx.guild.name}.",
                    description=f"Reason: {reason}\nModerator: {ctx.author.mention}\nDuration: {duration}",
                    color=0x2f3136
                )
                dm_embed.timestamp = discord.utils.utcnow()
                await user.send(embed=dm_embed)
            except:
                # User might have DMs closed
                pass
            
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error temp banning: {e}")
            error_embed = discord.Embed(
                color=0x2f3136,
                description=f"<:alert:1199317330790993960> An error occurred: {e}"
            )
            await ctx.send(embed=error_embed)


    @commands.hybrid_command(
        name="unban",
        help="Unban a member from server.",
        usage="unban <@member/id> [reason]")
    @blacklist_check()
    @commands.has_permissions(ban_members=True)
    async def _unban(self, ctx: commands.Context, id: str, *, reason: str = "No reason provided"):
        try:
            user = await self.bot.fetch_user(int(id))
            await ctx.guild.unban(user, reason=reason)

            embed = discord.Embed(
                title="Unban result:",
                description=f"Reason: {reason}\nModerator: {ctx.author.mention}\nSuccessful unbans: {user.mention}",
                color=0x2f3136
            )
            embed.timestamp = discord.utils.utcnow()
            
            await ctx.send(embed=embed)

        except discord.NotFound:
            error = discord.Embed(color=0x2f3136, description=f"<:alert:1199317330790993960> User not found.")
            await ctx.send(embed=error, delete_after=10)

        except Exception as e:
            print(f"Error unbanning: {e}")
            error_embed = discord.Embed(
                color=0x2f3136,
                description=f"<:alert:1199317330790993960> An error occurred: {e}"
            )
            await ctx.send(embed=error_embed)


    @commands.hybrid_command(
        name="history",
        help="Shows the punishment history of a user.",
        usage="history <@user>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(moderate_members=True)
    async def _history(self, ctx: commands.Context, user: discord.User):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeouts (
            user_id INTEGER,
            guild_id INTEGER,
            reason TEXT,
            duration TEXT,
            timestamp INTEGER
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            user_id INTEGER,
            guild_id INTEGER,
            reason TEXT,
            timestamp INTEGER
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kicks (
            user_id INTEGER,
            guild_id INTEGER,
            reason TEXT,
            timestamp INTEGER
        )
        ''')
        
        self.cursor.execute('SELECT reason, unban_time, status FROM bans WHERE user_id = ? AND guild_id = ?', 
                           (user.id, ctx.guild.id))
        ban_rows = self.cursor.fetchall()
        
        self.cursor.execute('SELECT reason, duration, timestamp FROM timeouts WHERE user_id = ? AND guild_id = ? ORDER BY timestamp DESC', 
                           (user.id, ctx.guild.id))
        timeout_rows = self.cursor.fetchall()
        
        self.cursor.execute('SELECT reason, timestamp FROM warnings WHERE user_id = ? AND guild_id = ? ORDER BY timestamp DESC', 
                           (user.id, ctx.guild.id))
        warn_rows = self.cursor.fetchall()
        
        self.cursor.execute('SELECT reason, timestamp FROM kicks WHERE user_id = ? AND guild_id = ? ORDER BY timestamp DESC', 
                           (user.id, ctx.guild.id))
        kick_rows = self.cursor.fetchall()

        if not ban_rows and not timeout_rows and not warn_rows and not kick_rows:
            embed = discord.Embed(
                color=0x2f3136,
                description=f"<:alert:1199317330790993960> No punishment history found for {user.mention}.")
            await ctx.send(embed=embed)
            return

        embeds = []
        
        
        if ban_rows:
            ban_description = ""
            for i, (reason, unban_time, status) in enumerate(ban_rows[:5], 1):
                if isinstance(unban_time, str) and unban_time:
                    try:
                        unban_time = datetime.datetime.fromisoformat(unban_time)
                        unban_time_str = f"<t:{int(unban_time.timestamp())}:F>"
                    except:
                        unban_time_str = "Unknown"
                else:
                    unban_time_str = "Permanent"
                
                ban_description += f"**#{i} | Ban**\n**Reason:** {reason}\n**Duration:** {unban_time_str}\n**Status:** {status}\n\n"
            
            if ban_description:
                ban_embed = discord.Embed(
                    title=f"Ban History for {user.name}",
                    description=ban_description,
                    color=0x2f3136
                )
                ban_embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                embeds.append(ban_embed)
        
        if timeout_rows:
            timeout_description = ""
            for i, (reason, duration, timestamp) in enumerate(timeout_rows[:5], 1):
                timeout_time = f"<t:{int(timestamp)}:F>" if timestamp else "Unknown"
                timeout_description += f"**#{i} | Timeout**\n**Reason:** {reason}\n**When:** {timeout_time}\n**Duration:** {duration}\n\n"
            
            if timeout_description:
                timeout_embed = discord.Embed(
                    title=f"Timeout History for {user.name}",
                    description=timeout_description,
                    color=0x2f3136
                )
                timeout_embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                embeds.append(timeout_embed)
        
        if warn_rows:
            warn_description = ""
            for i, (reason, timestamp) in enumerate(warn_rows[:5], 1):
                warn_time = f"<t:{int(timestamp)}:F>" if timestamp else "Unknown"
                warn_description += f"**#{i} | Warning**\n**Reason:** {reason}\n**When:** {warn_time}\n\n"
            
            if warn_description:
                warn_embed = discord.Embed(
                    title=f"Warning History for {user.name}",
                    description=warn_description,
                    color=0x2f3136
                )
                warn_embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                embeds.append(warn_embed)
        
        if kick_rows:
            kick_description = ""
            for i, (reason, timestamp) in enumerate(kick_rows[:5], 1):
                kick_time = f"<t:{int(timestamp)}:F>" if timestamp else "Unknown"
                kick_description += f"**#{i} | Kick**\n**Reason:** {reason}\n**When:** {kick_time}\n\n"
            
            if kick_description:
                kick_embed = discord.Embed(
                    title=f"Kick History for {user.name}",
                    description=kick_description,
                    color=0x2f3136
                )
                kick_embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                embeds.append(kick_embed)
        
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            view = PaginatorView(embeds)
            message = await ctx.send(embed=embeds[0], view=view)
            view.message = message


    @commands.hybrid_command(name="clone", help="Clones a channel.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx: commands.Context, channel: discord.TextChannel):
        await channel.clone()
        embed = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | {channel.name} has been cloned successfully.")
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="nick",
                             aliases=['setnick', 'nickname'],
                             help="To change someone's nickname.",
                             usage="nick [member]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_nicknames=True)
    async def changenickname(self, ctx: commands.Context,
                             member: discord.Member, *, nick):
        await member.edit(nick=nick)
        hacker = discord.Embed(
            color=0x2f3136,
            description=
            f"<:whitecheck:1243577701638475787> | Successfully changed nickname of {member.name}")
        hacker.set_author(name=f"{ctx.author.name}",
                          icon_url=f"{ctx.author.avatar}")
        
        await ctx.send(embed=hacker)

    @commands.group(aliases=["c"],
                    invoke_without_command=True,
                    help="Clears the messages")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    async def clear(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    async def do_removal(self,
                         ctx,
                         limit,
                         predicate,
                         *,
                         before=None,
                         after=None,
                         message=True):
        if limit > 1000:
            em = discord.Embed(
                description=
                f" Too many messages to search given ({limit}/2000)",
                color=0x2f3136)
            return await ctx.send(embed=em)

        if not before:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit,
                                              before=before,
                                              after=after,
                                              check=predicate)
        except discord.HTTPException as e:
            em = discord.Embed(description=f" Try a smaller search?",
                               color=0x2f3136)
            return await ctx.send(embed=em)

        deleted = len(deleted)
        if message is True:
            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(
                description=
                f" Successfully removed {deleted} message{'' if deleted == 1 else 's'}.",
                color=0x2f3136,
                delete_after=3))

    @clear.command(aliases=["e"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def embeds(self, ctx, search=1000):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @clear.command(aliases=["f"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def files(self, ctx, search=1000):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @clear.command(aliases=["m"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def mentions(self, ctx, search=1000):
        """Removes messages that have mentions in them."""
        await self.do_removal(
            ctx, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @clear.command(aliases=["i"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def images(self, ctx, search=1000):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search,
                              lambda e: len(e.embeds) or len(e.attachments))

    @clear.command(aliases=["co"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send(
                "The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 1000, lambda e: substr in e.content)

    @clear.command(name="bots", aliases=["b"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def _bots(self, ctx, search=100, prefix=None):
        """Removes a bot user's messages and messages with their optional prefix."""

        getprefix = [
            ";", "$", "!", "-", "?", ">", "^", "$", "w!", ".", ",", "a?", "g!",
            "m!", "s?"
        ]

        def predicate(m):
            return (m.webhook_id is None
                    and m.author.bot) or m.content.startswith(tuple(getprefix))

        await self.do_removal(ctx, search, predicate)

    @clear.command(name="emojis", aliases=["em"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def _emojis(self, ctx, search=1000):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(
            r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @clear.command(name="reactions", aliases=["r"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def _reactions(self, ctx, search=1000):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(
                f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()
        await ctx.message.delete()
        await ctx.send(embed=discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Successfully Removed {total_reactions}.",
            color=0x2f3136))

    @commands.hybrid_command(name="nuke", help="Deletes the channel and clones it, so pings are removed.", usage="nuke")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def _nuke(self, ctx: commands.Context):
        if ctx.guild.me.guild_permissions.manage_channels:
            try:
                channel = ctx.channel
                newchannel = await channel.clone()

                await newchannel.edit(position=channel.position)
                await channel.delete()

                await newchannel.send(f"`channel was nuked by {ctx.author}`")
            except Exception as e:
                print(e)
                await ctx.send(f"An error occured while cloning the channel. An automatic alert was sent to the developers.")

    @commands.hybrid_command(name="lock",
                             help="Locks down a channel",
                             usage="lock <channel> <reason>",
                             aliases=["lockdown"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def _lock(self,
                    ctx: commands.Context,
                    channel: discord.TextChannel = None,
                    *,
                    reason=None):
        if channel is None: channel = ctx.channel
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(send_messages=False),
                reason=reason)
            await ctx.send(embed=discord.Embed(
                
                description=
                "<:whitecheck:1243577701638475787> | Successfully locked **%s**"
                % (channel.mention),
                color=0x2f3136))
        except:
            await ctx.send(
                embed=discord.Embed(
                                    description="Failed to lockdown **%s**" %
                                    (channel.mention),
                                    color=0x2f3136))
        else:
            pass

    @commands.hybrid_command(name="unlock",
                             help="Unlocks a channel",
                             usage="unlock <channel> <reason>",
                             aliases=["unlockdown"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def _unlock(self,
                      ctx: commands.Context,
                      channel: discord.TextChannel = None,
                      *,
                      reason=None):
        if channel is None: channel = ctx.channel
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(send_messages=True),
                reason=reason)
            await ctx.send(embed=discord.Embed(
                
                description=
                "<:whitecheck:1243577701638475787> | Successfully unlocked **%s**"
                % (channel.mention),
                color=0x2f3136))
        except:
            await ctx.send(
                embed=discord.Embed(
                                    description="Failed to lock **`%s`**" %
                                    (channel.mention),
                                    color=0x2f3136))
        else:
            pass

    @commands.hybrid_command(name="slowmode",
                             help="Changes the slowmode",
                             usage="slowmode [seconds]",
                             aliases=["slow"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def _slowmode(self, ctx: commands.Context, seconds: int = 0):
        if seconds > 120:
            return await ctx.send(embed=discord.Embed(
                title="slowmode",
                description="Slowmode can not be over 2 minutes",
                color=0x2f3136))
        if seconds == 0:
            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.send(
                embed=discord.Embed(title="slowmode",
                                    description="Slowmode is disabled",
                                    color=0x2f3136))
        else:
            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.send(
                embed=discord.Embed(title="slowmode",
                                    description="Set slowmode to **`%s`**" %
                                    (seconds),
                                    color=0x2f3136))

    @commands.hybrid_command(name="unslowmode",
                             help="Disables slowmode",
                             usage="unslowmode",
                             aliases=["unslow"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def _unslowmode(self, ctx: commands.Context):
        await ctx.channel.edit(slowmode_delay=0)
        await ctx.send(embed=discord.Embed(title="unslowmode",
                                           description="Disabled slowmode",
                                           color=0x2f3136))


#

    @commands.hybrid_command(help="Search for emojis!",
                             aliases=['searchemoji', 'findemoji', 'emojifind'])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def emojisearch(self, ctx: commands.Context, name: Lower = None):
        if not name:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=discord.Embed(
                description=
                "Please enter a emoji!\n\nExample: `emojisearch nitro`",
                color=0x2f3136))
        emojis = [
            str(emoji) for emoji in self.bot.emojis
            if name in emoji.name.lower() and emoji.is_usable()
        ]
        if len(emojis) == 0:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=discord.Embed(
                description=
                f"Couldn't find any results for `{name}`, please try again .",
                color=0x2f3136))
        paginators = commands.Paginator(prefix="", suffix="", max_size=500)
        for emoji in emojis:
            paginators.add_line(emoji)
        await ctx.reply(embed=discord.Embed(
            description=f"Found `{len(emojis)}` emojis .", color=0x2f3136))
        if len(Paginator.pages) == 1:
            return await ctx.send(paginators.pages[0])
        view = TextPaginator(ctx, paginators.pages)
        await ctx.send(paginators.pages[0], view=view)

    @commands.hybrid_command(
        help="Search for stickers!",
        aliases=['searchsticker', 'findsticker', 'stickerfind'])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def stickersearch(self, ctx: commands.Context, name: Lower = None):
        if not name:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=discord.Embed(
                description="Please enter a sticker`"))
        stickers = [
            sticker for sticker in self.bot.stickers
            if name in sticker.name.lower()
        ]
        if len(stickers) == 0:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=discord.Embed(
                description=
                f"Couldn't find any results for `{name}` | Try Again .",
                color=0x2f3136))
        embeds = []
        for sticker in stickers:
            embeds.append(
                discord.Embed(title=sticker.name,
                              description=sticker.description,
                              color=0x2f3136,
                              url=sticker.url).set_image(url=sticker.url))
        await ctx.reply(embed=discord.Embed(
            description=f"Found `{len(embeds)}` stickers .", color=0x2f3136))
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        view = Paginator(ctx, embeds)
        return await ctx.send(embed=embeds[0], view=view)

    @commands.hybrid_group(help="Get info about stickers in a message!",
                           aliases=['stickers', 'stickerinfo'])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def sticker(self, ctx: commands.Context):
        ref = ctx.message.reference
        if not ref:
            stickers = ctx.message.stickers
        else:
            msg = await ctx.fetch_message(ref.message_id)
            stickers = msg.stickers
        if len(stickers) == 0:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(
                embed=discord.Embed(" No Stickers!",
                                    "There are no stickers in this message.",
                                    color=0x2f3136))
        embeds = []
        for sticker in stickers:
            sticker = await sticker.fetch()
            embed = discord.Embed(
                title=" Sticker Info",
                description=f"""
**Name:** {sticker.name}
**ID:** {sticker.id}
**Description:** {sticker.description}
**URL:** [Link]({sticker.url})
{"**Related Emoji:** "+":"+sticker.emoji+":" if isinstance(sticker, discord.GuildSticker) else "**Tags:** "+', '.join(sticker.tags)}
                """,
                color=0x2f3136).set_thumbnail(url=sticker.url)
            if isinstance(sticker, discord.GuildSticker):
                embed.add_field(name="Guild ID:",
                                value=f"{sticker.guild_id}",
                                inline=False)
            else:
                pack = await sticker.pack()
                embed.add_field(name="Pack Info:",
                                value=f"""
**Name:** {pack.name}
**ID:** {pack.id}
**Stickers:** {len(pack.stickers)}
**Description:** {pack.description}
                    """,
                                inline=False)
                embed.set_image(url=pack.banner.url)
            embeds.append(embed)

        if len(embeds) == 1:
            await ctx.reply(embed=embeds[0])
        else:
            view = Paginator(ctx, embeds)
            await ctx.reply(embed=embeds[0], view=view)
    @commands.hybrid_group(name="role", description="Toggle a role for a user or use subcommands", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @blacklist_check()
    async def role(self, ctx: commands.Context, user: discord.Member = None, *, role_input: str = None):
        if ctx.subcommand_passed is None:
            if user is None or role_input is None:
                await ctx.send_help(ctx.command)
                ctx.command.reset_cooldown(ctx)
                return
        
            role = None
            if role_input.isdigit():
                role = ctx.guild.get_role(int(role_input))
            else:
                role_mention_match = re.match(r'<@&(\d+)>', role_input)
                if role_mention_match:
                    role_id = int(role_mention_match.group(1))
                    role = ctx.guild.get_role(role_id)
                else:
                    role = discord.utils.find(lambda r: r.name.lower() == role_input.lower(), ctx.guild.roles)
                    
                    if role is None:
                        matching_roles = [r for r in ctx.guild.roles if role_input.lower() in r.name.lower()]
                        if matching_roles:
                            role = matching_roles[0]
            
            if role is None:
                embed = discord.Embed(
                    description=f"<:alert:1199317330790993960> | Could not find a role matching '{role_input}'",
                    color=0x2f3136
                )
                return await ctx.send(embed=embed)
            
            if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                embed = discord.Embed(
                    description=f"<:alert:1199317330790993960> | {role.mention} is higher than or equal to your top role!",
                    color=0x2f3136
                )
                return await ctx.send(embed=embed)
            
            if role.position >= ctx.guild.me.top_role.position:
                embed = discord.Embed(
                    description=f"<:alert:1199317330790993960> | {role.mention} is higher than my top role, move my role above {role.mention}.",
                    color=0x2f3136
                )
                return await ctx.send(embed=embed)
            
            if role in user.roles:
                await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
                embed = discord.Embed(
                    description=f"<:whitecheck:1243577701638475787> | Removed {role.mention} from {user.mention}",
                    color=0x2f3136
                )
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                await ctx.send(embed=embed)
            else:
                await user.add_roles(role, reason=f"Role added by {ctx.author}")
                embed = discord.Embed(
                    description=f"<:whitecheck:1243577701638475787> | Added {role.mention} to {user.mention}",
                    color=0x2f3136
                )
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                await ctx.send(embed=embed)
        else:
            pass


    @role.command(name="temporary", description="give a temporary role to a user.")
    @commands.bot_has_permissions(manage_roles=True)
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def temp(self, ctx, role: discord.Role, time, *,
                   user: discord.Member):
        if role == ctx.author.top_role:
            embed = discord.Embed(
                description=
                f"<:anxCross:1107932430322647144> | {role} has the same position as your top role!",
                color=0x2f3136)
            return await ctx.send(embed=embed)
        else:
            if role.position >= ctx.guild.me.top_role.position:
                embed1 = discord.Embed(
                    description=
                    f"<:anxCross:1107932430322647144> | {role} is higher than my role, move my role above {role}.",
                    color=0x2f3136)
                return await ctx.send(embed=embed1)
        seconds = convert(time)
        await user.add_roles(role, reason=None)
        hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Successfully added {role.mention} to {user.mention} .",
            color=0x2f3136)
        await ctx.send(embed=hacker)
        await asyncio.sleep(seconds)
        await user.remove_roles(role)

    @role.command(name="remove", description="remove a role from a user.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def remove(self, ctx, user: discord.Member, role: discord.Role):
        if role == ctx.author.top_role:
            embed = discord.Embed(
                description=
                f"<:anxCross:1107932430322647144> | {role} has the same position as your top role!",
                color=0x2f3136)
            return await ctx.send(embed=embed)
        else:
            if role.position >= ctx.guild.me.top_role.position:
                embed1 = discord.Embed(
                    description=
                    f"<:anxCross:1107932430322647144> | {role} is higher than my role, move my role above {role}.",
                    color=0x2f3136)
                return await ctx.send(embed=embed1)
        await user.remove_roles(role)
        hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Successfully removed {role.mention} from {user.mention} .",
            color=0x2f3136)
        await ctx.send(embed=hacker)

    @role.command(name="delete", description="delete a role from server")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def delete(self, ctx, role: discord.Role):
        if role == ctx.author.top_role:
            embed = discord.Embed(
                description=
                f"<:anxCross:1107932430322647144> | {role} has the same position as your top role!",
                color=0x2f3136)
            return await ctx.send(embed=embed)
        else:
            if role.position >= ctx.guild.me.top_role.position:
                embed1 = discord.Embed(
                    description=
                    f"<:anxCross:1107932430322647144> | {role} is higher than my role, move my role above {role}.",
                    color=0x2f3136)
                return await ctx.send(embed=embed1)
        if role is None:
            embed2 = discord.Embed(
                description=
                f"<:anxCross:1107932430322647144> | No role named {role} found in this server .",
                color=0x2f3136)
            return await ctx.send(embed=embed2)
        await role.delete()
        hacker = discord.Embed(
            description=
            f"<:whitecheck:1243577701638475787> | Successfully deleted {role}",
            color=0x2f3136)
        await ctx.send(embed=hacker)

    @role.command(name="create", description="create a role in the server.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def create(self, ctx, *, name):
        if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
            hacker = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Successfully created role with the name {name}",
                color=0x2f3136)
            await ctx.guild.create_role(name=name,
                                        color=discord.Color.default())
            await ctx.send(embed=hacker)
        else:
            hacker5 = discord.Embed(
                description=
                """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")

            await ctx.send(embed=hacker5)

    @role.command(name="rename", description="rename a role")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def rename(self, ctx, role: discord.Role, *, newname):
        if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
            await role.edit(name=newname)
            await ctx.send(
                f"<:whitecheck:1243577701638475787> | Role {role.name} has been renamed to {newname}"
            )
        elif role is None:
            embed2 = discord.Embed(
                description=
                f"<:anxCross:1107932430322647144> | No role named {role} found in this server .",
                color=0x2f3136)
            return await ctx.send(embed=embed2)
        else:
            hacker5 = discord.Embed(
                description=
                """```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")

            await ctx.send(embed=hacker5)



    @role.command(name="humans", description="give a role to all humans.")
    @commands.has_permissions(administrator=True)
    async def humans(self, ctx, role: discord.Role):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            hacker1 = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | Added {role.mention} to all humans.",
                color=0x2f3136)
            hacker1.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.avatar}")

            for hacker in ctx.guild.members:
                if not hacker.bot:
                    try:
                        await hacker.add_roles(role, reason=f"Role humans command used by {ctx.author}")
                    except discord.Forbidden:
                        pass
                    except discord.HTTPException as e:
                        print(f"An error occurred in role humans: {e}")
                    except Exception as e:
                        await ctx.send(e)

            await ctx.send(embed=hacker1)
        else:
            hacker5 = discord.Embed(
                description="""```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")

            await ctx.send(embed=hacker5, mention_author=False)




    @role.command(name="bots", description="give a role to all bots.")
    @commands.has_permissions(administrator=True)
    async def bots(self,ctx,role:discord.Role):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            hacker1 = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | Added {role.mention} to all bots .",
                color=0x2f3136)
            hacker1.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.avatar}")
            for hacker in ctx.guild.members:
                if hacker.bot:
                    try:
                        await hacker.add_roles(role, reason=f"Role bots command used by {ctx.author}")
                    except discord.Forbidden:
                        pass
                    except discord.HTTPException as e:
                        print(f"An error occurred: {e}")
                    except Exception as e:
                        await ctx.send(e)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")

            await ctx.send(embed=hacker5, mention_author=False)










    @commands.group(name="admin",
                     help="",
                     invoke_without_command=True,
                     usage="admin add")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _admin(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_admin.command(name="add",
                        help="Add a user to admin list",
                        usage="admin add <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def admin_add(self, ctx, user: discord.User):
        data = getConfig(ctx.guild.id)
        wled = data["admins"]

        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            if len(wled) == 15:
                hacker = discord.Embed(
                 
                    description=
                    "<:right:1199668086916263956> You are trying to add more users than what it's allowed in [Trusted Admins]!",           color=0x2f3136)
                hacker.set_author(
                    name="Unsuccessful Operation!",
                    icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.reply(embed=hacker, mention_author=False)
            else:
                if str(user.id) in wled:
                    hacker1 = discord.Embed(
                        color=0x2f3136)
                    hacker1.add_field(
                    name="<:whitecheck:1243577701638475787> Successful Operations",
                    value="No successful operation!",
                    inline=False)
                    hacker1.add_field(
                    name="<:right:1199668086916263956> Unsuccessful Operations",
                    value=f"""<:right:1199668086916263956> `{user}` <:anxCross:1107932430322647144>
                                                               <:right:1199668086916263956> *Already exists!*""",
                   inline=False)
                    hacker1.set_author(
                    name="Trusted Admins Addition Result:",
                    icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.reply(embed=hacker1, mention_author=False)
                else:
                    wled.append(str(user.id))
                    updateConfig(ctx.guild.id, data)
                    hacker4 = discord.Embed(
                        color=0x2f3136
                    )
                    hacker4.add_field(
                    name="<:whitecheck:1243577701638475787> Successful Operations",
                    value=f"<:right:1199668086916263956> `{user}`",
                    inline=False)
                    hacker4.add_field(
                    name="<:warn:1199645241729368084> Unsuccessful Operations",
                    value="All operations were successful!",
                    inline=False)
                    hacker4.set_author(
                    name="Trusted Admins Addition Result:",
                    icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.reply(embed=hacker4, mention_author=False)

        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5, mention_author=False)

    @_admin.command(name="remove",
                        help="Remove a user from admin list",
                        usage="admin remove <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def admin_remove(self, ctx, user: discord.User):
        data = getConfig(ctx.guild.id)
        wled = data["admins"]
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            if str(user.id) in wled:
                wled.remove(str(user.id))
                updateConfig(ctx.guild.id, data)
                hacker = discord.Embed(
                    color=0x2f3136,
                 
                    description=f"<:whitecheck:1243577701638475787> | Successfully Removed {user.mention} From Admin list For {ctx.guild.name}"
                )
                await ctx.reply(embed=hacker, mention_author=False)
            else:
                hacker2 = discord.Embed(
                    color=0x2f3136,
                 
                    description=
                    "<:anxCross:1107932430322647144> | That user is not in my admin list ."
                )
                await ctx.reply(embed=hacker2, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5, mention_author=False)

    @_admin.command(name="show",
                        help="Shows list of admin users in the server.",
                        usage="admin show")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def admin_show(self, ctx):
        data = getConfig(ctx.guild.id)
        wled = data["admins"]
        if len(wled) == 0:
            hacker = discord.Embed(
                color=0x2f3136,
             
                description=
                f"<:anxCross:1107932430322647144> | There aren\'t any admin users for this server"
            )
            await ctx.reply(embed=hacker, mention_author=False)
        else:
            entries = [
                f"`{no}` | <@!{idk}> | ID: [{idk}](https://discord.com/users/{idk})"
                for no, idk in enumerate(wled, start=1)
            ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=f"Admin Users of {ctx.guild.name} - 15/{len(wled)}",
                description="",
                color=0x2F3136),
                                  ctx=ctx)
            await paginator.paginate()

    @_admin.command(name="reset",
                        help="removes every user from admin database",
                        aliases=["clear"],
                        usage="admin reset")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def wl_reset(self, ctx: Context):
        data = getConfig(ctx.guild.id)

        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            data = getConfig(ctx.guild.id)
            data["admins"] = []
            updateConfig(ctx.guild.id, data)
            hacker = discord.Embed(
                color=0x2f3136,
             
                description=
                f"<:whitecheck:1243577701638475787> | Successfully Cleared Admin Database For **{ctx.guild.name}**"
            )
            await ctx.reply(embed=hacker, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5, mention_author=False)

    @_admin.command(name="role",
                        help="Add a role to admin role",
                        usage="Antinuke admin role")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_role(self, ctx, role: discord.Role):
        data = getConfig(ctx.guild.id)
        data["adminrole"] = role.id
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            updateConfig(ctx.guild.id, data)
            hacker4 = discord.Embed(
                color=0x2f3136,
             
                description=
                f"<:whitecheck:1243577701638475787> | {role.mention} Has Been Added To Admin Role For {ctx.guild.name}"
            )
            await ctx.reply(embed=hacker4, mention_author=False)

        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5, mention_author=False)





