from multiprocessing import managers
import time
import discord, asyncio, re, aiohttp
from discord.ext import commands, tasks
from discord.ext.commands import BucketType
from core import Cog, Astroz, Context
from discord.enums import ButtonStyle
import utils.antiraider as utils
import sqlite3
from datetime import timedelta
from datetime import date 
errorcol = 0x2f3136
urgecolor = 0x2f3136
success = discord.Colour.blurple()
checkmoji = "<:whitecheck:1243577701638475787>"
xmoji = "<:whitecross:1243852723753844736>"
urgentmoji = "<:warn:1199645241729368084>"



async def send_command_help(ctx):
    await ctx.send_help(ctx.invoked_subcommand or ctx.command)

async def Confirms(self:discord.ext.commands.Cog, ctx:discord.ext.commands.Context, msg:discord.Message, invoker:discord.User=None, invoked:discord.User=None, timeout:int=180):

    if invoker == None:
        invoker=ctx.author
    if invoked == None:
        invoked=ctx.author
    view = Confirm(invoker=invoker, invoked=invoked, timeout=timeout)
    await msg.edit(view=view)
    await view.wait()
    return view.value

class Confirm(discord.ui.View):
    def __init__(self, invoker:"discord.User|discord.Member", invoked:"discord.User|discord.Member", *, timeout:float=None):
        if timeout is not None:
            super().__init__(timeout=timeout)
        else:
            super().__init__()
        self.value = None
        self.invoker = invoker
        self.invoked = invoked

    @discord.ui.button(label="Yes", style=ButtonStyle.green)
    async def confirm(self, interaction:discord.Interaction, button:discord.ui.Button):
        await self.confirmation(interaction, True)

    @discord.ui.button(label="No", style=ButtonStyle.red)
    async def cancel(self, interaction:discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, False)

    async def confirmation(self, interaction:discord.Interaction, confirm:bool):
        if confirm:
            if not interaction.user.id == self.invoker.id:
                await interaction.response.send_message(embed=discord.Embed(description=f"<:warn:1199645241729368084> {interaction.user.mention}: You cannot interact with this", color=int("faa61a", 16)), ephemeral=True)
                return
        else:
            if not interaction.user.id == self.invoker.id:
                if interaction.user.id == self.invoked.id:
                    pass
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"<:warn:1199645241729368084> {interaction.user.mention}: You cannot interact with this", color=int("faa61a", 16)), ephemeral=True)
                    return
        if confirm:
            await interaction.response.defer()
        else:
           await interaction.response.defer()
        self.value = confirm
        self.stop()



def strip_codeblock(content):
    if content.startswith('```') and content.endswith('```'):
        return content.strip('```')
    return content.strip('` \n')

class Flags(commands.FlagConverter, prefix='--', delimiter=' ', case_insensitive=True):
    @classmethod
    async def convert(cls, ctx, argument: str):
        argument = strip_codeblock(argument).replace(' —', ' --')
        return await super().convert(ctx, argument)
    do: str = "kick" or "ban"
    accountage: int 
    threshold: int = None
    massjoin: str = None


