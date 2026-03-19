import discord
from discord.utils import *
import aiohttp
from core import Astroz, Cog
import json
from utils.Tools import *
from discord.ext import commands
from utils.config import TOKEN


headers = {'Authorization': f'Bot {TOKEN}'}

class Autorole2(Cog):
    def __init__(self, bot: Astroz):
        self.bot = bot



    @Cog.listener()
    async def on_member_join(self, member):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS autorole (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                type TEXT NOT NULL
            )
            ''')
            conn.commit()
            
            cursor.execute('SELECT role_id FROM autorole WHERE guild_id = ? AND type = ?', 
                          (member.guild.id, 'bot'))
            bot_roles = cursor.fetchall()
            
            cursor.execute('SELECT role_id FROM autorole WHERE guild_id = ? AND type = ?', 
                          (member.guild.id, 'human'))
            human_roles = cursor.fetchall()
            
            conn.close()
            
            bot_role_ids = [role[0] for role in bot_roles]
            human_role_ids = [role[0] for role in human_roles]
            
            if member.bot and bot_role_ids:
                async with aiohttp.ClientSession(headers=headers, connector=None) as session:
                    for role_id in bot_role_ids:
                        try:
                            async with session.put(
                                f"https://discord.com/api/v10/guilds/{member.guild.id}/members/{member.id}/roles/{role_id}", 
                                json={'reason': "Incite | Auto Role"}
                            ) as req:
                                print(req.status)
                        except Exception as e:
                            print(f"Error applying bot role: {e}")

            elif not member.bot and human_role_ids:
                async with aiohttp.ClientSession(headers=headers, connector=None) as session:
                    for role_id in human_role_ids:
                        try:
                            async with session.put(
                                f"https://discord.com/api/v10/guilds/{member.guild.id}/members/{member.id}/roles/{role_id}", 
                                json={'reason': "Incite | Auto Role"}
                            ) as req:
                                print(req.status)
                        except Exception as e:
                            print(f"Error applying human role: {e}")
                            
        except Exception as e:
            print(f"Error in autorole: {e}")