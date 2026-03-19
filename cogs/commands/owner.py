from __future__ import annotations
from discord.ext import commands
from utils.Tools import *
from discord import *
from utils.config import OWNER_IDS
import discord
import typing
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
import datetime
import asyncio
from utils.Tools import get_db_connection

from typing import Optional
def convert_time_to_seconds(time_str):
    time_units = {
        "h": "hour",
        "d": "day",
        "m": "month"
    }
    num = int(time_str[:-1])
    unit = time_units.get(time_str[-1])
    return datetime.timedelta(**{unit: num})
        

class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.initialize_database()
        
    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            user_id INTEGER PRIMARY KEY,
            reason TEXT DEFAULT 'No reason provided'
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS premium_users (
            user_id INTEGER PRIMARY KEY
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS no_prefix_users (
            user_id INTEGER PRIMARY KEY
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            user_id INTEGER PRIMARY KEY,
            badges TEXT DEFAULT '[]'
        )
        ''')
        
        conn.commit()
        conn.close()

    @commands.command(name="bdm", description="DM a USER (Bot Owner Only)")
    @commands.is_owner()
    async def _dm(self, ctx, member: discord.Member, *, message: str):
        try:
            await member.send(message)
            await ctx.reply("Message sent!", delete_after=7)
        except discord.Forbidden:
            await ctx.reply("I can't DM that user!", delete_after=7)

    @commands.command(name="slist")
    @commands.is_owner()
    async def _slist(self, ctx):
        hasanop = ([hasan for hasan in self.client.guilds])
        hasanop = sorted(hasanop,
                         key=lambda hasan: hasan.member_count,
                         reverse=True)
        entries = [
            f"`[{i}]` | [{g.name}](https://discord.com/channels/{g.id}) - {g.member_count}"
            for i, g in enumerate(hasanop, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=f"Server List - {len(self.client.guilds)}",
            color=0x2f3136,
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()



    @commands.command(name="brestart", help="Restarts the client.")
    @commands.is_owner()
    async def _restart(self, ctx: Context):
        await ctx.reply("Restarting!")
        restart_program()

    @commands.command(name="syncdata", help="Syncs all database.")
    @commands.is_owner()
    async def _sync(self, ctx):
        await ctx.reply("Syncing database...", mention_author=False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create guild_settings table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id INTEGER PRIMARY KEY,
            events_enabled INTEGER DEFAULT 1
        )
        ''')
        
        # Sync guild data
        for guild in self.client.guilds:
            # Check if guild exists in database
            cursor.execute('SELECT guild_id FROM guild_settings WHERE guild_id = ?', (guild.id,))
            exists = cursor.fetchone()
            
            # Add guild if it doesn't exist
            if not exists:
                cursor.execute('INSERT INTO guild_settings (guild_id, events_enabled) VALUES (?, 1)', (guild.id,))
        
        # Remove guilds that no longer exist
        cursor.execute('SELECT guild_id FROM guild_settings')
        stored_guilds = cursor.fetchall()
        
        for guild_id in stored_guilds:
            if not self.client.get_guild(guild_id[0]):
                cursor.execute('DELETE FROM guild_settings WHERE guild_id = ?', (guild_id[0],))
        
        conn.commit()
        conn.close()
        
        await ctx.send("<:whitecheck:1243577701638475787> | Database synced successfully!")

    @commands.group(name="blacklist",
                    help="let's you add someone in blacklist",
                    aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM blacklist')
            blacklisted_users = cursor.fetchall()
            conn.close()
            
            entries = [
                f"`[{no}]` | <@!{mem[0]}> (ID: {mem[0]})"
                for no, mem in enumerate(blacklisted_users, start=1)
            ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=
                f"List of Blacklisted users - {len(blacklisted_users)}",
                description="",
                per_page=10,
                color=0x2f3136),
                                  ctx=ctx)
            await paginator.paginate()

    @blacklist.command(name="add")
    @commands.is_owner()
    async def blacklist_add(self, ctx: Context, member: discord.Member):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (member.id,))
            is_blacklisted = cursor.fetchone()
            
            if is_blacklisted:
                conn.close()
                embed = discord.Embed(
                    title="Error!",
                    description=f"{member.name} is already blacklisted",
                    color=discord.Colour(0x2f3136))
                await ctx.reply(embed=embed, mention_author=False)
            else:
                cursor.execute('INSERT INTO blacklist (user_id) VALUES (?)', (member.id,))
                conn.commit()
                
                cursor.execute('SELECT COUNT(*) FROM blacklist')
                count = cursor.fetchone()[0]
                
                conn.close()
                
                embed = discord.Embed(
                    title="Blacklisted",
                    description=f"Successfully Blacklisted {member.name}",
                    color=discord.Colour(0x2f3136))
                embed.set_footer(
                    text=f"There are now {count} users in the blacklist"
                )
                await ctx.reply(embed=embed, mention_author=False)
        except Exception as e:
            embed = discord.Embed(title="Error!",
                                  description=f"An Error Occurred: {e}",
                                  color=discord.Colour(0x2f3136))
            await ctx.reply(embed=embed, mention_author=False)

    @blacklist.command(name="remove")
    @commands.is_owner()
    async def blacklist_remove(self, ctx, member: discord.Member = None):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (member.id,))
            is_blacklisted = cursor.fetchone()
            
            if not is_blacklisted:
                conn.close()
                embed = discord.Embed(
                    title="Error!",
                    description=f"**{member.name}** is not in the blacklist.",
                    color=0x2f3136)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                cursor.execute('DELETE FROM blacklist WHERE user_id = ?', (member.id,))
                conn.commit()
                
                cursor.execute('SELECT COUNT(*) FROM blacklist')
                count = cursor.fetchone()[0]
                
                conn.close()
                
                embed = discord.Embed(
                    title="User removed from blacklist",
                    description=
                    f"<:whitecheck:1243577701638475787> | **{member.name}** has been successfully removed from the blacklist",
                    color=0x2f3136)
                embed.set_footer(
                    text=f"There are now {count} users in the blacklist"
                )
                await ctx.reply(embed=embed, mention_author=False)
        except Exception as e:
            embed = discord.Embed(
                title="Error!",
                description=f"An error occurred: {e}",
                color=0x2f3136)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.group(
    name="premium",
    help="Add user to premium list"
    )
    @commands.is_owner()
    async def _premium(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_premium.command(name="list")
    @commands.is_owner()
    async def premium_list(self, ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM premium_users')
        premium_users = cursor.fetchall()
        conn.close()
        
        premium_list = [user[0] for user in premium_users]
        npl = ([await self.client.fetch_user(nplu) for nplu in premium_list])
        npl = sorted(npl, key=lambda nop: nop.created_at)
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) (ID: {mem.id})"
            for no, mem in enumerate(npl, start=1) ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"Premium List - {len(premium_list)}",
            per_page=10,
            color=0x2f3136),
            ctx=ctx)
        await paginator.paginate()

    @_premium.command(name="add", help="Add user to premium list")
    @commands.is_owner()
    async def premium_add(self, ctx, user: discord.User):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM premium_users WHERE user_id = ?', (user.id,))
        is_premium = cursor.fetchone()
        
        if is_premium:
            conn.close()
            embed = discord.Embed(
                description="**The user you provided is already in the premium list.**",
                color=0x2f3136
            )
            await ctx.reply(embed=embed)
            return
        else:
            cursor.execute('INSERT INTO premium_users (user_id) VALUES (?)', (user.id,))
            conn.commit()
            conn.close()
            
            embed1 = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | Added {user} to the premium list.",
                color=0x2f3136
            )
            await ctx.reply(embed=embed1)

    @_premium.command(name="remove", help="Remove user from premium list")
    @commands.is_owner()
    async def premium_remove(self, ctx, user: discord.User):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM premium_users WHERE user_id = ?', (user.id,))
        is_premium = cursor.fetchone()
        
        if not is_premium:
            conn.close()
            embed = discord.Embed(
                description=f"**{user} is not in the premium list!**",
                color=0x2f3136)
            await ctx.reply(embed=embed)
            return
        else:
            cursor.execute('DELETE FROM premium_users WHERE user_id = ?', (user.id,))
            conn.commit()
            conn.close()
            
            embed2 = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | Removed {user} from the premium list.",
                color=0x2f3136)
            await ctx.reply(embed=embed2)

    @commands.group(
        name="np",
        help="Allows the owners to add someone in no prefix list"
    )
    @commands.is_owner()
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="list")
    @commands.is_owner()
    async def np_list(self, ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM no_prefix_users')
        np_users = cursor.fetchall()
        conn.close()
        
        nplist = [user[0] for user in np_users]
        npl = ([await self.client.fetch_user(nplu) for nplu in nplist])
        npl = sorted(npl, key=lambda nop: nop.created_at)
        entries = [
            f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) (ID: {mem.id})"
            for no, mem in enumerate(npl, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"No Prefix - {len(nplist)}",
            description="",
            per_page=10,
            color=0x2f3136),
                              ctx=ctx)
        await paginator.paginate()

    @_np.command(name="add", help="Add user to no prefix")
    @commands.is_owner()
    async def np_add(self, ctx, user: discord.User):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM no_prefix_users WHERE user_id = ?', (user.id,))
        has_np = cursor.fetchone()
        
        if has_np:
            conn.close()
            embed = discord.Embed(
                description=
                f"**The user is already in no prefix list.**",
                color=0x2f3136)
            await ctx.reply(embed=embed)
            return
        else:
            cursor.execute('INSERT INTO no_prefix_users (user_id) VALUES (?)', (user.id,))
            conn.commit()
            conn.close()
            
            embed1 = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Added no prefix to {user} for all",
                color=0x2f3136)
            await ctx.reply(embed=embed1)

    @_np.command(name="remove", help="Remove user from no prefix")
    @commands.is_owner()
    async def np_remove(self, ctx, user: discord.User):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM no_prefix_users WHERE user_id = ?', (user.id,))
        has_np = cursor.fetchone()
        
        if not has_np:
            conn.close()
            embed = discord.Embed(
                description="**{} is not in no prefix!**".format(user),
                color=0x2f3136)
            await ctx.reply(embed=embed)
            return
        else:
            cursor.execute('DELETE FROM no_prefix_users WHERE user_id = ?', (user.id,))
            conn.commit()
            conn.close()
            
            embed2 = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Removed no prefix from {user} for all",
                color=0x2f3136)
            await ctx.reply(embed=embed2)

    @commands.group(
        name="bdg",
        help="Allows the owners to manage user badges"
    )
    @commands.is_owner()
    async def _badge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            
    @_badge.command(name="add",
                    aliases=["give"],
                    help="Add some badges to a user.")
    @commands.is_owner()
    async def badge_add(self, ctx, member: discord.Member, *, badge: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT badges FROM badges WHERE user_id = ?', (member.id,))
        result = cursor.fetchone()
        
        if result:
            ok = json.loads(result[0])
        else:
            ok = []
        
        if badge.lower() in ["own", "owner", "king"]:
            idk = "*<:Owner:1199671282405486672> Owner*"
            if idk not in ok:
                ok.append(idk)
                cursor.execute('INSERT OR REPLACE INTO badges (user_id, badges) VALUES (?, ?)', 
                             (member.id, json.dumps(ok)))
                conn.commit()
                
                embed2 = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | **Successfully Added `Owner` Badge To {member}**",
                    color=0x2f3136)
                await ctx.reply(embed=embed2)
            else:
                await ctx.reply("This user already has this badge.")
        
        elif badge.lower() in ["staff", "support staff"]:
            idk = "*<:Staff:1199665548271833138> Staff*"
            if idk not in ok:
                ok.append(idk)
                cursor.execute('INSERT OR REPLACE INTO badges (user_id, badges) VALUES (?, ?)', 
                             (member.id, json.dumps(ok)))
                conn.commit()
                
                embed3 = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | **Successfully Added `Staff` Badge To {member}**",
                    color=0x2f3136)
                await ctx.reply(embed=embed3)
            else:
                await ctx.reply("This user already has this badge.")

        elif badge.lower() in ["partner"]:
            idk = "*<:Partnered:1199665549827920003> Partner*"
            if idk not in ok:
                ok.append(idk)
                cursor.execute('INSERT OR REPLACE INTO badges (user_id, badges) VALUES (?, ?)', 
                             (member.id, json.dumps(ok)))
                conn.commit()
                
                embed4 = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | **Successfully Added `Partner` Badge To {member}**",
                    color=0x2f3136)
                await ctx.reply(embed=embed4)
            else:
                await ctx.reply("This user already has this badge.")
        elif badge.lower() in ["sponsor", "contributers", "donator"]:
            idk = "*<a:Sponsors:1199671279796629534> Sponsor*"
            ok.append(idk)
            makebadges(member.id, ok)
            embed5 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Added `Sponsor` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed5)
        elif badge.lower() in [
                "friend", "friends", "homies", "owner's friend"
        ]:
            idk = "*<:Friend:1199671283487608863> Owner`s Friends*"
            ok.append(idk)
            makebadges(member.id, ok)
            embed1 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Added `Owner's Friend` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed1)
        elif badge.lower() in ["early", "supporter", "support"]:
            idk = "*<:Early:1199663725129519215> Early Supporter*"
            ok.append(idk)
            makebadges(member.id, ok)
            embed6 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Added `Early Supporter` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed6)

        elif badge.lower() in ["vip", "premium"]:
            idk = "*<a:Vip:1199671281092669522> Vip*"
            ok.append(idk)
            makebadges(member.id, ok)
            embed7 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Added `VIP` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed7)

        elif badge.lower() in ["bug", "hunter"]:
            idk = "*<:Bugter:1199671285190512713> Bug Hunter*"
            ok.append(idk)
            makebadges(member.id, ok)
            embed8 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Added `Bug Hunter` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed8)
        elif badge.lower() in ["all"]:
            idk = "*<:Owner:1199671282405486672> Owner\n<:Staff:1199665548271833138> Staff\n<:Partnered:1199665549827920003> Partner\n<a:Sponsors:1199671279796629534> Sponsor\n<:Friend:1199671283487608863> Owner`s Friends\n<:Early:1199663725129519215> Early Supporter\n<a:Vip:1199671281092669522> Vip\n<:Bugter:1199671285190512713> Bug Hunter*"
            ok.append(idk)
            makebadges(member.id, ok)
            embedall = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Added `All` Badges To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embedall)
        else:
            hacker = discord.Embed(
                                   description="**Invalid Badge**",
                                   color=0x2f3136)
            
            await ctx.reply(embed=hacker)

            conn.close()

    @_badge.command(name="remove",
                    help="Remove badges from a user.",
                    aliases=["re"])
    @commands.is_owner()
    async def badge_remove(self, ctx, member: discord.Member, *, badge: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT badges FROM badges WHERE user_id = ?', (member.id,))
        result = cursor.fetchone()
        
        if result:
            ok = json.loads(result[0])
        else:
            ok = []
            
        if badge.lower() in ["own", "owner", "king"]:
            idk = "*<:Owner:1199671282405486672> Owner*"
            if idk in ok:
                ok.remove(idk)
                cursor.execute('INSERT OR REPLACE INTO badges (user_id, badges) VALUES (?, ?)', 
                             (member.id, json.dumps(ok)))
                conn.commit()
                
                embed2 = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | **Successfully Removed `Owner` Badge From {member}**",
                    color=0x2f3136)
                await ctx.reply(embed=embed2)
            else:
                await ctx.reply("This user doesn't have this badge.")
        
        elif badge.lower() in ["staff", "support staff"]:
            idk = "*<:Staff:1199665548271833138> Staff*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed3 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Removed `Staff` Badge From {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed3)

        elif badge.lower() in ["partner"]:
            idk = "*<:Partnered:1199665549827920003> Partner*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed4 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Removed `Partner` Badge From {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed4)

        elif badge.lower() in ["sponsor", "donator", "contributers"]:
            idk = "*<a:Sponsors:1199671279796629534> Sponsor*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed5 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Removed `Sponsor` Badge From {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed5)

        elif badge.lower() in [
                "friend", "friends", "homies", "owner's friend"
        ]:
            idk = "*<:friends:993857133852495962> Owner's Friend*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed1 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Removed `Owner's Friend` Badge From {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed1)

        elif badge.lower() in ["early", "supporter", "support"]:
            idk = "*<:Early:1199663725129519215> Early Supporter*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed6 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Removed `Early Supporter` Badge From {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed6)

        elif badge.lower() in ["vip", "premium"]:
            idk = "*<a:Vip:1199671281092669522> Vip*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed7 = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Removed `VIP` Badge From {member}**",
                color=0x2f3136)
           
            await ctx.reply(embed=embed7)

        elif badge.lower() in ["bug", "hunter"]:
            idk = "*<:Bugter:1199671285190512713> Bug Hunter*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed8 = discord.Embed(
                
                description=
                f"**Successfully Removed `Bug Hunter` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed8)
        elif badge.lower() in ["all"]:
            idk = "*<:Owner:1199671282405486672> Owner\n<:Staff:1199665548271833138> Staff\n<:Partnered:1199665549827920003> Partner\n<a:Sponsors:1199671279796629534> Sponsor\n<:Friend:1199671283487608863> Owner`s Friends\n<:Early:1199663725129519215> Early Supporter\n<a:Vip:1199671281092669522> Vip\n<:Bugter:1199671285190512713> Bug Hunter*"
            ok.remove(idk)
            makebadges(member.id, ok)
            embedall = discord.Embed(
                
                description=
                f"<:whitecheck:1243577701638475787> | **Successfully Removed `All` Badges From {member}**",
                color=0x2f3136)
            await ctx.reply(embed=embedall)
        else:
            hacker = discord.Embed(
                                   description="**Invalid Badge**",
                                   color=0x2f3136)
            await ctx.reply(embed=hacker)

            conn.close()





               
        
