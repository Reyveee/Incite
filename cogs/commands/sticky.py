import asyncio
import discord
from discord.ext import commands, tasks
import json
import aiohttp
from utils.Tools import *

class Sticky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()
        self.stickies = self.load_stickies()
        self.update_sticky.start()
        self.max_stickies = 3

    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sticky_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            webhook_url TEXT,
            last_message_id TEXT
        )
        ''')
        
        conn.commit()
        conn.close()

    def load_stickies(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT guild_id, channel_id, content, webhook_url, last_message_id FROM sticky_messages')
        rows = cursor.fetchall()
        
        stickies = {}
        for row in cursor.fetchall():
            guild_id = str(row[0])
            if guild_id not in stickies:
                stickies[guild_id] = {"messages": []}
            
            stickies[guild_id]["messages"].append({
                "channel": str(row[1]),
                "content": row[2],
                "webhook": row[3],
                "last_id": row[4] if row[4] else None
            })
        
        conn.close()
        return stickies

    def save_sticky(self, guild_id, channel_id, content, webhook_url=None, last_message_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO sticky_messages (guild_id, channel_id, content, webhook_url, last_message_id) VALUES (?, ?, ?, ?, ?)',
            (int(guild_id), int(channel_id), content, webhook_url, last_message_id)
        )
        
        conn.commit()
        conn.close()
    
    def update_sticky_message(self, guild_id, channel_id, last_message_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE sticky_messages SET last_message_id = ? WHERE guild_id = ? AND channel_id = ?',
            (last_message_id, int(guild_id), int(channel_id))
        )
        
        conn.commit()
        conn.close()
    
    def update_webhook_url(self, guild_id, channel_id, webhook_url):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE sticky_messages SET webhook_url = ? WHERE guild_id = ? AND channel_id = ?',
            (webhook_url, int(guild_id), int(channel_id))
        )
        
        conn.commit()
        conn.close()
    
    def delete_sticky(self, guild_id, index):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM sticky_messages WHERE guild_id = ? ORDER BY id', (int(guild_id),))
        sticky_ids = cursor.fetchall()
        
        if 1 <= index <= len(sticky_ids):
            sticky_id = sticky_ids[index-1][0]
            cursor.execute('DELETE FROM sticky_messages WHERE id = ?', (sticky_id,))
            
        conn.commit()
        conn.close()
    
    def get_sticky_data(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT channel_id, content, webhook_url, last_message_id FROM sticky_messages WHERE guild_id = ?', 
                      (int(guild_id),))
        rows = cursor.fetchall()
        
        result = {"messages": []}
        for row in rows:
            result["messages"].append({
                "channel": str(row[0]),
                "content": row[1],
                "webhook": row[2],
                "last_id": row[3] if row[3] else None
            })
        
        conn.close()
        return result

    def get_sticky_count(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM sticky_messages WHERE guild_id = ?', (int(guild_id),))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    async def create_webhook(self, channel):
        webhooks = await channel.webhooks()
        webhook = discord.utils.get(webhooks, name='Incite')
        if webhook is None:
            avatar_url = self.bot.user.display_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    avatar_bytes = await resp.read()
            webhook = await channel.create_webhook(name='Incite', avatar=avatar_bytes)
        return webhook.url

    @tasks.loop(minutes=7)
    async def update_sticky(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT guild_id, channel_id, content, webhook_url, last_message_id FROM sticky_messages')
            rows = cursor.fetchall()
            
            conn.close()
            
            for row in rows:
                guild_id, channel_id, content, webhook_url, last_message_id = row
                
                guild = self.bot.get_guild(guild_id)
                if guild is None:
                    continue

                channel = guild.get_channel(channel_id)
                if channel is None:
                    continue

                if not webhook_url:
                    webhook_url = await self.create_webhook(channel)
                    self.update_webhook_url(guild_id, channel_id, webhook_url)

                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    
                    if last_message_id:
                        try:
                            last_message = await channel.fetch_message(int(last_message_id))
                            await last_message.delete()
                        except discord.NotFound:
                            pass

                    new_message = await webhook.send(content, wait=True)
                    self.update_sticky_message(guild_id, channel_id, str(new_message.id))

        except Exception as e:
            print(f"An error occurred in update_sticky: {e}")

    @blacklist_check()
    @ignore_check()
    @commands.hybrid_group(name="sticky")
    async def sticky(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @sticky.command(name="setup", description="Create a sticky message in a channel")
    @blacklist_check()
    @ignore_check()
    async def stickysetup(self, ctx, channel: discord.TextChannel, *, content):
        formatted_content = f"__**STICKY MESSAGE**__\n\n{content}"
        
        guild_id = ctx.guild.id
        
        sticky_count = self.get_sticky_count(guild_id)
        if sticky_count >= self.max_stickies:
            embed = discord.Embed(title="Error!", 
                description=f"<:whitecross:1243852723753844736> Maximum of {self.max_stickies} sticky messages allowed per guild.", 
                color=0x2f3136)
            await ctx.send(embed=embed)
            return

        webhook_url = await self.create_webhook(channel)
        
        self.save_sticky(guild_id, channel.id, formatted_content, webhook_url)

        embed = discord.Embed(
            title="Sticky Message Added",
            description=f"{content} - (#{channel.name})",
            color=0x2f3136
        )
        added = await ctx.send(embed=embed)

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            message = await webhook.send(formatted_content, wait=True)
            self.update_sticky_message(guild_id, channel.id, str(message.id))

        await asyncio.sleep(10)
        await added.delete()

    @sticky.command(name="unsticky", description="Remove a sticky message by its index")
    async def unsticky(self, ctx, index: int = 1):
        guild_id = ctx.guild.id
        sticky_data = self.get_sticky_data(guild_id)
        
        if not sticky_data["messages"]:
            embed = discord.Embed(description="No sticky messages found for this guild.", color=0x2f3136)
            await ctx.send(embed=embed)
            return

        if not 1 <= index <= len(sticky_data["messages"]):
            embed = discord.Embed(description="Invalid sticky message index.", color=0x2f3136)
            await ctx.send(embed=embed)
            return

        removed_sticky = sticky_data["messages"][index - 1]
        
        if removed_sticky.get("last_id"):
            try:
                channel = ctx.guild.get_channel(int(removed_sticky["channel"]))
                if channel:
                    last_message = await channel.fetch_message(int(removed_sticky["last_id"]))
                    await last_message.delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                print(f"Error deleting sticky message: {e}")
        
        self.delete_sticky(guild_id, index)

        embed = discord.Embed(
            description=f"<:whitecheck:1243577701638475787> Sticky message {index} removed.\n\nMessage: **{removed_sticky['content']}**",
            color=0x2f3136
        )
        await ctx.send(embed=embed)

    @sticky.command(name="list", description="List all sticky messages in the server")
    async def sticky_list(self, ctx):
        guild_id = ctx.guild.id
        sticky_data = self.get_sticky_data(guild_id)
        
        if not sticky_data["messages"]:
            embed = discord.Embed(title="Sticky Messages", description="No sticky messages set.", color=0x2f3136)
            await ctx.send(embed=embed)
            return

        description = ""
        for i, sticky in enumerate(sticky_data["messages"], 1):
            channel = ctx.guild.get_channel(int(sticky["channel"]))
            channel_name = channel.name if channel else "deleted-channel"
            description += f"**{i}.** {sticky['content']} - (#{channel_name})\n"

        embed = discord.Embed(title="Sticky Messages", description=description, color=0x2f3136)
        await ctx.send(embed=embed)
