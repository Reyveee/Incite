import discord
from discord import client, user
from discord.ext import commands
from typing import Optional, Union, List
import time
import re
import aiohttp
from os import name
from discord.ext.commands.errors import BotMissingPermissions
import asyncio
import random
import pathlib
from utils.Tools import get_db_connection

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout: Optional[int] = None):
        super().__init__(timeout=timeout)
        self.ctx = ctx
      
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=discord.Embed(description=f"Only **{self.user}** can interact with this one. Use {self.ctx.prefix}**{self.ctx.command}** to run the command.", color=self.ctx.author.color),ephemeral=False)
            return False
        return True

class OnOrOff(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=None)
        self.value = None

    @discord.ui.button(label="Yes", custom_id='Yes', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'Yes'
        self.stop()

    @discord.ui.button(label="No", custom_id='No', style=discord.ButtonStyle.danger)
    async def truth(self, interaction, button):
        self.value = 'No'
        self.stop()
        
class afk(commands.Cog):

    def __init__(self, client, *args, **kwargs):
        self.client = client
        self.initialize_database()

    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS afk (
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            is_afk BOOLEAN DEFAULT 0,
            reason TEXT,
            time INTEGER,
            mentions INTEGER DEFAULT 0,
            dm_enabled BOOLEAN DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
        ''')
        
        conn.commit()
        conn.close()

    async def cog_after_invoke(self, ctx):
        ctx.command.reset_cooldown(ctx)

    async def update_data(self, user, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM afk WHERE user_id = ? AND guild_id = ?', 
                      (user.id, guild_id))
        result = cursor.fetchone()
        
        if not result:
            cursor.execute('''
            INSERT INTO afk (user_id, guild_id, is_afk, reason, mentions, dm_enabled)
            VALUES (?, ?, 0, 'None', 0, 0)
            ''', (user.id, guild_id))
            
        conn.commit()
        conn.close()

    async def time_formatter(self, seconds: float):
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = ((str(days) + " days, ") if days else "") + \
            ((str(hours) + " hours, ") if hours else "") + \
            ((str(minutes) + " minutes, ") if minutes else "") + \
            ((str(seconds) + " seconds, ") if seconds else "")
        return tmp[:-2]

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot or not message.guild:
                return
                
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT is_afk, reason, time, mentions FROM afk WHERE user_id = ? AND guild_id = ?', 
                          (message.author.id, message.guild.id))
            author_afk = cursor.fetchone()
            
            if author_afk and author_afk[0]:
                meth = int(time.time()) - int(author_afk[2])
                been_afk_for = await self.time_formatter(meth)
                mentionz = author_afk[3]
                
                cursor.execute('''
                UPDATE afk SET is_afk = 0, reason = 'None', mentions = 0
                WHERE user_id = ? AND guild_id = ?
                ''', (message.author.id, message.guild.id))
                
                conn.commit()
                
                wlbat = discord.Embed(description=f'{str(message.author.mention)}, I removed your AFK, You were afk for {been_afk_for}, You got {mentionz} while you were afk.', color=0x2f3136)
                ass = await message.channel.send(embed=wlbat)
                await asyncio.sleep(10)
                await ass.delete()
                
                try:
                    if message.author.display_name.startswith("[AFK] "):
                        await message.author.edit(nick=f'{message.author.display_name[5:]}')
                except:
                    pass
            
            if message.mentions:
                for user_mention in message.mentions:
                    if user_mention.id == message.author.id:
                        continue
                        
                    cursor.execute('''
                    SELECT is_afk, reason, time, mentions, dm_enabled 
                    FROM afk 
                    WHERE user_id = ? AND guild_id = ?
                    ''', (user_mention.id, message.guild.id))
                    mention_afk = cursor.fetchone()
                    
                    if mention_afk and mention_afk[0]:
                        reason = mention_afk[1]
                        afk_time = mention_afk[2]
                        mentions = mention_afk[3] + 1
                        dm_enabled = mention_afk[4]
                        
                        cursor.execute('''
                        UPDATE afk SET mentions = ?
                        WHERE user_id = ? AND guild_id = ?
                        ''', (mentions, user_mention.id, message.guild.id))
                        
                        conn.commit()
                        
                        wl = discord.Embed(description=f'**{str(user_mention)}** went AFK <t:{afk_time}:R> : {reason}', color=0x2f3136)
                        ass = await message.channel.send(embed=wl)
                        await asyncio.sleep(10)
                        await ass.delete()
                        
                        if dm_enabled:
                            embed = discord.Embed(description=f'You were Mentioned in **{message.guild.name}** by **{message.author.name}#{message.author.discriminator}**!', color=0x2f3136)
                            embed.add_field(name="Total mentions :", value=mentions, inline=False)
                            embed.add_field(name="Contents:", value=message.content, inline=False)
                            embed.add_field(name="Jump Url:", value=f"[Jump To Message]({message.jump_url})", inline=False)
                            
                            try:
                                await user_mention.send(embed=embed)
                            except:
                                pass
            
            await self.update_data(message.author, message.guild.id)
            
            conn.close()
            
        except Exception as e:
            print(f"Error in AFK on_message: {e}")

    @commands.hybrid_command(description="Shows an AFK status when you're mentioned")
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def afk(self, ctx, *, reason=None):
        if not reason:
            reason = "I am AFK"

        if re.search(r'<@!?(\d+)>', reason):  #user mentions
            emd = discord.Embed(description="<:warn:1199645241729368084> | You can't add user mentions in AFK reason", color=0x2f3136)
            return await ctx.send(embed=emd)

        if re.search(r'<@&(\d+)>', reason):  #role mentions
            emd = discord.Embed(description="<:warn:1199645241729368084> | You can't add role mentions in AFK reason", color=0x2f3136)
            return await ctx.send(embed=emd)

        if re.search(r'(?:https?://)?(?:www\.)?\S+\.\S+', reason):  #links
            emd = discord.Embed(description="<:warn:1199645241729368084> | You can't add links in AFK reason", color=0x2f3136)
            return await ctx.send(embed=emd)

        view = OnOrOff(ctx)
        
        em = discord.Embed(description="Should I DM you on every mention you get, while AFK?", color=0x2f3136)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        
        if not view.value:
            return await test.edit(content="Timed Out!", view=None)
            
        dm_enabled = 1 if view.value == 'Yes' else 0
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO afk (user_id, guild_id, is_afk, reason, time, mentions, dm_enabled)
        VALUES (?, ?, 1, ?, ?, 0, ?)
        ''', (ctx.author.id, ctx.guild.id, reason, int(time.time()), dm_enabled))
        
        conn.commit()
        conn.close()
        
        await test.delete()
        await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention} Your AFK is now set to: {reason}", color=0x2f3136))
        
        try:
            if not ctx.author.display_name.startswith("[AFK] "):
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
        except:
            pass

