
import discord
from discord.ext import commands
import datetime
from utils.Tools import get_db_connection

class vanityroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()

    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vanityroles (
            guild_id INTEGER PRIMARY KEY,
            vanity TEXT,
            role_id INTEGER,
            channel_id INTEGER
        )
        ''')
        
        conn.commit()
        conn.close()

    def get_vanity_config(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT vanity, role_id, channel_id FROM vanityroles WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                "vanity": result[0],
                "role": result[1],
                "channel": result[2]
            }
        return None

    def save_vanity_config(self, guild_id, vanity, role_id, channel_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO vanityroles (guild_id, vanity, role_id, channel_id) VALUES (?, ?, ?, ?)',
            (guild_id, vanity, role_id, channel_id)
        )
        
        conn.commit()
        conn.close()

    def delete_vanity_config(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM vanityroles WHERE guild_id = ?', (guild_id,))
        
        conn.commit()
        conn.close()

    @commands.hybrid_group(aliases=['vr'])
    @commands.has_permissions(administrator=True)
    async def vanityroles(self, ctx):
        prefix = ctx.prefix
        em = discord.Embed(
            title=f"Vanityroles Commands", description=f"<...> Required | [...] Optional", color=0x2f3136)
        em.add_field(name="vanityroles setup", value="Configures the vanityroles module in the server.")
        em.add_field(name="vanityroles reset", value="Reset's all vanityroles configurations in the server.")
        em.add_field(name="vanityroles show", value="Displays all vanityroles configurations in the server.")
        await ctx.reply(embed=em)
      
    @vanityroles.command(name="setup", description="Configures the vanityroles module in the server.")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx, vanity, channel: discord.TextChannel, role: discord.Role):
        if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
            if role.permissions.administrator or role.permissions.ban_members or role.permissions.kick_members:
                embed1 = discord.Embed(
                    description=
                    "Could not setup vanityroles, role must not have administrator permissions enabled.",
                    color=0x2f3136)
                await ctx.send(embed=embed1)
            else:
                self.save_vanity_config(ctx.guild.id, vanity, role.id, channel.id)
                
                embed = discord.Embed(color=0x2f3136)
                embed.set_author(name=f"Vanity Roles Config For {ctx.guild}", icon_url=ctx.author.display_avatar.url, url="https://discord.gg/encoders")
                embed.add_field(name="<:right:1199668086916263956> **__Vanity__**", value='Not Set' if vanity is None else vanity, inline=False)
                embed.add_field(name="<:right:1199668086916263956> **__Role__**", value='Not Set' if role is None else role.mention, inline=False)
                embed.add_field(name="<:right:1199668086916263956> **__Channel__**", value='Not Set' if channel is None else channel.mention, inline=False)

                await ctx.send(embed=embed, mention_author=False)
        else:
            embed5 = discord.Embed(
                description=
                """You have to be top of my role""",
                color=0x2f3136)
            await ctx.reply(embed=embed5, mention_author=False)

    @vanityroles.command(aliases=[('delete','remove')], description="Reset's all vanityroles configurations in the server.")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
            config = self.get_vanity_config(ctx.guild.id)
            if not config:
                embed1 = discord.Embed(
                    description=
                    "Please add vanity roles first",
                    color=0x2f3136)
                await ctx.reply(embed=embed1, mention_author=False)
            else:
                self.delete_vanity_config(ctx.guild.id)
                await ctx.reply(embed=discord.Embed(color=0x2f3136, description="Successfully Removed Vanity-Roles Setup"),
                    mention_author=False)
        else:
            embed5 = discord.Embed(
                description=
                """You have to be top of my role""",
                color=0x2f3136)
            await ctx.reply(embed=embed5, mention_author=False)

    @vanityroles.command(aliases=[("show")], description="Displays all vanityroles configurations in the server.")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        config = self.get_vanity_config(ctx.guild.id)
        if not config:
            embed1 = discord.Embed(
                description=
                "There is no vanity roles configurations to display. Please setup the vanityroles module first.",
                color=0x2f3136)
            embed1.set_footer(text="Use vanityroles setup")
            await ctx.reply(embed=embed1, mention_author=False)
        else:
            vanity = config["vanity"]
            role_id = config["role"]
            channel_id = config["channel"]
            channel = self.bot.get_channel(channel_id)
            role = ctx.guild.get_role(role_id)
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f"Vanity Roles Config For {ctx.guild}", icon_url=ctx.author.display_avatar.url, url="https://discord.gg/encoders")
            embed.add_field(name="<:right:1199668086916263956> **__Vanity__**", value='Not Set' if vanity is None else vanity, inline=False)
            embed.add_field(name="<:right:1199668086916263956> **__Role__**", value='Not Set' if role is None else role.mention, inline=False)
            embed.add_field(name="<:right:1199668086916263956> **__Channel__**", value='Not Set' if channel is None else channel.mention, inline=False)

            await ctx.send(embed=embed, mention_author=False)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        try:
            if before.bot or before.guild.id != after.guild.id or before.activity == after.activity or before.status == discord.Status.offline:
                return

            if after.activity is None or before.activity == after.activity:
                return

            config = self.get_vanity_config(after.guild.id)
            if not config:
                return

            vanity = config["vanity"]
            role_id = config["role"]
            channel_id = config["channel"]

            gchannel = self.bot.get_channel(channel_id)
            grole = after.guild.get_role(role_id)

            if not grole or not gchannel:
                return

            if vanity.lower() in after.activity.name.lower() and grole not in after.roles:
                await after.add_roles(grole, reason="Incite | Vanity roles")
                embed = discord.Embed(color=0x2f3136, description=f"{after.mention} added `{vanity}` in their status, successfully added vanity role.",
                                  timestamp=datetime.datetime.utcnow())
                embed.set_author(name=after.name, icon_url=after.display_avatar.url)
                embed.set_footer(text="Incite - Vanityroles")
                await gchannel.send(embed=embed)

            elif vanity.lower() not in after.activity.name.lower() and grole in after.roles:
                await after.remove_roles(grole, reason="Incite | Vanity roles")
                embed = discord.Embed(color=0x2f3136, description=f"{after.mention} changed their status, successfully removing vanity role.",
                                  timestamp=datetime.datetime.utcnow())
                embed.set_author(name=after.name, icon_url=after.display_avatar.url)
                embed.set_footer(text="Incite Vanityroles")
                await gchannel.send(embed=embed)
        except Exception as e:
            print(f"Error in On presence update Vanityroles: {e}")