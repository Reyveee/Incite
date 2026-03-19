import contextlib
from traceback import format_exception
from aiohttp import ClientSession
import discord
from discord.ext import commands
#import notedb
#from notedb import *
import io
import textwrap
import pymongo
import datetime
import sys
from discord.ui import Button, View
import psutil
import re 
import time
import datetime
import platform
from utils.Tools import *
from io import BytesIO
import ast
import logging
from discord.ext import commands
from pymongo import MongoClient
from discord.ext.commands import BucketType, cooldown
import requests
from typing import *
from typing import Union, Optional
from utils import *
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from core import Cog, Astroz, Context
from typing import Optional
from discord import app_commands
from discord.utils import get
import pathlib

start_time = time.time()
EMOJI_REGEX = r'<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>'

MAIN_COLOR = 0x2f3136  #Main colour for bot's embed
RED_COLOR = 0xFF0000  #Red colour for error embeds

#EMOJI'S FOR BOT


SUPPORT_SERVER_LINK = "https://discord.gg/encoders"




def datetime_to_seconds(thing: datetime.datetime):
    current_time = datetime.datetime.fromtimestamp(time.time())
    return round(
        round(time.time()) +
        (current_time - thing.replace(tzinfo=None)).total_seconds())

class Confirm(discord.ui.View):
    def __init__(self, context: commands.Context, timeout: Optional[int] = 300, user: Optional[Union[discord.Member, discord.User]] = None):
        super().__init__(timeout=timeout)
        self.value = None
        self.context = context
        self.user = user or self.context.author

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes(self, b, i):
        self.value = True
        self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no(self, b, i):
        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot interact in other's commands.", ephemeral=True)
            return False
        return True
    
class StickerFlags(commands.FlagConverter, prefix="--", delimiter=" ", case_insensitive=True):
    name: Optional[str] = None
    description: Optional[str] = None
    emoji: Optional[str] = None

class CalculatorButton(Button):
    def __init__(self, label, style=discord.ButtonStyle.grey, custom_id=None, row=None):
        super().__init__(label=label, style=style, custom_id=custom_id, row=row)
        
    async def callback(self, interaction: discord.Interaction):
        view: CalculatorView = self.view
        value = self.label
        
        if value == "=":
            view.expression = view.evaluate_expression()
        elif value == "C":
            view.expression = ""
        elif value == "⌫":
            view.expression = view.expression[:-1]
        else:
            view.expression += value
            
        embed = discord.Embed(
            title="Calculator",
            description=f"```\n{view.expression or '0'}\n```",
            color=0x2f3136
        )
        embed.set_footer(text="________________________________________")
        await interaction.response.edit_message(embed=embed, view=view)