class Antiraid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('antiraid.db')
        self.cursor = self.conn.cursor()
        asyncio.create_task(self.setup_tables())
        self.cacheAntiraid.start()

    @tasks.loop(minutes=70)
    async def cacheAntiraid(self):
        self.cursor.execute('SELECT * FROM antiraid')
        antiraids = self.cursor.fetchall()
        self.cache = {}
        for row in antiraids:
            guild_id, age, _, _, _, ignored, penalty, defaultpfp, logs = row
            self.cache[guild_id] = {'age': age, 'ignored': ignored, 'penalty': penalty, 'defaultpfp': defaultpfp, 'logs': logs}

    @cacheAntiraid.before_loop
    async def before_cacheAntiraid(self):
        await self.bot.wait_until_ready()

    async def setup_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS antiraid (
                guild_id INTEGER PRIMARY KEY,
                age INTEGER,
                time TEXT,
                author TEXT,
                antiraid TEXT,
                ignored TEXT,
                penalty TEXT,
                defaultpfp TEXT,
                logs TEXT
            )
        ''')
        self.conn.commit()

    async def teardown_tables(self):
        self.conn.close()

    async def setup(self):
        await self.setup_tables()

    async def teardown(self):
        await self.teardown_tables()

    async def cog_unload(self):
        await self.teardown()
        self.conn.close()

    @commands.hybrid_group(
        usages='manage_guild',
        description='Protect your server from getting raided, mass joins, no profile picture.',
        help='Setup antiraid module in your server'
    )
    async def antiraid(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Antiraid", description="<...> Required | [...] Optional", color=0x2f3136)

                embed.add_field(name='antiraid enable', value='Enables antiraid in the server.', inline=False)
                embed.add_field(name='antiraid disable', value='Disables antiraid in the server.', inline=False)
                embed.add_field(name='antiraid age', value="Sets an account age for new joins. If an account's creation date is younger than the given threshold, they will be punished as per your configuration.", inline=False)
                embed.add_field(name='antiraid nopfp', value='Toggle on or off actions that will be taken on members with no profile picture.', inline=False)
                embed.add_field(name='antiraid config', value='Displays current antiraid settings.', inline=False)
                embed.add_field(name='antiraid massban', value='Bans the user that have joined the server in the given time.', inline=False)
                embed.add_field(name='antiraid logging', value='Set a channel for antiraid logging.', inline=False)
                embed.add_field(name='antiraid removelogs', value='Removes a channel from antiraid logging.', inline=False)
                embed.add_field(name='antiraid punishment', value='Set a punishment for the raiders.', inline=False)

                embed.set_footer(text=f"Incite")
                embed.timestamp = discord.utils.utcnow()
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e) 

    @antiraid.command(
        aliases=['nopfp'],
        usage="on/off",
        description="Toggles on or off actions that will be take on members with no profile picture."
    )
    @commands.has_permissions(manage_guild=True)
    async def defaultpfp(self, ctx, action): 
        check = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
        if check and action == "on":
            self.cursor.execute('UPDATE antiraid SET defaultpfp=? WHERE guild_id=?', ('on', ctx.guild.id))
            self.conn.commit()
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid will now take action on any users who join the server with a defaultpfp.", color=0x2f3136))
        if check and action == "off":
            self.cursor.execute('UPDATE antiraid SET defaultpfp=? WHERE guild_id=?', ('off', ctx.guild.id))
            self.conn.commit()
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid will no longer take action on those with a defaultpfp.", color=0x2f3136))
        if check and not action == "on" or check and not action == "off":
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} ``Action`` must be ``on`` or ``off``", color=errorcol))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} You must set an ``antiraid account_age`` in order to proceed.", color=errorcol))
    
    @antiraid.command(
        aliases=['punishment'],
        usage="kick/ban",
        description="Set a punishment for the raiders, antiraid will take action."
    )
    @commands.has_permissions(manage_guild=True)
    async def penalty(self, ctx, penalty):
        check = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
        if check and penalty == "ban":
            self.cursor.execute('UPDATE antiraid SET penalty=? WHERE guild_id=?', ('ban', ctx.guild.id))
            self.conn.commit()
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid will now ban any users who don't fit the ``account_age`` requirements.", color=0x2f3136))
        if check and penalty == "kick":
            self.cursor.execute('UPDATE antiraid SET penalty=? WHERE guild_id=?', ('kick', ctx.guild.id))
            self.conn.commit()
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid will now kick any users who don't fit the ``account_age`` requirements.", color=0x2f3136))
        if check and not penalty == "kick" or check and not penalty == "ban":
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} punishment must be ``kick`` or ``ban``", color=errorcol))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} You must set an antiraid ``account age`` in order to proceed.", color=errorcol))

    @antiraid.command(
        aliases=['logger', 'logging', 'log', 'setlogs', 'logset'],
        usage='#channel',
        description="Set a channel for antiraid logging.",
)
    @commands.has_permissions(manage_guild=True)
    async def logs(self, ctx, channel: discord.TextChannel):
        checks = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
        if checks and checks[8]:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} An antiraid log channel already exists! ", color=errorcol))
        else:
            self.cursor.execute('UPDATE antiraid SET logs=? WHERE guild_id=?', (channel.id, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> Antinuke Logging will now be sent in {channel.mention}", color=0x2f3136))

    @antiraid.command(
        aliases=['rlog', 'clearlogs', 'removelog', 'clearlog'],
        usage='removelogs',
        description="Removes a channel from antiraid logging.",
    )
    @commands.has_permissions(manage_guild=True)
    async def removelogs(self, ctx):
        checks = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
        check = checks[8]
        if not check:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} No antiraid log channel found.", color=errorcol))
        else:
            self.cursor.execute('UPDATE antiraid SET logs=NULL WHERE guild_id=?', (ctx.guild.id,))
            self.conn.commit()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> Antinuke Logging will no longer be sent", color=0x2f3136))

    @antiraid.command(
        usage="massban 15",
        description="Bans the user that have joined the server in the given time.",
)
    @commands.has_permissions(administrator=True)
    async def massban(self, ctx, minutes):
        ids = []
        if int(minutes) > 35:
            return await ctx.send("You can only massban up to `35` minutes worth of accounts")
        else:
            d = discord.utils.utcnow() - timedelta(minutes=int(minutes))
            for mem in ctx.guild.members:
                sti = mem.joined_at
                if sti > d:
                    ids.append(mem.id)

            if not ids:
                return await ctx.send(f"No accounts have joined in the past `{minutes}` minutes")
            else:
                yes = discord.Embed(description=f"{urgentmoji} Are you sure you want to ban `{len(ids)}` member(s) who joined in the past ``{minutes}`` minutes?", color=urgecolor)
                msg = await ctx.send(embed=yes)
                yes2 = discord.Embed(description=f"<:check:921544057312915498> Processing..", color=0x2f3136)
                async def confirm():
                    await msg.edit(view=None, embed=yes2)
                    count = 1
                    rows = []
                    content = discord.Embed(description = "", color=0x2f3136)
                    for count, i in enumerate(ids, start=1):
                        #await ban_method(author=ctx.message.author, guildID=ctx.guild.id, userID=i)
                        await i.ban()
                        rows.append(f"``{count})`` {i}")
                    content.set_author(name=f"Banned {len(ids)} members who attempted to raid.", icon_url=ctx.guild.icon.url)
                    await utils.send_as_pages(ctx, content, rows)

                async def cancel():
                    no = discord.Embed(description=f"{xmoji} Antiraid `massban minutes` process cancelled", color=errorcol)
                    await msg.edit(view=None, embed=no)
                    pass

                confirmed:bool = await Confirms(self, ctx, msg)
                if confirmed:
                    await confirm()
                else:
                    await cancel()

    @antiraid.command(
        aliases=['config', 'configure', 'settings', 'show'],
        usage="config",
        description="Displays current antiraid settings.",
)
    @commands.has_permissions(manage_guild=True)
    async def status(self, ctx):
        try:
            check = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
            if check:
                whens = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
                when = whens[2]
                who = whens[3]
                find = whens[1]
                isenabled = whens[4]
                if "Enabled" in isenabled:
                    isenabled = "<:whitecheck:1243577701638475787>"
                else:
                    isenabled = "<:whitecross:1243852723753844736>"
                defaultpfp = whens[7]
                if defaultpfp and "on" in defaultpfp:
                    defaultpfp = "<:whitecheck:1243577701638475787>"
                else:
                    defaultpfp = "<:whitecross:1243852723753844736>"
                penalty = whens[6]
                whitelisted = whens[5]
                meow = whens[4]

                loger = whens[8]
                if loger is None:
                    logsch = 'None'
                else:
                    logsch = f"<#{str(loger)}>"

                if whitelisted is not None:
                    if whitelisted != 'NULL':
                        whitelisted_users = []
                        for i in whitelisted.split(','):
                            whitelisted_users.append(f"<@{i}>")
                        whitelisted = ' '.join(whitelisted_users)
                    else:
                        whitelisted = "None"
                else:
                    whitelisted = "None"

                embed2 = discord.Embed(title=f"Antiraid Configuration", description=f"Antiraid is currently **{meow}** and will {penalty} any user accounts not made before {find} days ago.", color=0x2f3136)
                embed2.add_field(name="Module", value=f"**Enabled**: {isenabled}\n**Enabled by:** {who}\n**Enabled On:** {when}\n**account age:** <:whitecheck:1243577701638475787>\n**defaultpfp:** {defaultpfp}\n**Penalty:** {penalty}\n**Whitelisted:** {whitelisted}\n**Logs:** {logsch}")
                embed2.set_footer(text=f"Account Age: {find} days")
                await ctx.send(embed=embed2)

            else:
                await ctx.send(embed=discord.Embed(description=f"{xmoji} The antiraid module hasn't been assigned an account age.", color=errorcol))
        except Exception as e:
            print(e)
          

    @antiraid.command(
        aliases=['age', 'set_age'],
        usage='7',
        description="Sets account age for new joins.",
)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 14, commands.BucketType.user)
    async def account_age(self, ctx, age):
        try:
            check = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
            if check:
                if age.isdigit():
                    age = int(age)
                    self.cursor.execute('UPDATE antiraid SET age=? WHERE guild_id=?', (age, ctx.guild.id))
                    self.conn.commit()
                    await asyncio.sleep(1)
                    finddit = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
                    foundit = finddit[1]
                    self.cacheAntiraid.restart()
                    return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid account age is now set to {foundit} days.", color=0x2f3136))
                else:
                    embed = discord.Embed(description=f"{xmoji} Argument must be an integer.", color=errorcol)
                    await ctx.send(embed=embed)
            else:
                if age.isdigit():
                    age = int(age)
                    self.cursor.execute('INSERT INTO antiraid (guild_id, age, time, author, antiraid, ignored, penalty, defaultpfp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (ctx.guild.id, age, None, None, None, None, 'kick', None))
                    self.conn.commit()
                    await asyncio.sleep(1)
                    today = date.today()
                    d2 = today.strftime("%B %d, %Y")
                    self.cursor.execute('UPDATE antiraid SET time=? WHERE guild_id=?', (str(d2), ctx.guild.id))
                    self.cursor.execute('UPDATE antiraid SET author=? WHERE guild_id=?', (str(ctx.author), ctx.guild.id))
                    self.cursor.execute('UPDATE antiraid SET antiraid=? WHERE guild_id=?', ('Enabled', ctx.guild.id))
                    self.conn.commit()
                    await asyncio.sleep(1)
                    finddit = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
                    foundit = finddit[1]
                    self.cacheAntiraid.restart()
                    return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid account age is now set to {foundit} days.", color=0x2f3136))
                else:
                    embed = discord.Embed(description=f"{xmoji} Argument must be an integer.", color=errorcol)
                    await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @antiraid.command(
        aliases=['on'],
        usage='enable',
        description="Enables antiraid in your server",
)
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx):
        check = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
        today = date.today()
        d2 = today.strftime("%B %d, %Y")
        if check:
            await ctx.send(embed=discord.Embed(description=f"{xmoji} The antiraid is already enabled in this server ", color=errorcol))
        else:
            self.cursor.execute('INSERT INTO antiraid (guild_id, age, time, author, antiraid, ignored, penalty, defaultpfp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (ctx.guild.id, '7', d2, str(ctx.author), 'Enabled', None, 'kick', None))
            self.conn.commit()
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid has now been enabled", color=0x2f3136))

    @antiraid.command(
        aliases=['off'],
        usage='disable',
        description="Disables antiraid in your server",
)
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        check = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (ctx.guild.id,)).fetchone()
        if check:
            self.cursor.execute('DELETE FROM antiraid WHERE guild_id=?', (ctx.guild.id,))
            self.conn.commit()
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> The antiraid has now been disabled", color=0x2f3136))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} The antiraid is already disabled in this server! ", color=errorcol))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        #print(f"Member {member.name} joined in {member.guild.name}")
        guild = member.guild
        results = self.cursor.execute('SELECT * FROM antiraid WHERE guild_id=?', (member.guild.id,)).fetchone()

        if results is not None:
            penalty = results[6]
            logs = results[8]
            antir = results[4]
            age = results[1]
            avatarcheck = results[7]
            if logs is not None:
                channel = discord.utils.get(member.guild.text_channels, id=int(logs))
        else:
            pass    
        
        if results:
            if "Enabled" in antir: 
                    if age:
                        now = timedelta(days=age).days
                        seconds = now * 24 * 60 * 60
                        if time.time() - member.created_at.timestamp() < seconds: 
                            if penalty == "kick":
                                try:
                                    embed=discord.Embed(title=f"You've been kicked from {guild.name}!", description=f"<:warn:1199645241729368084> **Reason:** Detected that your account was created less than {now} days ago.", color=0xf23136)
                                    await member.send(embed=embed)

                                    if channel:
                                        loge=discord.Embed(title=f"User kicked", description=f'{member.mention} has been kicked from the server.\n\n**Reason: **Account age less than the minimum.', color=0x2f3136)
                                        await channel.send(embed=loge)

                                except discord.Forbidden:
                                        pass
                                
                                except Exception as e:
                                     print(e)
                                                       
                                try:
                                    await member.kick(reason=f"Incite Antiraid | Account younger than {now} days.")
                                except Exception as e:
                                    print(f"Failed to kick member {member.name} | antiraid: {e}")

                            elif penalty == "ban":
                                try:
                                    embed = discord.Embed(title=f"You've been banned from {guild.name}!", description=f"<:warn:1199645241729368084> **Reason:** Detected that your account was created less than {now} days ago.", color=0xf23136)
                                    await member.send(embed=embed)

                                    if channel:
                                        loge=discord.Embed(title=f"User Banned", description=f'{member.mention} has been banned from the server.\n\n**Reason: **Account age less than the minimum.', color=0x2f3136)
                                        await channel.send(embed=loge)

                                except discord.Forbidden:
                                        pass

                                except Exception as e:
                                    print(e)
                                try:
                                    await member.ban(reason=f"Incite Antiraid | Account younger than {now} days.")
                                except Exception as e:
                                    print(f"Failed to ban member {member.name} | antiraid: {e}")

                    
                    if avatarcheck  == "on":
                        try:
                            if member.avatar is None:
                                if penalty == "kick":
                                    try:
                                        embed = discord.Embed(title=f"You've been kicked from {guild.name}!", description=f"<:warn:1199645241729368084> **Reason:** Detected that your account has no profile picture.", color=0xf23136)
                                        await member.send(embed=embed)

                                        if channel:
                                            loge=discord.Embed(title=f"User kicked", description=f'{member.mention} has been kicked from the server.\n\n**Reason: **User having no pfp or default pfp.', color=0x2f3136)
                                            await channel.send(embed=loge)

                                    except discord.Forbidden:
                                        pass

                                    except Exception as e:
                                        print(e)
                                    try:
                                        await member.kick(reason=f"Incite Antiraid | Account has no profile picture")
                                    except Exception as e:
                                        print(f"Failed to kick member {member.name} | antiraid: {e}")
                                elif penalty == "ban":
                                    try:
                                        embed = discord.Embed(title=f"You've been banned from {guild.name}!", description=f"<:warn:1199645241729368084> **Reason:** Detected that your account has no profile picture.", color=0xf23136)
                                        await member.send(embed=embed)

                                        if channel:
                                            loge=discord.Embed(title=f"User Banned", description=f'{member.mention} has been Banned from the server.\n\n**Reason:** User having no pfp or default pfp.', color=0x2f3136)
                                            await channel.send(embed=loge)

                                    except discord.Forbidden:
                                        pass

                                    except Exception as e:
                                        print(e)
                                    try:
                                        await member.ban(reason=f"Incite Antiraid | Account has no profile picture")
                                    except Exception as e:
                                        print(f"Failed to ban member {member.name} | antiraid: {e}")
                                else:
                                    pass
                        except Exception as e:
                            print(f"Error while processing member {member.name}: {e}")
            else:
                return

def setup(bot):
    bot.add_cog(Antiraid(bot))