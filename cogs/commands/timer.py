import time
import discord
from discord.ext import commands
import asyncio
from utils.Tools import *
from datetime import datetime, timedelta
import sqlite3
import re

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_timers = {}
        self.initialize_database()
        self.load_timers()
        
    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS timers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            message_id INTEGER,
            author_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            end_time INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_timers(self):
        """Load active timers from database on startup"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, guild_id, channel_id, message_id, author_id, title, end_time FROM timers WHERE end_time > ?', 
                      (int(datetime.utcnow().timestamp()),))
        
        timers = cursor.fetchall()
        conn.close()
        
        for timer in timers:
            timer_id, guild_id, channel_id, message_id, author_id, title, end_time = timer
            self.bot.loop.create_task(self.resume_timer(timer_id, guild_id, channel_id, message_id, author_id, title, end_time))
    
    async def resume_timer(self, timer_id, guild_id, channel_id, message_id, author_id, title, end_time):
        """Resume a timer that was active before restart"""
        now = int(time.time())  # Use time.time() instead of datetime
        remaining = end_time - now
        
        if remaining <= 0:
            # Timer already expired, clean up
            self.delete_timer(timer_id)
            return
            
        # Schedule the timer to complete
        await asyncio.sleep(remaining)
        
        # Get the channel and try to send completion message
        try:
            channel = self.bot.get_channel(channel_id)
            if channel:
                # Try to get the original message to check reactions
                try:
                    message = await channel.fetch_message(message_id)
                    reactants = []
                    for reaction in message.reactions:
                        if reaction.emoji == "⏱️":
                            users = [user async for user in reaction.users() if user.id != self.bot.user.id]
                            reactants.extend(users)
                    
                    # Create completion embed
                    embed = discord.Embed(
                        title=f"⏱️ Timer Complete: {title}",
                        description=f"The timer has ended!",
                        color=0x2f3136
                    )
                    embed.add_field(name="Started by", value=f"<@{author_id}>", inline=True)
                    embed.add_field(name="Ended at", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=True)
                    embed.set_footer(text=f"Timer ID: {timer_id}")
                    
                    # Mention reactants if any
                    if reactants:
                        mentions = " ".join([user.mention for user in reactants])
                        await channel.send(content=f"⏱️ **Timer Complete!** {mentions}", embed=embed)
                    else:
                        await channel.send(content=f"⏱️ **Timer Complete!** <@{author_id}>", embed=embed)
                        
                except discord.NotFound:
                    # Original message was deleted, just send a new completion message
                    embed = discord.Embed(
                        title=f"⏱️ Timer Complete: {title}",
                        description=f"The timer has ended!",
                        color=0x2f3136
                    )
                    embed.add_field(name="Started by", value=f"<@{author_id}>", inline=True)
                    embed.set_footer(text=f"Timer ID: {timer_id}")
                    await channel.send(content=f"⏱️ **Timer Complete!** <@{author_id}>", embed=embed)
        except Exception as e:
            print(f"Error completing timer: {e}")
        
        # Clean up the timer from database
        self.delete_timer(timer_id)
    
    def save_timer(self, guild_id, channel_id, message_id, author_id, title, end_time):
        """Save a timer to the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO timers (guild_id, channel_id, message_id, author_id, title, end_time, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (guild_id, channel_id, message_id, author_id, title, end_time, int(datetime.utcnow().timestamp()))
        )
        
        timer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return timer_id
    
    def delete_timer(self, timer_id):
        """Delete a timer from the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM timers WHERE id = ?', (timer_id,))
        
        conn.commit()
        conn.close()

    def parse_time(self, time_str):
        """Parse time string into seconds"""
        # Check if it's just a number (seconds)
        if time_str.isdigit():
            return int(time_str)
        
        # Parse time with unit (e.g., 1h, 30m, 45s)
        time_units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        # Use regex to match number + unit format
        match = re.match(r'(\d+)([smhd])', time_str.lower())
        if match:
            value, unit = match.groups()
            return int(value) * time_units[unit]
            
        raise ValueError("Invalid time format")

    @commands.hybrid_group(name="timer", aliases=['tstart'], description="Start a countdown timer")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _timer(self, ctx, time_input, *, title: str = None):
        if title is None:
            title = 'Timer'
            
        try:
            seconds = self.parse_time(time_input)
            
            if seconds > 86400:
                return await ctx.send("⚠️ Timers cannot exceed 24 hours (1 day).", ephemeral=True)
            if seconds <= 0:
                return await ctx.send("⚠️ Timer duration must be positive.", ephemeral=True)
                
            # Use single timestamp calculation method
            now = int(time.time())  # Current Unix timestamp
            end_timestamp = now + seconds
            
            if end_timestamp <= now:
                return await ctx.send("⚠️ An error has occurred!", ephemeral=True)
            
            embed = discord.Embed(
                title=f"⏱️ {title}",
                description=f"Timer will end <t:{end_timestamp}:R> (<t:{end_timestamp}:F>)",
                color=0x2f3136
            )
            
            if seconds >= 3600:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds_left = seconds % 60
                time_str = f"{hours}h {minutes}m {seconds_left}s"
            elif seconds >= 60:
                minutes = seconds // 60
                seconds_left = seconds % 60
                time_str = f"{minutes}m {seconds_left}s"
            else:
                time_str = f"{seconds}s"
                
            embed.add_field(name="Duration", value=time_str, inline=True)
            embed.add_field(name="Started by", value=ctx.author.mention, inline=True)
            embed.set_footer(text="React with ⏱️ to be notified when the timer ends")
            
            message = await ctx.send(embed=embed)
            await message.add_reaction("⏱️")
            
            timer_id = self.save_timer(
                ctx.guild.id, 
                ctx.channel.id, 
                message.id, 
                ctx.author.id, 
                title, 
                end_timestamp
            )
            
            self.bot.loop.create_task(
                self.resume_timer(
                    timer_id, 
                    ctx.guild.id, 
                    ctx.channel.id, 
                    message.id,
                    ctx.author.id, 
                    title, 
                    end_timestamp
                )
            )
            
        except ValueError:
            await ctx.send("⚠️ Invalid time format. Examples: `30s`, `5m`, `2h`, `1d`", ephemeral=True)
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {str(e)}", ephemeral=True)
            
    @_timer.command(name="list", description="List all active timers in this server")
    @blacklist_check()
    @ignore_check()
    async def list_timers(self, ctx):
        """List all active timers in the current server"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, channel_id, author_id, title, end_time FROM timers WHERE guild_id = ? AND end_time > ? ORDER BY end_time',
            (ctx.guild.id, int(datetime.utcnow().timestamp()))
        )
        
        timers = cursor.fetchall()
        conn.close()
        
        if not timers:
            return await ctx.send("No active timers in this server.", ephemeral=True)
            
        embed = discord.Embed(
            title="⏱️ Active Timers",
            description=f"There are {len(timers)} active timers in this server.",
            color=0x2f3136
        )
        
        for i, timer in enumerate(timers, 1):
            timer_id, channel_id, author_id, title, end_time = timer
            
            embed.add_field(
                name=f"{i}. {title}",
                value=f"Ends <t:{end_time}:R> (<t:{end_time}:F>)\n"
                      f"Channel: <#{channel_id}>\n"
                      f"Started by: <@{author_id}>",
                inline=False
            )
            
        await ctx.send(embed=embed)
        
    @_timer.command(name="canceltimer", description="Cancel an active timer")
    @blacklist_check()
    @ignore_check()
    async def cancel_timer(self, ctx, timer_id: int):
        """Cancel an active timer by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT author_id, title FROM timers WHERE id = ? AND guild_id = ?', 
                      (timer_id, ctx.guild.id))
        
        timer = cursor.fetchone()
        conn.close()
        
        if not timer:
            return await ctx.send("⚠️ Timer not found or already completed.", ephemeral=True)
            
        author_id, title = timer
        
        # Only allow the timer creator or users with manage messages permission to cancel
        if author_id != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send("⚠️ You can only cancel timers that you created.", ephemeral=True)
            
        # Delete the timer
        self.delete_timer(timer_id)
        
        embed = discord.Embed(
            title="⏱️ Timer Cancelled",
            description=f"The timer **{title}** has been cancelled.",
            color=0x2f3136
        )
        
        await ctx.send(embed=embed)