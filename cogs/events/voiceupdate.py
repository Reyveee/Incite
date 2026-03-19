import discord
from discord.ext import commands
from core import Astroz, Cog
from discord.utils import *
from discord import *
from utils.Tools import *

from discord.utils import get
from utils.Tools import get_db_connection


class Vcroles2(Cog):
    def __init__(self, bot: Astroz):
        self.bot = bot
        self.initialize_database()

    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vcroles (
            guild_id INTEGER PRIMARY KEY,
            bot_role_id INTEGER,
            human_role_id INTEGER
        )
        ''')
        
        conn.commit()
        conn.close()

    def get_vcroles(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT bot_role_id, human_role_id FROM vcroles WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                "bots": result[0] if result[0] else "",
                "humans": result[1] if result[1] else ""
            }
        else:
            return {
                "bots": "",
                "humans": ""
            }

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        vcrole_data = self.get_vcroles(member.guild.id)
        
        if member.bot:
            if not vcrole_data["bots"]:
                return
            else:
                if not before.channel and after.channel:
                    r = vcrole_data["bots"]
                    br = get(member.guild.roles, id=r)
                    if br:
                        await member.add_roles(br, reason="Incite | VC Roles (Joined VC)")
                elif before.channel and not after.channel:
                    r1 = vcrole_data["bots"]
                    br1 = get(member.guild.roles, id=r1)
                    if br1:
                        await member.remove_roles(br1, reason="Incite | VC Roles (Left VC)")
        elif not member.bot:
            if not vcrole_data["humans"]:
                return
            else:
                if not before.channel and after.channel:
                    r2 = vcrole_data["humans"]
                    br2 = get(member.guild.roles, id=r2)
                    if br2:
                        await member.add_roles(br2, reason="Incite | VC Roles (Joined VC)")
                elif before.channel and not after.channel:
                    r3 = vcrole_data["humans"]
                    br3 = get(member.guild.roles, id=r3)
                    if br3:
                        await member.remove_roles(br3, reason="Incite | VC Roles (Left VC)")