class CalculatorView(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.expression = ""
        self.ctx = ctx
        self.setup_buttons()

    def setup_buttons(self):
        controls = ['C', '(', ')', '÷']
        for i, ctrl in enumerate(controls):
            style = discord.ButtonStyle.red if ctrl == 'C' else discord.ButtonStyle.blurple if ctrl == '÷' else discord.ButtonStyle.grey
            self.add_item(CalculatorButton(ctrl, style=style, row=0))

        numbers = [
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+']
        ]
        
        for row, row_numbers in enumerate(numbers, 1):
            for i, num in enumerate(row_numbers):
                style = discord.ButtonStyle.blurple if num in ['×', '-', '+'] else discord.ButtonStyle.grey
                self.add_item(CalculatorButton(num, style=style, row=row))

        last_row = ['0', '.', '=', '⌫']
        for i, label in enumerate(last_row):
            style = discord.ButtonStyle.green if label == '=' else discord.ButtonStyle.red if label == '⌫' else discord.ButtonStyle.grey
            self.add_item(CalculatorButton(label, style=style, row=4))

    async def update_message(self, interaction):
        embed = discord.Embed(
            title="Calculator",
            description=f"```\n{self.expression or '0'}\n```",
            color=0x2f3136
        )
        embed.set_footer(text="________________________________________")
        await interaction.response.edit_message(embed=embed, view=self)

    def evaluate_expression(self):
        try:
            expr = self.expression.replace('×', '*').replace('÷', '/')
            
            tree = ast.parse(expr, mode='eval')
            
            def validate_node(node):
                if isinstance(node, (ast.Num, ast.Expression)):
                    return True
                elif isinstance(node, ast.BinOp):
                    allowed_ops = (ast.Add, ast.Sub, ast.Mult, ast.Div)
                    if not isinstance(node.op, allowed_ops):
                        raise ValueError("Invalid operation")
                    return validate_node(node.left) and validate_node(node.right)
                else:
                    raise ValueError("Invalid expression")

            if validate_node(tree.body):
                result = eval(compile(tree, '<string>', 'eval'))
                if isinstance(result, float):
                    result = round(result, 6)
                    if result.is_integer():
                        result = int(result)
                return str(result)
        except:
            return "Error"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This calculator is not for you!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass
class Extra(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.cid = 1117073053256527952



    @blacklist_check()
    @ignore_check()
    @commands.hybrid_command(name='calc', aliases=['calculate', 'math'])
    async def calculator(self, ctx, *, expression: str = None):
        if expression:
            expression = expression.replace('x', '*').replace('÷', '/')
            expression = ''.join(c for c in expression if c.isdigit() or c in '+-*/.() ')

            try:
                tree = ast.parse(expression, mode='eval')
        
                def validate_node(node):
                    if isinstance(node, (ast.Num, ast.Expression)):
                        return True
                    elif isinstance(node, ast.BinOp):
                        allowed_ops = (ast.Add, ast.Sub, ast.Mult, ast.Div)
                        if not isinstance(node.op, allowed_ops):
                            raise ValueError("Invalid operation")
                        return validate_node(node.left) and validate_node(node.right)
                    else:
                        raise ValueError("Invalid expression")

                if validate_node(tree.body):
                    result = eval(compile(tree, '<string>', 'eval'))

                    if isinstance(result, float):
                        result = round(result, 6)
                        if result.is_integer():
                            result = int(result)

                    embed = discord.Embed(
                        title="Calculator",
                        color=0xFFFFFF
                    )
                    embed.add_field(
                        name="Expression",
                        value=f"```py\n{expression}```",
                        inline=False
                    )
                    embed.add_field(
                        name="Result",
                        value=f"```py\n{result}```",
                        inline=False
                    )
            
                    embed.set_footer(
                        text="Supported operations: + (add), - (subtract), * (multiply), / (divide)"
                    )

                    await ctx.send(content=result, embed=embed)

            except (SyntaxError, ValueError, ZeroDivisionError, TypeError) as e:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description=f"Invalid expression: {str(e)}",
                    color=discord.Color.red()
                )
                error_embed.add_field(
                    name="Example Usage",
                    value="```!calc 2 + 2\n!calc (5 * 3) / 2\n!calc 10 - (3 + 2)```",
                    inline=False
                )
                await ctx.send(embed=error_embed)    
        else:
            view = CalculatorView(ctx)
            embed = discord.Embed(
                title="Calculator",
                description="```\n0\n```",
                color=0x2f3136
            )
            embed.set_footer(text="________________________________________")
            view.message = await ctx.send(embed=embed, view=view)                            

    @commands.hybrid_group(name="banner")
    async def banner(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @banner.command(name="server", description="Displays server's banner.")
    async def server(self, ctx):
        if not ctx.guild.banner:
            await ctx.reply("This server does not have a banner.")
        else:
            webp = ctx.guild.banner.replace(format='webp')
            jpg = ctx.guild.banner.replace(format='jpg')
            png = ctx.guild.banner.replace(format='png')
            embed = discord.Embed(
                color=0x2f3136,
                description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
                if not ctx.guild.banner.is_animated() else
                f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({ctx.guild.banner.replace(format='gif')})"
            )
            embed.set_image(url=ctx.guild.banner)
            embed.set_author(name=ctx.guild.name,
                             icon_url=ctx.guild.icon.url
                             if ctx.guild.icon else ctx.guild.default_icon.url)
            embed.set_footer(
                text=f"Requested By {ctx.author}",
                icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=embed)

    @blacklist_check()
    @ignore_check()
    @banner.command(name="user", description="Displays user's banner.")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _user(self,
                    ctx,
                    member: Optional[Union[discord.Member,
                                           discord.User]] = None):
        if member == None or member == "":
            member = ctx.author
        bannerUser = await self.bot.fetch_user(member.id)
        if not bannerUser.banner:
            await ctx.reply("{} does not have a banner.".format(member))
        else:
            webp = bannerUser.banner.replace(format='webp')
            jpg = bannerUser.banner.replace(format='jpg')
            png = bannerUser.banner.replace(format='png')
            embed = discord.Embed(
                color=0x2f3136,
                description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
                if not bannerUser.banner.is_animated() else
                f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({bannerUser.banner.replace(format='gif')})"
            )
            embed.set_author(name=f"{member}",
                             icon_url=member.avatar.url
                             if member.avatar else member.default_avatar.url)
            embed.set_image(url=bannerUser.banner)
            embed.set_footer(
                text=f"Requested By {ctx.author}",
                icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)

            await ctx.send(embed=embed)


    @blacklist_check()
    @ignore_check()
    @commands.hybrid_command(name = "weather", help="Shows weather of a city", description="Shows weather of a city")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def weather(self, ctx, *, city: str):
        api_key = "df3eebb6044eed109f5a6727be3d5a5c"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = city
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)

        x = response.json()
        channel = ctx.message.channel
        if x["cod"] != "404":
            async with channel.typing():
                y = x["main"]
                current_temperature = y["temp"]
                current_temperature_celsiuis = str(round(current_temperature - 273.15))
                current_pressure = y["pressure"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                weather_description = z[0]["description"]
                embed = discord.Embed(
                title=f"Weather in {city_name}",
                color=0x2f3136,
                timestamp=ctx.message.created_at,)
                embed.add_field(name="Descripition",
                            value=f"**{weather_description}**",
                            inline=False)
                embed.add_field(name="Temperature(C)",
                            value=f"**{current_temperature_celsiuis}°C**",
                            inline=False)
                embed.add_field(name="Humidity(%)",
                            value=f"**{current_humidity}%**",
                            inline=False)
                embed.add_field(name="Atmospheric Pressure(hPa)",
                            value=f"**{current_pressure}hPa**",
                            inline=False)
                embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
                embed.set_footer(text=f"Requested by {ctx.author.name}",icon_url=ctx.author.avatar.url)
                await channel.send(embed=embed)


    @commands.hybrid_command(name="invite", aliases=['inv'], description="Get my invite link!"
                              )
    @blacklist_check()
    @ignore_check()
    async def invite(self, ctx: commands.Context):
        cid = 1117073053256527952
        embed = discord.Embed(
            description=f"**Useful links are provided below!**",
            color=0x2f3136)
        embed.set_author(name=f"{ctx.author.name}",
                         icon_url=f"{ctx.author.avatar}")
        b = Button(label='Invite Me', style=discord.ButtonStyle.link, url=f'https://discord.com/oauth2/authorize?client_id={self.cid}&permissions=2113268958&scope=bot')
        hacker = Button(label='Support Server', style=discord.ButtonStyle.link, url=f'https://discord.com/invite/encoders-community-1058660812182519921')
        button_v = Button(label='Vote Me', style=discord.ButtonStyle.link, url=f'https://top.gg/bot/{self.cid}/vote')
        view = View()
        view.add_item(b)
        view.add_item(hacker)
        view.add_item(button_v)
        await ctx.send(embed=embed, view=view)

    @blacklist_check()
    @ignore_check()
    @commands.hybrid_command(name="botinfo",
                             aliases=['bi', 'stats', 'statistics'],
                             help="Get information about me!",
                             with_app_command=True)
    async def botinfo(self, ctx: commands.Context):
        users = sum(g.member_count for g in self.bot.guilds
                    if g.member_count != None)

        initial_embed = discord.Embed(color=0x2f3136,
                              title="Official Server Invite",
                              url="https://discord.com/invite/encoders-community-1058660812182519921",
                              description=f"""
                              The **Ultimate** Discord Bot for **Unparalleled** Functionality and Excitement!
                              
__**Bot Info**__
**Servers:** {len(self.bot.guilds)}
**Users:** Cached {users}
**Commands: **Total {len(set(self.bot.walk_commands()))}
**Shards:** {len(self.bot.shards)}
**Uptime:** {str(datetime.timedelta(seconds=int(round(time.time()-start_time))))}
**Latency:** {int(self.bot.latency * 1000)} ms
""")
        initial_embed.set_footer(text=f"Requested By {ctx.author}",
                         icon_url=ctx.author.avatar.url if ctx.author.avatar
                         else ctx.author.default_avatar.url)
        initial_embed.set_author(name="Ash & Sam",
        icon_url=
        "https://images-ext-2.discordapp.net/external/LiNdAeOepRk83Aw1cIDH2pbwPWA9VGXEbPbmeD3FjuE/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1071821844006576159/8d09b1364c4e8054991438e306e05e2a.png?format=webp&quality=lossless"
        )
        
        #Buttons
        stats_button = Button(label="Stats", style=discord.ButtonStyle.gray, custom_id="stats")
        system_info = Button(label="System Info", style=discord.ButtonStyle.gray, custom_id="system_info")
        update_logs = Button(label="Update Logs", style=discord.ButtonStyle.gray, custom_id="update_logs")

        view = discord.ui.View()
        view.add_item(stats_button)
        view.add_item(system_info)
        view.add_item(update_logs)

        await ctx.send(embed=initial_embed, view=view)

        async def stats_callback(interaction: discord.Interaction):
            stats_embed = discord.Embed(
                description=f"""
__**Bot Info**__
**Servers:** {len(self.bot.guilds)}
**Users:** Cached {users}
**Commands: **Total {len(set(self.bot.walk_commands()))}
**Shards:** {len(self.bot.shards)}
**Uptime:** {str(datetime.timedelta(seconds=int(round(time.time()-start_time))))}
**Latency:** {int(self.bot.latency * 1000)}ms
""",
                color=0x2f3136
                )
            stats_embed.set_author(name="Ash & Sam",
        icon_url=
        "https://images-ext-2.discordapp.net/external/LiNdAeOepRk83Aw1cIDH2pbwPWA9VGXEbPbmeD3FjuE/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1071821844006576159/8d09b1364c4e8054991438e306e05e2a.png?format=webp&quality=lossless"
        )
                
            await interaction.response.edit_message(embed=stats_embed)

        async def system_callback(interaction: discord.Interaction):
            system_embed = discord.Embed(
                description=f"""
__**System**__
**CPU usage:** {round(psutil.cpu_percent())}%
**Memory usage:** {int((psutil.virtual_memory().total - psutil.virtual_memory().available)
 / 2560 / 2560)} MB
""",
                color=0x2f3136
                )
            system_embed.set_author(name="Ash & Sam",
        icon_url=
        "https://images-ext-2.discordapp.net/external/LiNdAeOepRk83Aw1cIDH2pbwPWA9VGXEbPbmeD3FjuE/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1071821844006576159/8d09b1364c4e8054991438e306e05e2a.png?format=webp&quality=lossless"
        )
                
            await interaction.response.edit_message(embed=system_embed)

        async def update_callback(interaction: discord.Interaction):
            update_embed = discord.Embed(
                title="Update Logs",
                description=f"Click to view latest updates: [Encoders](https://discord.com/invite/encoders-community-1058660812182519921):[#Incite](https://ptb.discord.com/channels/1058660812182519921/1114404505400918086)",
                color=0x2f3136
                )
            update_embed.set_author(name="Ash & Sam",
        icon_url=
        "https://images-ext-2.discordapp.net/external/LiNdAeOepRk83Aw1cIDH2pbwPWA9VGXEbPbmeD3FjuE/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1071821844006576159/8d09b1364c4e8054991438e306e05e2a.png?format=webp&quality=lossless"
        )
                
            await interaction.response.edit_message(embed=update_embed)

        stats_button.callback = stats_callback
        system_info.callback = system_callback
        update_logs.callback = update_callback
        
    @commands.hybrid_command(name="uptime", description="Displays bot's uptime.")
    async def uptime(self, ctx):
        uptime = datetime.timedelta(seconds=int(round(time.time() - self.start_time)))

        embed = discord.Embed(
            description=f"The bot has been running for: {str(uptime)}",
            color=0x2f3136
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo",
                           aliases=["sinfo", "si", "serveri"],
                           with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def serverinfo(self, ctx: commands.Context):
        c_at = int(ctx.guild.created_at.timestamp())
        nsfw_level = ''
        if ctx.guild.nsfw_level.name == 'default':
            sfw_level = 'Default'
        if ctx.guild.nsfw_level.name == 'explicit':
            nsfw_level = 'Explicit'
        if ctx.guild.nsfw_level.name == 'safe':
            nsfw_level = 'Safe'
        if ctx.guild.nsfw_level.name == 'age_restricted':
            nsfw_level = 'Age Restricted'
            
        guild: discord.Guild = ctx.guild
        t_emojis = len(guild.emojis)
        t_stickers = len(guild.stickers)
        total_emojis = t_emojis + t_stickers
        
        # Create the buttons
        home_button = discord.ui.Button(
            label="General",
            style=discord.ButtonStyle.gray,
            custom_id="home"
            )
        members_button = discord.ui.Button(
            label="Count",
            style=discord.ButtonStyle.gray,
            custom_id="members"
            )
        channels_button = discord.ui.Button(
            label="Channels",
            style=discord.ButtonStyle.gray,
            custom_id="channels"
            )
        boost_features_button = discord.ui.Button(
            label="Boost Features",
            style=discord.ButtonStyle.gray,
            custom_id="boost"
            )
        moderation_button = discord.ui.Button(
            label="Moderation",
            style=discord.ButtonStyle.gray,
            custom_id="moderation"
            )
        view = discord.ui.View()
        view.add_item(home_button)
        view.add_item(members_button)
        view.add_item(channels_button)
        view.add_item(boost_features_button)
        view.add_item(moderation_button)
        
        initial_embed = discord.Embed(
            title="Server Information",
            description=f"**Description:** {guild.description}\n\n**Owner:** {guild.owner.mention}\n**ID:** {guild.id}\n**Created:** <t:{c_at}:F>",
            color=0x2f3136
            )
        
        if guild.icon is not None:
            initial_embed.set_thumbnail(url=guild.icon.url)
        if guild.banner is not None:
            initial_embed.set_image(url=guild.banner.url)
            
        await ctx.send(embed=initial_embed, view=view)
        
        async def home_callback(interaction: discord.Interaction):
            home_embed = discord.Embed(
                title="Server Information",
                description=f"**Description:** {guild.description}\n\n**Owner:** {guild.owner.mention}\n**ID:** {guild.id}\n**Created:** <t:{c_at}:F>",
                color=0x2f3136
                )
            home_embed.set_thumbnail(url=guild.icon.url)
            
            if guild.banner is not None:
                home_embed.set_image(url=guild.banner.url)
                
            await interaction.response.edit_message(embed=home_embed)
            
        async def members_callback(interaction: discord.Interaction):
            emojis = guild.emojis
            emoji_count = len(emojis)
            sticker_count = len([e for e in emojis if e.animated])
            members_embed = discord.Embed(
                title="Guild Counts",
                description=f"**Members**\nTotal: {len(guild.members)}\nHumans: {len(list(filter(lambda m: not m.bot, guild.members)))}\nBots: {len(list(filter(lambda m: m.bot, guild.members)))}\n\n**Emojis / Stickers**\nTotal Emojis Count: {emoji_count}\nAnimated Emojis Count: {sticker_count}",
                color=0x2f3136
                )
                
            members_embed.set_thumbnail(url=guild.icon.url)
            await interaction.response.edit_message(embed=members_embed)
                
        async def channels_callback(interaction: discord.Interaction):    
            channels_embed = discord.Embed(
                title="Channels",
                description=f"Categories: {len(guild.categories)}\nText Channels: {len(guild.text_channels)}\nVoice Channels: {len(guild.voice_channels)}\nThreads: {len(guild.threads)}",
                color=0x2f3136
                )
            channels_embed.set_thumbnail(url=guild.icon.url)
            await interaction.response.edit_message(embed=channels_embed)
                
        async def boost_callback(interaction: discord.Interaction):
            boost_count = guild.premium_subscription_count
            boost_level = guild.premium_tier
            boost_embed = discord.Embed(
                title="Boost",
                description=f"Level\n{boost_level}\nBoost Amount\n{boost_count}", 
                color=0x2f3136
                )
            boost_embed.set_thumbnail(url=guild.icon.url)
            await interaction.response.edit_message(embed=boost_embed)
                
        async def moderation_callback(interaction: discord.Interaction):
            moderation_embed = discord.Embed(
                title="Moderation",
                description=f"**Roles**\n{len(guild.roles)}\n**Verification Level**\n{str(guild.verification_level).title()}\n",
                color=0x2f3136
                )
            moderation_embed.set_thumbnail(url=guild.icon.url)
            await interaction.response.edit_message(embed=moderation_embed)

        home_button.callback = home_callback
        members_button.callback = members_callback
        channels_button.callback = channels_callback
        boost_features_button.callback = boost_callback
        moderation_button.callback = moderation_callback
                
            


    @blacklist_check()
    @ignore_check()
    @commands.hybrid_command(name="userinfo",
                             aliases=["whois", "ui"],
                             usage="Userinfo [user]",
                             with_app_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _userinfo(self,
                        ctx,
                        member: Optional[Union[discord.Member,
                                               discord.User]] = None):
        if member == None or member == "":
            member = ctx.author
        elif member not in ctx.guild.members:
            member = await self.bot.fetch_user(member.id)

        activity = member.activity
        if activity is None:
            activity_str = "None"
        elif isinstance(activity, discord.CustomActivity):
            activity_str = f"{activity.name} ({activity.type.name})"
        else:
            activity_str = f"{activity.name} ({activity.type.name})"

        badges = ""
        if member.public_flags.hypesquad:
            badges += "<:HypeEvent:1199665544928952352> "
        if member.public_flags.hypesquad_balance:
            badges += "<:Balance:1199663719945347072> "
        if member.public_flags.hypesquad_bravery:
            badges += "<:Bravery:1199663721140719676> "
        if member.public_flags.hypesquad_brilliance:
            badges += "<:Brilliance:1199663723908968560> "
        if member.public_flags.early_supporter:
            badges += "<:Early:1199663725129519215> "
        if member.public_flags.active_developer:
            badges += "<:Discord_ActiveDeveloper:1372935545788829808> "
        if member.public_flags.verified_bot_developer:
            badges += "<:VerifiedBotDev:1199663726207451158> "
        if member.public_flags.discord_certified_moderator:
            badges += "<:Certifiedmod:1199665546233385060> "
        if member.public_flags.staff:
            badges += "<:Staff:1199665548271833138> "
        if member.public_flags.partner:
            badges += "<:Partnered:1199665549827920003> "
        if badges == None or badges == "":
            badges += "None"

        if member in ctx.guild.members:
            nickk = f"{member.nick if member.nick else 'None'}"
            joinedat = f"<t:{round(member.joined_at.timestamp())}:R>"
        else:
            nickk = "None"
            joinedat = "None"

        kp = ""
        if member in ctx.guild.members:
            if member.guild_permissions.kick_members:
                kp += "Kick Members"
            if member.guild_permissions.ban_members:
                kp += ", Ban Members"
            if member.guild_permissions.administrator:
                kp += ", Administrator"
            if member.guild_permissions.manage_channels:
                kp += ", Manage Channels"


            if member.guild_permissions.manage_guild:
                kp = "Manage Server"
            if member.guild_permissions.manage_messages:
                kp += ", Manage Messages"
            if member.guild_permissions.mention_everyone:
                kp += ", Mention Everyone"
            if member.guild_permissions.manage_nicknames:
                kp += ", Manage Nicknames"
            if member.guild_permissions.manage_roles:
                kp += ", Manage Roles"
            if member.guild_permissions.manage_webhooks:
                kp += ", Manage Webhooks"
            if member.guild_permissions.manage_emojis:
                kp += ", Manage Emojis"

            if kp is None or kp == "":
                kp = "None"

        if member in ctx.guild.members:
            if member == ctx.guild.owner:
                aklm = "Server Owner"
            elif member.guild_permissions.administrator:
                aklm = "Server Administrator"
            elif member.guild_permissions.ban_members or member.guild_permissions.kick_members:
                aklm = "Server Moderator"
            else:
                aklm = "Server Member"

        bannerUser = await self.bot.fetch_user(member.id)
        embed = discord.Embed(color=0x2f3136)
        embed.timestamp = discord.utils.utcnow()
        if not bannerUser.banner:
            pass
        else:
            embed.set_image(url=bannerUser.banner)
        embed.set_author(name=f"{member.name}'s Information",
                         icon_url=member.avatar.url
                         if member.avatar else member.default_avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.
                            default_avatar.url)
        embed.add_field(name="__General Information__",
                        value=f"""
**Name:** {member}
**ID:** {member.id}
**Nickname:** {nickk}
**Bot?:** {'<:en_tick:1199658108532826252> Yes' if member.bot else '<:en_cross:1199658158059159654> No'}
**Badges:** {badges}
**Status:** {member.status}
**Activity:** {activity_str}
**Account Created:** <t:{round(member.created_at.timestamp())}:R>
**Server Joined:** {joinedat}
            """,
                        inline=False)
        if member in ctx.guild.members:
            r = (', '.join(role.mention for role in member.roles[1:][::-1])
                 if len(member.roles) > 1 else 'None.')
            embed.add_field(name="__Role Info__",
                            value=f"""
**Highest Role:** {member.top_role.mention if len(member.roles) > 1 else 'None'}
**Roles [{f'{len(member.roles) - 1}' if member.roles else '0'}]:** {r if len(r) <= 1024 else r[0:1006] + ' and more...'}
**Color:** {member.color if member.color else '000000'}
                """,
                            inline=False)
        if member in ctx.guild.members:
            embed.add_field(
                name="__Extra__",
                value=
                f"**Boosting:** {f'<t:{round(member.premium_since.timestamp())}:R>' if member in ctx.guild.premium_subscribers else 'None'}\n**Voice <:voice:1199317325309030440>:** {'None' if not member.voice else member.voice.channel.mention}",
                inline=False)
        if member in ctx.guild.members:
            embed.add_field(name="__Key Permissions__",
                            value=", ".join([kp]),
                            inline=False)
        if member in ctx.guild.members:
            embed.add_field(name="__Acknowledgement__",
                            value=f"{aklm}",
                            inline=False)
        if member in ctx.guild.members:
            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
        else:
            if member not in ctx.guild.members:
                embed.set_footer(
                    text=f"{member.name} not in this this server.",
                    icon_url=ctx.author.avatar.url
                    if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="roleinfo",
                             help="Shows you all information about a role.",
                             usage="Roleinfo <role>",
                             with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def roleinfo(self, ctx: commands.Context, *, role: discord.Role):
        """Get information about a role"""
        content = discord.Embed(title=f"@{role.name} | #{role.id}")

        content.colour = role.color

        if isinstance(role.icon, discord.Asset):
            content.set_thumbnail(url=role.icon.url)
        elif isinstance(role.icon, str):
            content.title = f"{role.icon} @{role.name} | #{role.id}"

        content.add_field(name="Color", value=str(role.color).upper())
        content.add_field(name="Member count", value=len(role.members))
        content.add_field(name="Created at",
                          value=role.created_at.strftime("%d/%m/%Y %H:%M"))
        content.add_field(name="Hoisted", value=str(role.hoist))
        content.add_field(name="Mentionable", value=role.mentionable)
        content.add_field(name="Mention", value=role.mention)
        if role.managed:
            if role.tags.is_bot_managed():
                manager = ctx.guild.get_member(role.tags.bot_id)
            elif role.tags.is_integration():
                manager = ctx.guild.get_member(role.tags.integration_id)
            elif role.tags.is_premium_subscriber():
                manager = "Server boosting"
            else:
                manager = "UNKNOWN"
            content.add_field(name="Managed by", value=manager)

        perms = []
        for perm, allow in iter(role.permissions):
            if allow:
                perms.append(f"`{perm.upper()}`")

        if perms:
            content.add_field(name="Allowed permissions",
                              value=" ".join(perms),
                              inline=False)

        await ctx.send(embed=content)


    @commands.command(name="emoji",
                      help="Shows emoji syntax",
                      usage="emoji <emoji>")
    @blacklist_check()
    @ignore_check()
    async def emoji(self, ctx, emoji: discord.Emoji):
        return await ctx.send(embed=discord.Embed(
            title="**emoji**",
            description="emoji: %s\nid: **`%s`**" % (emoji, emoji.id),
            color=0x2f3136))

    @commands.command(name="user",
                      help="Shows user syntax",
                      usage="user [user]",
                      with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def user(self, ctx, user: discord.Member = None):
        return await ctx.send(
            embed=discord.Embed(title="user",
                                description="user: %s\nid: **`%s`**" %
                                (user.mention, user.id),
                                color=0x2f3136))

    @commands.command(name="channel",
                      help="Shows channel syntax",
                      usage="channel <channel>")
    @blacklist_check()
    @ignore_check()
    async def channel(self, ctx, channel: discord.TextChannel):
        return await ctx.send(
            embed=discord.Embed(title="channel",
                                description="channel: %s\nid: **`%s`**" %
                                (channel.mention, channel.id),
                                color=0x2f3136))

    @commands.command(name="boostcount",
                      help="Shows boosts count",
                      usage="boosts",
                      aliases=["boostc", "bcount"],
                      with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def boosts(self, ctx):
        await ctx.send(
            embed=discord.Embed(title=f"Boosts Count",
                                description="**%s**" %
                                (ctx.guild.premium_subscription_count),
                                color=0x2f3136))

    @commands.group(name="list",
                           invoke_without_command=True,
                           with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def __list_(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @__list_.command(name="boosters",
                     aliases=["boost", "booster"],
                     usage="List boosters",
                     help="ᗣ See a list of boosters in the server.",
                     with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_boost(self, ctx):
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{round(mem.premium_since.timestamp())}:R>"
            for no, mem in enumerate(guild.premium_subscribers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=
            f"List of Boosters in {guild.name} - {len(guild.premium_subscribers)}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(
        name="inrole",
        aliases=["inside-role"],
        help="ᗣ See a list of members that are in the specified role .",
        with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_inrole(self, ctx, role: discord.Role):
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
            for no, mem in enumerate(role.members, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"List of Members in {role} - {len(role.members)}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="emojis",
                     aliases=["emoji"],
                     help="Shows you all emojis in the server with ids",
                     with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_emojis(self, ctx):
        guild = ctx.guild
        entries = [
            f"`[{no}]` | {e} - `{e}`"
            for no, e in enumerate(ctx.guild.emojis, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"List of Emojis in {guild.name} - {len(ctx.guild.emojis)}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="roles",
                     aliases=["role"],
                     help="Shows you all roles in the server with ids",
                     with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_roles(self, ctx):
        guild = ctx.guild
        entries = [
            f"`[{no}]` | {e.mention} - `[{e.id}]`"
            for no, e in enumerate(ctx.guild.roles, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"List of Roles in {guild.name} - {len(ctx.guild.roles)}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="bots",
                     aliases=["bot"],
                     help="Get a list of All Bots in a server .",
                     with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_bots(self, ctx):
        guild = ctx.guild
        people = filter(lambda member: member.bot, ctx.guild.members)
        people = sorted(people, key=lambda member: member.joined_at)
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}]"
            for no, mem in enumerate(people, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Bots in {guild.name} - {len(people)}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="admins",
                     aliases=["admin"],
                     help="Get a list of All Admins of a server .",
                     with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_admin(self, ctx):
        hackers = ([
            hacker for hacker in ctx.guild.members
            if hacker.guild_permissions.administrator
        ])
        #hackers = filter(lambda hacker: not hacker.bot)
        hackers = sorted(hackers, key=lambda hacker: not hacker.bot)
        admins = len([
            hacker for hacker in ctx.guild.members
            if hacker.guild_permissions.administrator
        ])
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
            for no, mem in enumerate(hackers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Admins in {guild.name} - {admins}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="invoice", aliases=["invc"], with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def listusers(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("You are not connected to a voice channel")
        members = ctx.author.voice.channel.members
        entries = [
            f"`[{n}]` | {member} [{member.mention}]"
            for n, member in enumerate(members, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=
            f"Voice List of {ctx.author.voice.channel.name} - {len(members)}",
            color=0x2f3136),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="moderators",
                     aliases=["mods"],
                     with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_mod(self, ctx):
        hackers = ([
            hacker for hacker in ctx.guild.members
            if hacker.guild_permissions.ban_members
            or hacker.guild_permissions.kick_members
        ])
        hackers = filter(lambda member: member.bot, ctx.guild.members)
        hackers = sorted(hackers, key=lambda hacker: hacker.joined_at)
        admins = len([
            hacker for hacker in ctx.guild.members
            if hacker.guild_permissions.ban_members
            or hacker.guild_permissions.kick_members
        ])
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
            for no, mem in enumerate(hackers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Mods in {guild.name} - {admins}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="early", aliases=["sup"], with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_early(self, ctx):
        hackers = ([
            hacker for hacker in ctx.guild.members
            if hacker.public_flags.early_supporter
        ])
        hackers = sorted(hackers, key=lambda hacker: hacker.created_at)
        admins = len([
            hacker for hacker in ctx.guild.members
            if hacker.public_flags.early_supporter
        ])
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id})  [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
            for no, mem in enumerate(hackers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Early Id's in {guild.name} - {admins}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="activedeveloper",
                     aliases=["activedev"],
                     with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_activedeveloper(self, ctx):
        hackers = ([
            hacker for hacker in ctx.guild.members
            if hacker.public_flags.active_developer
        ])
        hackers = sorted(hackers, key=lambda hacker: hacker.created_at)
        admins = len([
            hacker for hacker in ctx.guild.members
            if hacker.public_flags.active_developer
        ])
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
            for no, mem in enumerate(hackers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Active Developer Id's in {guild.name} - {admins}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="createpos", with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_cpos(self, ctx):
        hackers = ([hacker for hacker in ctx.guild.members])
        hackers = sorted(hackers, key=lambda hacker: hacker.created_at)
        admins = len([hacker for hacker in ctx.guild.members])
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) - <t:{int(mem.created_at.timestamp())}:D>"
            for no, mem in enumerate(hackers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Creation every id in {guild.name} - {admins}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @__list_.command(name="joinpos", with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def list_joinpos(self, ctx):
        hackers = ([hacker for hacker in ctx.guild.members])
        hackers = sorted(hackers, key=lambda hacker: hacker.joined_at)
        admins = len([hacker for hacker in ctx.guild.members])
        guild = ctx.guild
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) Joined At - <t:{int(mem.joined_at.timestamp())}:D>"
            for no, mem in enumerate(hackers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Join Position of every user in {guild.name} - {admins}",
            description="",
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @commands.hybrid_command(
        name="roleicon",
        help="Set the icon for a role",
        usage="roleicon <role> <icon>",
        aliases=["setroleicon"],
        with_app_command=True
    )
    async def roleicon(self, ctx, role: discord.Role, *, emoji: discord.PartialEmoji = None):
        if ctx.guild.premium_subscription_count <=6:
            embed = discord.Embed(description="This server does not support roleicons.", color=0x2f3136)
            await ctx.send(embed=embed)
            return

        if emoji is None:
            await role.edit(display_icon=None,reason=f"Roleicons command by {ctx.author}")
            embed = discord.Embed(description=f"Successfully updated the roleicon for {role.name}.", color=0x2f3136)
            await ctx.send(embed=embed)

        else:
            emoji_op = await emoji.read()

            await role.edit(display_icon=emoji_op,reason=f"command executed by {ctx.author}")
            embed = discord.Embed(description=f"Successfully updated the roleicon of {role.name} to {emoji}.", color=0x2f3136)
            await ctx.send(embed=embed)



  #  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(7, 15, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(
        name="steal",
        help="Adds emojis to the server",
        usage="steal <emoji1> <emoji2> ...",
        aliases=["eadd"],
        with_app_command=True
    )
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx, *emojis):
        try:
            added_emojis = []
            failed_emojis = []

            if emojis is None:
                embed = discord.Embed(description="Please enter a valid emote to steal.", color=0x2f3136)
                await ctx.send(embed=embed)
                return
            
            for emote in emojis:
                if not emote.startswith('<'):
                    failed_emojis.append(emote)
                    continue

                name = emote.split(':')[1]
                emoji_name = emote.split(':')[2][:-1]
                anim = emote.split(':')[0]
                
                if anim == '<a':
                    url = f'https://cdn.discordapp.com/emojis/{emoji_name}.gif'
                else:
                    url = f'https://cdn.discordapp.com/emojis/{emoji_name}.png'
                
                try:
                    response = requests.get(url)
                    img = response.content
                    created_emoji = await ctx.guild.create_custom_emoji(name=name, image=img)
                    added_emojis.append(created_emoji)
                except Exception:
                    failed_emojis.append(emote)

            if added_emojis:
                added_emojis_str = ', '.join([str(e) for e in added_emojis])
                await ctx.send(embed=discord.Embed(
                    description=f"Added emojis: {added_emojis_str}",
                    color=0x2f3136
                ))

            if failed_emojis:
                failed_emojis_str = ', '.join(failed_emojis)
                await ctx.send(embed=discord.Embed(
                    title="Failed",
                    description=f"Failed to add emojis: {failed_emojis_str}.\n\nIf you are adding multiple emojis, make sure to give spaces between them.",
                    color=0x2f3136
                ))

        except Exception:
            await ctx.send(embed=discord.Embed(
                title="Error!",
                description="Failed to add emojis. If you are adding multiple emojis, make sure to give spaces between them.",
                color=0x2f3136
            ))
    
    @commands.command(name="stealsticker", help="Create a sticker in your server!", aliases=['makesticker', 'create_sticker', 'make_sticker', 'create-sticker', 'make-sticker', 'stickersteal'])
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.has_permissions(manage_emojis_and_stickers=True)
    @commands.bot_has_permissions(manage_emojis_and_stickers=True)
    async def _sticker(self, ctx: commands.Context, emoji: discord.PartialEmoji = None, *, emoji_flags: Optional[StickerFlags] = None):
        if emoji is not None:
            file = discord.File(BytesIO(await emoji.read()), filename=f"{emoji.name}.png")
        elif ctx.message.reference and ctx.message.reference.cached_message and ctx.message.reference.cached_message.stickers:
            file = await ctx.message.reference.cached_message.stickers[0].to_file()
        elif ctx.message.stickers:
            file = await ctx.message.stickers[0].to_file()
        else:
            referenced_sticker_file = await self.get_sticker_from_reference(ctx)
            if referenced_sticker_file:
                file = referenced_sticker_file
            else:
                ctx.command.reset_cooldown(ctx)
                embed = discord.Embed(description=f"Please mention an emoji, upload a file, or reply to a sticker to make a sticker!", color=0x2f3136)
                return await ctx.reply(embed=embed)

        name = emoji_flags.name if emoji_flags and emoji_flags.name else file.filename.split(".")[0]
        description = emoji_flags.description if emoji_flags and emoji_flags.description else f"Uploaded by {ctx.author}"
        emoji_ = emoji_flags.emoji if emoji_flags and emoji_flags.emoji else name

        try:
            sticker = await ctx.guild.create_sticker(
                name=name,
                description=description,
                emoji=emoji_,
                file=file,
                reason=f"Added by {ctx.author}"
            )

            embed = discord.Embed(
                description=f"Sticker uploaded!",
                color=0x2f3136 
            )
            embed.set_thumbnail(url="attachment://sticker.png")
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

            await ctx.reply(embed=embed, stickers=[sticker], file=file)
        except Exception as e:
            ctx.command.reset_cooldown(ctx)
            embed = discord.Embed(
                description=f"Sticker upload failed. Error: `{e}`\n\nIf this was unexpected, please report it in our support server: {SUPPORT_SERVER_LINK}",
                color=0x2f3136 
            )
            await ctx.reply(embed=embed)



            
                

    @commands.hybrid_command(name="removeemoji",
                             help="Deletes the emoji from the server",
                             usage="removeemoji <emoji>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_emojis=True)
    async def removeemoji(self, ctx, emoji: discord.Emoji):
        await emoji.delete()
        await ctx.send(
            "**<:warn:1199645241729368084> emoji has been deleted.**"
        )

    @commands.hybrid_command(name="unbanall",
                             help="Unbans Everyone In The Guild!",
                             aliases=['massunban'],
                             usage="Unbanall",
                             with_app_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unbanall(self, ctx):
        button = Button(label="Yes",
                        style=discord.ButtonStyle.green,
                        emoji="<:en_tick:1199658108532826252>")
        button1 = Button(label="No",
                         style=discord.ButtonStyle.red,
                         emoji="<:en_cross:1199658158059159654>")

        async def button_callback(interaction: discord.Interaction):
            a = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.ban_members:
                    await interaction.response.edit_message(
                        content="Unbanning All Banned Member(s)",
                        embed=None,
                        view=None)
                    async for idk in interaction.guild.bans(limit=None):
                        await interaction.guild.unban(
                            user=idk.user,
                            reason="Unbanall Command Executed By: {}".format(
                                ctx.author))
                        a += 1
                    await interaction.channel.send(
                        content=f"Successfully Unbanned {a} Member(s)")
                else:
                    await interaction.response.edit_message(
                        content=
                        "I am missing ban members permission.\ntry giving me permissions and retry",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "Hey! This Is Not For You.",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                await interaction.response.edit_message(
                    content="Canceled",
                    embed=None,
                    view=None)
            else:
                await interaction.response.send_message(
                    "This Is Not For You Dummy!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        embed = discord.Embed(
            color=0x2f3136,
            description=
            '**Are you sure you want to unban everyone in this guild?**')

        view = View()
        button.callback = button_callback
        button1.callback = button1_callback
        view.add_item(button)
        view.add_item(button1)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.hybrid_command(name="joinedat",
                      help="Shows when a user joined",
                      usage="joined-at [user]",
                      with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def joined_at(self, ctx, user: discord.Member):
        joined = ctx.author.joined_at.strftime("%a, %d %b %Y %I:%M %p")
        await ctx.send(embed=discord.Embed(title="joined-at",
                                           description="**`%s`**" % (joined),
                                           color=0x2f3136))

    @commands.hybrid_command(name="github", usage="github [search]", description="Shows information about a github repository.")
    @blacklist_check()
    @ignore_check()
    async def github(self, ctx, *, search_query):
        json = requests.get(
            f"https://api.github.com/search/repositories?q={search_query}"
        ).json()

        if json["total_count"] == 0:
            await ctx.send("No matching repositories found")
        else:
            await ctx.send(
                f"First result for '{search_query}':\n{json['items'][0]['html_url']}"
            )

    @commands.hybrid_command(name="vcinfo",
                             help="get info about voice channel",
                             usage="Vcinfo <VoiceChannel>",
                             with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def vcinfo(self, ctx: Context, vc: discord.VoiceChannel):
        e = discord.Embed(title='VC Information', color=0x2f3136)
        e.add_field(name='VC name', value=vc.name, inline=False)
        e.add_field(name='VC ID', value=vc.id, inline=False)
        e.add_field(name='VC bitrate', value=vc.bitrate, inline=False)
        e.add_field(name='Mention', value=vc.mention, inline=False)
        e.add_field(name='Category name', value=vc.category.name, inline=False)
        await ctx.send(embed=e)

    @commands.hybrid_command(name="channelinfo",
                             help="shows info about channel",
                             aliases=['channeli', 'cinfo', 'ci'],
                             pass_context=True,
                             no_pm=True,
                             usage="Channelinfo [channel]",
                             with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def channelinfo(self, ctx, *, channel: Union[discord.TextChannel, discord.VoiceChannel] = None):
        """Shows channel information"""
        if not channel:
            channel = ctx.message.channel
        
        if not channel:
            return await ctx.send(embed=discord.Embed(
                description="<:whitecross:1243852723753844736> | Channel not found or I don't have access to it.",
                color=0x2f3136
            ))

        data = discord.Embed()
        if hasattr(channel, 'mention'):
            data.description = "**Information about Channel:** " + channel.mention
        if hasattr(channel, 'changed_roles'):
            if len(channel.changed_roles) > 0:
                data.color = 0x2f3136 if channel.changed_roles[
                    0].permissions.read_messages else 0x2f3136
        if isinstance(channel, discord.TextChannel):
            _type = "Text"
        elif isinstance(channel, discord.VoiceChannel):
            _type = "Voice"
        else:
            _type = "Unknown"
        data.add_field(name="Type", value=_type)
        data.add_field(name="ID", value=channel.id, inline=False)
        if hasattr(channel, 'position'):
            data.add_field(name="Position", value=channel.position)
        if isinstance(channel, discord.VoiceChannel):
            if channel.user_limit != 0:
                data.add_field(name="User Number",
                               value="{}/{}".format(len(channel.voice_members),
                                                    channel.user_limit))
            else:
                data.add_field(name="User Number",
                               value="{}".format(len(channel.voice_members)))
            userlist = [r.display_name for r in channel.members]
            if not userlist:
                userlist = "None"
            else:
                userlist = "\n".join(userlist)
            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)
        elif isinstance(channel, discord.TextChannel):
            try:
                pins = await channel.pins()
                data.add_field(name="Pins", value=len(pins), inline=True)
            except discord.Forbidden:
                pass
            data.add_field(name="Members", value="%s" % len(channel.members))
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)
            hidden = []
            allowed = []
            for role in channel.changed_roles:
                if role.permissions.read_messages is True:
                    if role.name != "@everyone":
                        allowed.append(role.mention)
                elif role.permissions.read_messages is False:
                    if role.name != "@everyone":
                        hidden.append(role.mention)
            if len(allowed) > 0:
                data.add_field(name='Allowed Roles ({})'.format(len(allowed)),
                               value=', '.join(allowed),
                               inline=False)
            if len(hidden) > 0:
                data.add_field(name='Restricted Roles ({})'.format(
                    len(hidden)),
                               value=', '.join(hidden),
                               inline=False)
        if channel.created_at:
            data.set_footer(text=("Created on {} ({} days ago)".format(
                channel.created_at.strftime("%d %b %Y %H:%M"), (
                    ctx.message.created_at - channel.created_at).days)))
        await ctx.send(embed=data)

    @commands.hybrid_command(name="note",
                      help="Creates a note for you",
                      usage="Note <message>")
    @cooldown(1, 10, BucketType.user)
    @blacklist_check()
    @ignore_check()
    async def note(self, ctx, *, message):
        message = str(message)
        print(message)
        stats = await NoteBook.find_one({"id": ctx.author.id})
        if len(message) <= 50:
            #
            if stats is None:
                newuser = {"id": ctx.author.id, "note": message}
                await NoteBook.insert_one(newuser)
                await ctx.send("**Your note has been stored**")
                await ctx.message.delete()

            else:
                x = NoteBook.find({"id": ctx.author.id})
                z = 0
                async for i in x:
                    z += 1
                if z > 2:
                    await ctx.send("**You cannot add more than 3 notes**")
                else:
                    newuser = {"id": ctx.author.id, "note": message}
                    await NoteBook.insert_one(newuser)
                    await ctx.send("**Yout note has been stored**")
                    await ctx.message.delete()

        else:
            await ctx.send("**Message cannot be greater then 50 characters**")

    @commands.hybrid_command(name="notes", help="Shows your note", usage="Notes")
    @blacklist_check()
    @ignore_check()
    async def notes(self, ctx):
        stats = await NoteBook.find_one({"id": ctx.author.id})
        if stats is None:
            embed = discord.Embed(
                timestamp=ctx.message.created_at,
                title="Notes",
                description=f"{ctx.author.mention} has no notes",
                color=0x2f3136,
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="Notes",
                                  description=f"Here are your notes",
                                  color=0x2f3136)
            x = NoteBook.find({"id": ctx.author.id})
            z = 1
            async for i in x:
                msg = i["note"]
                embed.add_field(name=f"Note {z}", value=f"{msg}", inline=False)
                z += 1
            await ctx.send(embed=embed)
        #  await ctx.send("**Please check your private messages to see your notes**")

    @commands.hybrid_command(name="trashnotes",
                      help="Delete the notes , it's a good practice",
                      usage="Trashnotes",
                      with_app_command=True)
    @blacklist_check()
    @ignore_check()
    async def trashnotes(self, ctx):
        try:
            await NoteBook.delete_many({"id": ctx.author.id})
            await ctx.send("**Your notes have been deleted , thank you**")
        except:
            await ctx.send("**You have no record**")



    @commands.hybrid_command(name="ping",
                             aliases=["latency"],
                             description="Checks the bot latency.",with_app_command = True)
    @ignore_check()
    @blacklist_check()
    async def ping(self, ctx):
        embed = discord.Embed(
            color=0x2f3136)
        
        embed.set_author(name=f"Pong! | {int(self.bot.latency * 1000)}ms", icon_url=f"{ctx.author.avatar.url}")

        await ctx.reply(embed=embed)


    @app_commands.command(name="report", description="Report a bug or issue with the bot.")
    @ignore_check()
    @blacklist_check()
    async def report(self, interaction: discord.Interaction, bug: str) -> None:
        """Report a bug or issue with the bot."""
        channel = self.bot.get_channel(1243614250476376205)
        embed = discord.Embed(
            title='Bug Reported',
            description=bug,
            color=0x2f3136
        )
        embed.add_field(
            name='Reported By', value=f'{interaction.user.name}', inline=True
        )
        embed.add_field(name="Server", value=interaction.guild.name, inline=False)
        embed.add_field(name="Channel", value=interaction.channel.name, inline=False)
        await channel.send(content="@everyone", embed=embed)

        await interaction.response.send_message("Thank you for reporting the bug. We will look into it.", ephemeral=True)

    @commands.hybrid_command(name="badges",
                             help="Check what premium badges a user have.",
                             aliases=["badge", "profile", "pr"],
                             usage="Badges [user]",with_app_command = True)
    @blacklist_check()
    @ignore_check()
    async def _badges(self, ctx, user: Optional[discord.User] = None):
        mem = user or ctx.author
        
        from utils.Tools import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM premium_users WHERE user_id = ?', (mem.id,))
        is_premium = cursor.fetchone() is not None
        
        cursor.execute('SELECT user_id FROM no_prefix_users WHERE user_id = ?', (mem.id,))
        has_no_prefix = cursor.fetchone() is not None
        
        cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (mem.id,))
        is_blacklisted = cursor.fetchone() is not None

        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands_used (
                user_id INTEGER PRIMARY KEY,
                commands_used INTEGER DEFAULT 1
            )
            ''')
            conn.commit()
            

            cursor.execute('SELECT commands_used FROM commands_used WHERE user_id = ?', (mem.id,))
            command_count_result = cursor.fetchone()
            command_count = command_count_result[0] if command_count_result else 0
        except Exception as e:
            print(f"Error getting command count: {e}")
            command_count = 0
        
        bdgs = getbadges(mem.id)
        
        discord_badges = ""
        if mem.public_flags.hypesquad:
            discord_badges += "<:Hypesquad:1199663717730582528> *Hypesquad*\n"
        if mem.public_flags.hypesquad_balance:
            discord_badges += "<:Balance:1199663719945347072> *HypeSquad Balance*\n"
        if mem.public_flags.hypesquad_bravery:
            discord_badges += "<:Bravery:1199663721140719676> *HypeSquad Bravery*\n"
        if mem.public_flags.hypesquad_brilliance:
            discord_badges += "<:Brilliance:1199663723908968560> *Hypesquad Brilliance*\n"
        if mem.public_flags.early_supporter:
            discord_badges += "<:Early:1199663725129519215> *Early Supporter*\n"
        if mem.public_flags.verified_bot_developer:
            discord_badges += "<:VerifiedBotDev:1199663726207451158> *Verified Bot Developer*\n"
        if mem.public_flags.active_developer:
            discord_badges += "<:Discord_ActiveDeveloper:1372935545788829808> *Active Developer*\n"
        if mem.public_flags.staff:
            discord_badges += "<:Staff:1199665548271833138> *Discord Staff*\n"
        if mem.public_flags.partner:
            discord_badges += "<:Partnered:1199665549827920003> *Discord Partner*\n"
        if mem.public_flags.bug_hunter:
            discord_badges += "<:Bugter:1199671285190512713> *Bug Hunter*\n"
        if mem.public_flags.bug_hunter_level_2:
            discord_badges += "<:Bugter:1199671285190512713> *Bug Hunter Level 2*\n"
        
        if discord_badges == "":
            discord_badges = "None"
        
        mutual_guilds = []
        for guild in self.bot.guilds:
            member = guild.get_member(mem.id)
            if member:
                mutual_guilds.append(guild)
        
        embed = discord.Embed(color=0x2f3136)
        
        created_at = int(mem.created_at.timestamp())
        embed.add_field(
            name="__User Information__",
            value=f"**Username:** {mem}\n"
                  f"**ID:** {mem.id}\n"
                  f"**Created:** <t:{created_at}:D> (<t:{created_at}:R>)\n"
                  f"**Mutual Servers:** {len(mutual_guilds)}\n"
                  f"**Commands Used:** {command_count}",
            inline=False
        )
        
        status_list = []
        if is_premium:
            status_list.append("<a:Vip:1199671281092669522> Premium User")
        if has_no_prefix:
            status_list.append("<:whitecheck:1243577701638475787> No Prefix")
        if is_blacklisted:
            status_list.append("<:warn:1199645241729368084> Blacklisted")
        
        # Add bot badges to relationship section
        if bdgs:
            status_list.extend(bdgs)
            
        bot_status = "\n".join(status_list) if status_list else "None"
        
        embed.add_field(
            name="__Bot Relationship__",
            value=bot_status,
            inline=False
        )
        
        embed.add_field(
            name="__Discord Badges__",
            value=discord_badges,
            inline=False
        )
        
        embed.set_author(
            name=f"{mem}'s Profile",
            icon_url=mem.avatar.url if mem.avatar else mem.default_avatar.url
        )
        embed.set_thumbnail(
            url=mem.avatar.url if mem.avatar else mem.default_avatar.url
        )
        
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        embed.timestamp = ctx.message.created_at
        
        conn.close()
        
        await ctx.reply(embed=embed, mention_author=False)