import sys, os
import discord
import sqlite3
from discord.ext import commands
from core import Context
import asyncio
import json

def get_db_connection():
    conn = sqlite3.connect('incite.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS guild_config (
        guild_id INTEGER PRIMARY KEY,
        config TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blacklist (
        user_id INTEGER PRIMARY KEY
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS badges (
        user_id INTEGER PRIMARY KEY,
        badges TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anti (
        guild_id INTEGER PRIMARY KEY,
        status TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ignore (
        guild_id INTEGER,
        channel_id INTEGER,
        PRIMARY KEY (guild_id, channel_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ignore_users (
        guild_id INTEGER,
        user_id INTEGER,
        PRIMARY KEY (guild_id, user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ignore_roles (
        guild_id INTEGER,
        role_id INTEGER,
        PRIMARY KEY (guild_id, role_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        guild_id INTEGER PRIMARY KEY,
        msg_log TEXT,
        member_log TEXT,
        server_log TEXT,
        channel_log TEXT,
        role_log TEXT,
        mod_log TEXT,
        webhooks TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        guild_id INTEGER PRIMARY KEY,
        config TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS premium (
        user_id INTEGER PRIMARY KEY
    )
    ''')
    
    conn.commit()
    conn.close()

initialize_database()

def updateDB(guildID, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data_json = json.dumps(data)
    
    cursor.execute(
        'INSERT OR REPLACE INTO guild_config (guild_id, config) VALUES (?, ?)',
        (guildID, data_json)
    )
    
    conn.commit()
    conn.close()

def getDB(guildID):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT config FROM guild_config WHERE guild_id = ?', (guildID,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return json.loads(result[0])
    else:
        defaultConfig = {
            "welcome": {
                "autodel": 0,
                "channel": [],
                "color": "",
                "embed": False,
                "footer": "",
                "image": "",
                "message": "Welcome to <<server.name>>!",
                "ping": True,
                "title": "",
                "thumbnail": "",
                "footer": ""
            },
            "autorole": {
                "bots": [],
                "humans": []
            },
            "vcrole": {
                "bots": "",
                "humans": ""
            },
            "ticket_panels": []
        }
        updateDB(guildID, defaultConfig)
        return defaultConfig

def getConfig(guildID):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT config FROM guild_config WHERE guild_id = ?', (guildID,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        try:
            config = json.loads(result[0])
            if "antiSpam" in config:
                return config
        except:
            pass
    
    defaultConfig = {
        "antiSpam": False,
        "antiLink": False,
        "antiMentions": False,
        "whitelisted": [],
        "admins": [],
        "adminrole": None,
        "punishment": "none",
        "prefix": ";",
        "staff": None,
        "vip": None,
        "girl": None,
        "guest": None,
        "frnd": None,
        "wlrole": None,
        "reqrole": None,
        "captcha": False, 
        "captchaChannel": False, 
        "logChannel": 1, 
        "temporaryRole": 1, 
        "roleGivenAfterCaptcha": False
    }
    updateConfig(guildID, defaultConfig)
    return defaultConfig

def updateConfig(guildID, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data_json = json.dumps(data)
    
    cursor.execute(
        'INSERT OR REPLACE INTO guild_config (guild_id, config) VALUES (?, ?)',
        (guildID, data_json)
    )
    
    conn.commit()
    conn.close()

def add_user_to_blacklist(user_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (user_id,))
    if cursor.fetchone():
        conn.close()
        return
    
    cursor.execute('INSERT INTO blacklist (user_id) VALUES (?)', (user_id,))
    
    conn.commit()
    conn.close()

def remove_user_from_blacklist(user_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM blacklist WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def blacklist_check():
    def predicate(ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result is None
    
    return commands.check(predicate)

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def getbadges(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT badges FROM badges WHERE user_id = ?', (userid,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return json.loads(result[0])
    else:
        default = []
        makebadges(userid, default)
        return default

def makebadges(userid, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data_json = json.dumps(data)
    
    cursor.execute(
        'INSERT OR REPLACE INTO badges (user_id, badges) VALUES (?, ?)',
        (userid, data_json)
    )
    
    conn.commit()
    conn.close()

def getanti(guildid):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT status FROM anti WHERE guild_id = ?', (guildid,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    else:
        default = "off"
        updateanti(guildid, default)
        return default

def updateanti(guildid, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT OR REPLACE INTO anti (guild_id, status) VALUES (?, ?)',
        (guildid, data)
    )
    
    conn.commit()
    conn.close()

def ignore_check():
    async def predicate(ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT channel_id FROM ignore WHERE guild_id = ? AND channel_id = ?', 
                      (ctx.guild.id, ctx.channel.id))
        channel_ignored = cursor.fetchone() is not None
        
        if channel_ignored:
            cursor.execute('SELECT user_id FROM ignore_users WHERE guild_id = ? AND user_id = ?', 
                          (ctx.guild.id, ctx.author.id))
            user_allowed = cursor.fetchone() is not None
            
            role_allowed = False
            for role in ctx.author.roles:
                cursor.execute('SELECT role_id FROM ignore_roles WHERE guild_id = ? AND role_id = ?', 
                              (ctx.guild.id, role.id))
                if cursor.fetchone():
                    role_allowed = True
                    break
            
            conn.close()
            
            if user_allowed or role_allowed:
                return True
            else:
                msg = await ctx.send("This channel is in the ignore list or you do not have permission to execute commands here.")
                await asyncio.sleep(4)
                await msg.delete()
                return False
        
        conn.close()
        return True
    
    return commands.check(predicate)

def getlogger(guildid):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT msg_log, member_log, server_log, channel_log, role_log, mod_log, webhooks FROM logs WHERE guild_id = ?', 
                  (guildid,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return {
            "msg": result[0],
            "member": result[1],
            "server": result[2],
            "channel": result[3],
            "role": result[4],
            "mod": result[5],
            "webhooks": json.loads(result[6]) if result[6] else {}
        }
    else:
        default = {
            "msg": None,
            "member": None,
            "server": None,
            "channel": None,
            "role": None,
            "mod": None,
            "webhooks": {}
        }
        makelogger(guildid, default)
        return default

async def create_webhook(channel, name="Incite"):
    try:
        webhook = await channel.create_webhook(name=name)
        return webhook.url
    except:
        return None

async def save_webhook(guildid, channel_id, webhook_type):
    data = getlogger(guildid)
    channel = channel_id
    
    if "webhooks" not in data:
        data["webhooks"] = {}
    
    if webhook_type not in data["webhooks"] or not data["webhooks"][webhook_type]:
        channel_obj = channel
        if isinstance(channel, (int, str)):
            from discord.ext.commands import Bot
            bot = Bot.get_instance()
            channel_obj = bot.get_channel(int(channel))
        
        if channel_obj:
            webhook_url = await create_webhook(channel_obj)
            if webhook_url:
                data["webhooks"][webhook_type] = webhook_url
                makelogger(guildid, data)
                return webhook_url
    return data["webhooks"].get(webhook_type)

def makelogger(guildid, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    webhooks_json = json.dumps(data.get("webhooks", {}))
    
    cursor.execute(
        '''INSERT OR REPLACE INTO logs 
           (guild_id, msg_log, member_log, server_log, channel_log, role_log, mod_log, webhooks) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (guildid, data.get("msg"), data.get("member"), data.get("server"), 
         data.get("channel"), data.get("role"), data.get("mod"), webhooks_json)
    )
    
    conn.commit()
    conn.close()

async def send_webhook_message(url, embed):
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url, session=session)
            await webhook.send(embed=embed)
            return True
    except:
        return False

def updateHacker(guildID, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data_json = json.dumps(data)
    
    cursor.execute(
        'INSERT OR REPLACE INTO events (guild_id, config) VALUES (?, ?)',
        (guildID, data_json)
    )
    
    conn.commit()
    conn.close()

def getHacker(guildID):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT config FROM events WHERE guild_id = ?', (guildID,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return json.loads(result[0])
    else:
        defaultConfig = {
            "antinuke": {
                "antirole-delete": True,
                "antirole-create": True,
                "antirole-update": True,
                "antichannel-create": True,
                "antichannel-delete": True,
                "antichannel-update": True,
                "antiban": True,
                "antikick": True,
                "antiwebhook": True,
                "antibot": True,
                "antiserver": True,
                "antiping": True,
                "antiprune": True,
                "antiemoji-delete": True,
                "antiemoji-create": True,
                "antiemoji-update": True,
                "antimemberrole-update": True
            }
        }
        updateHacker(guildID, defaultConfig)
        return defaultConfig

def load_premium():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM premium_users')
    results = cursor.fetchall()
    
    conn.close()
    
    return [row[0] for row in results]

def premium_only():
    def predicate(ctx):
        premium_users = load_premium()
        return ctx.author.id in premium_users
    
    return commands.check(predicate)