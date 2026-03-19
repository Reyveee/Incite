import discord
from discord.ext import commands
from core import Cog, Astroz, Context
from utils.Tools import *
from typing import *

class greet(Cog):
    def __init__(self, bot: Astroz):
        self.bot = bot
        
    @Cog.listener()
    async def on_member_join(self, member):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM welcome WHERE guild_id = ?', (member.guild.id,))
            result = cursor.fetchone()
            
            if not result:
                #print(f"No welcome configuration found for guild {member.guild.id}")
                return
            
            msg = result[2]
            chan = json.loads(result[1])
            emtog = bool(result[3])
            emping = bool(result[4])
            emimage = result[5]
            emthumbnail = result[6]
            emfooter1 = result[7]
            emautodel = int(result[8])

            placeholders_msg = {
                "<<server.name>>": member.guild.name,
                "<<server.member_count>>": member.guild.member_count,
                "<<user.name>>": str(member),
                "<<user.mention>>": member.mention,
                "<<user.created_at>>": f"<t:{int(member.created_at.timestamp())}:F>",
                "<<user.joined_at>>": f"<t:{int(member.joined_at.timestamp())}:F>"
            }
            for placeholder, value in placeholders_msg.items():
                msg = msg.replace(placeholder, str(value))
                
            placeholders_footer = {
                "<<server.name>>": member.guild.name,
                "<<server.member_count>>": member.guild.member_count,
                "<<user.name>>": str(member)
            }
            for placeholder, value in placeholders_footer.items():
                emfooter1 = emfooter1.replace(placeholder, str(value))

            em = discord.Embed(description=msg, color=0x2f3136)
            em.set_author(name=member, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
            em.timestamp = discord.utils.utcnow()
            em.set_image(url=emimage)
            em.set_thumbnail(url=emthumbnail)
            em.set_footer(text=emfooter1, icon_url=member.guild.icon.url if member.guild.icon else None)

            for ch_id in chan:
                ch = member.guild.get_channel(int(ch_id))
                if ch:
                    sent_msg = await ch.send(member.mention if emping else None, embed=em)
                    if emautodel:
                        await sent_msg.delete(delay=emautodel)
            
            conn.close()
        except Exception as e:
            print(f"Error in greet: {e}")