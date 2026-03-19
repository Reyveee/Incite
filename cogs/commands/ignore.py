from __future__ import annotations
import discord
from discord.ext import commands, tasks
from core import *
from utils.Tools import *
import asyncio
import json

def add_user_to_ignore(guild_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert user into ignore_users table
    cursor.execute('INSERT OR IGNORE INTO ignore_users (guild_id, user_id) VALUES (?, ?)', 
                  (guild_id, user_id))
    
    conn.commit()
    conn.close()
        
def remove_user_from_ignore(guild_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remove user from ignore_users table
    cursor.execute('DELETE FROM ignore_users WHERE guild_id = ? AND user_id = ?', 
                  (guild_id, user_id))
    
    conn.commit()
    conn.close()

def add_role_to_ignore(guild_id, role_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert role into ignore_roles table
    cursor.execute('INSERT OR IGNORE INTO ignore_roles (guild_id, role_id) VALUES (?, ?)', 
                  (guild_id, role_id))
    
    conn.commit()
    conn.close()

def remove_role_from_ignore(guild_id, role_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remove role from ignore_roles table
    cursor.execute('DELETE FROM ignore_roles WHERE guild_id = ? AND role_id = ?', 
                  (guild_id, role_id))
    
    conn.commit()
    conn.close()

def add_channel_to_ignore(guild_id: int, channel_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert channel into ignore table
    cursor.execute('INSERT OR IGNORE INTO ignore (guild_id, channel_id) VALUES (?, ?)', 
                  (guild_id, channel_id))
    
    conn.commit()
    conn.close()

def remove_channel_from_ignore(guild_id: int, channel_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remove channel from ignore table
    cursor.execute('DELETE FROM ignore WHERE guild_id = ? AND channel_id = ?', 
                  (guild_id, channel_id))
    
    conn.commit()
    conn.close()

def is_channel_ignored(guild_id: int, channel_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if channel is in ignore table
    cursor.execute('SELECT channel_id FROM ignore WHERE guild_id = ? AND channel_id = ?', 
                  (guild_id, channel_id))
    result = cursor.fetchone() is not None
    
    conn.close()
    return result

def get_ignored_channels(guild_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all ignored channels for guild
    cursor.execute('SELECT channel_id FROM ignore WHERE guild_id = ?', (guild_id,))
    channels = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return channels


class Ignore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="ignore", invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def _ignore(self, ctx):
        embed = discord.Embed(title="Ignore Channel Commands", description="<...> Required | [...] Optional", color=0x2f3136)
        embed.add_field(name="Ignore channel", value="None", inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await message.delete()

    @_ignore.group(name="channel",
                   aliases=["ch"],
                   help="Adds a channel to bot's ignore list.",
                   invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @blacklist_check()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _channel(self, ctx):
        embed = discord.Embed(title="Ignore Channel Commands", description="<...> Required | [...] Optional", color=0x2f3136)
        embed.add_field(name="ignore channel add", value="Add channel to command's ignore list", inline=False)
        embed.add_field(name="Ignore channel remove", value="Remove channel from command's ignore list", inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await message.delete()

    @_channel.command(name="add", description="Add a channel into bot's ignore list.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def channel_add(self, ctx: commands.Context, channel: discord.TextChannel):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            if is_channel_ignored(ctx.guild.id, channel.id):
                embed = discord.Embed(
                    title="Error!",
                    description=f"{channel.mention} is already in ignore channel list .",
                    color=0x2f3136)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                add_channel_to_ignore(ctx.guild.id, channel.id)
                embed = discord.Embed(
                    description=f"Now onwards {channel.mention} will be ignored by the bot.",
                    color=0x2f3136)
                await ctx.reply(embed=embed, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description="""```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5)

    @_channel.command(name="remove", description="Removes a channel from the bot's ignore list.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def channel_remove(self, ctx, channel: discord.TextChannel):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            remove_channel_from_ignore(ctx.guild.id, channel.id)
            embed = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | {channel.mention} has been successfully removed from ignore channel list",
                color=0x2f3136)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description="""```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5)

    @commands.hybrid_group(name="bypass", invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @blacklist_check()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _bypass(self, ctx):
        embed = discord.Embed(title="Bypass Commands", description="<...> Required | [...] Optional", color=0x2f3136)
        embed.add_field(name="bypass user add <user>", value="Add user to bypass list", inline=False)
        embed.add_field(name="bypass user remove <user>", value="Remove user from bypass list", inline=False)
        embed.add_field(name="bypass role add <role>", value="Add role to bypass list", inline=False)
        embed.add_field(name="bypass role remove <role>", value="Remove role from bypass list", inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await message.delete()

    @_bypass.group(name="user", invoke_without_command=True)
    @blacklist_check()
    async def _bypass_user(self, ctx):
        embed = discord.Embed(title="Bypass Commands", description="<...> Required | [...] Optional", color=0x2f3136)
        embed.add_field(name="bypass user add <user>", value="Add user to bypass list", inline=False)
        embed.add_field(name="bypass user remove <user>", value="Remove user from bypass list", inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await message.delete()

    @_bypass_user.command(name="add", help="Add a user to bypass bot's ignore channel check.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def bypass_user_add(self, ctx, user: discord.Member):
        # Check if any channels are ignored first
        ignored_channels = get_ignored_channels(ctx.guild.id)
        if not ignored_channels:
            embed = discord.Embed(description=f"No channel is added to the ignore list. Please add a channel first.")
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return
            
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            add_user_to_ignore(ctx.guild.id, user.id)
            embed = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | {user.mention} has been successfully added to the bypass user list",
                color=0x2f3136)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description="""```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5)

    @_bypass_user.command(name="remove", help="Removes a user from bot's ignore channel check bypass.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def bypass_user_remove(self, ctx, user: discord.Member):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            remove_user_from_ignore(ctx.guild.id, user.id)
            embed = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | {user.mention} has been successfully removed from the bypass user list",
                color=0x2f3136)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description="""```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5)

    @_bypass.group(name="role", invoke_without_command=True)
    @blacklist_check()
    async def _bypass_role(self, ctx):
        embed = discord.Embed(title="Bypass Commands", description="<...> Required | [...] Optional", color=0x2f3136)
        embed.add_field(name="bypass role add <user>", value="Add role to bypass list", inline=False)
        embed.add_field(name="bypass role remove <user>", value="Remove role from bypass list", inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await message.delete()

    @_bypass_role.command(name="add", help="Add a role to bypass bot's ignore channel check.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def bypass_role_add(self, ctx, role: discord.Role):
        # Check if any channels are ignored first
        ignored_channels = get_ignored_channels(ctx.guild.id)
        if not ignored_channels:
            embed = discord.Embed(description=f"No channel is added to the ignore list. Please add a channel first.")
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return
            
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            add_role_to_ignore(ctx.guild.id, role.id)
            embed = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | {role.mention} has been successfully added to the bypass role list",
                color=0x2f3136)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description="""```diff\n - You must have Administrator permission.\n - Your top role should be above my top role. \n```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5)

    @_bypass_role.command(name="remove", help="Removes a role from bot's ignore channel check bypass.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def bypass_role_remove(self, ctx, role: discord.Role):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            remove_role_from_ignore(ctx.guild.id, role.id)
            embed = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | {role.mention} has been successfully removed from the bypass role list",
                color=0x2f3136)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            hacker5 = discord.Embed(
                description="""```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5)

