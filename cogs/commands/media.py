import discord
from discord.ext import commands
from utils.Tools import get_db_connection

class Media(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.initialize_database()

    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            UNIQUE(guild_id, channel_id)
        )
        ''')
        
        conn.commit()
        conn.close()

    def get_media_channels(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (guild_id,))
        channels = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return channels

    def add_media_channel(self, guild_id, channel_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO media_channels (guild_id, channel_id) VALUES (?, ?)',
                (guild_id, channel_id)
            )
            conn.commit()
            success = True
        except:
            success = False
        
        conn.close()
        return success

    def remove_media_channel(self, guild_id, channel_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM media_channels WHERE guild_id = ? AND channel_id = ?',
            (guild_id, channel_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

    def reset_media_channels(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM media_channels WHERE guild_id = ?', (guild_id,))
        
        conn.commit()
        conn.close()

    @commands.hybrid_group(invoke_without_command = True)
    async def media(self, ctx):
        prefix = ctx.prefix
        em = discord.Embed(
          title=f"Media (4)",
          description=f"`{prefix}media`\nConfigures the media only channels!\n\n`{prefix}media setup`\nSetups media only channels in the server.\n\n`{prefix}media remove`\nRemoves the media only channels in the server.\n\n`{prefix}media config`\nShows the configured media only channels for the server.\n\n`{prefix}media reset`\nRemoves all the channels from media only channels for the server.", color=0x2f3136)
        await ctx.send(embed=em)
          
    @media.command(name="setup", description="Setups media only channels for the server")
    @commands.has_permissions(administrator = True)
    async def setup(self, ctx, *, channel: discord.TextChannel):
        success = self.add_media_channel(ctx.guild.id, channel.id)
        
        if success:
            await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Successfully added {channel.mention} to my media database.", color=0x2f3136))
        else:
            await ctx.send(embed=discord.Embed(description=f"<:whitecross:1243852723753844736> | {channel.mention} is already in the media database.", color=0x2f3136))

    @media.command(name="remove", description="Removes media only channels for the server")
    @commands.has_permissions(administrator = True)
    async def remove(self, ctx, *, channel: discord.TextChannel):
        success = self.remove_media_channel(ctx.guild.id, channel.id)
        
        if success:
            await ctx.send(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Successfully removed {channel.mention} from my media database.", color=0x2f3136))
        else:
            await ctx.send(embed=discord.Embed(description=f"<:whitecross:1243852723753844736> | {channel.mention} is not in the media database.", color=0x2f3136))

    @media.command(name="config", aliases=["settings", "show"], description="Shows the configured media only channels for the server")
    @commands.has_permissions(administrator = True)
    async def config(self, ctx):
        channels = self.get_media_channels(ctx.guild.id)
        
        if not channels:
            await ctx.send(embed=discord.Embed(description="No media channels configured for this server.", color=0x2f3136))
            return
        
        channel_mentions = []
        for channel_id in channels:
            channel = self.client.get_channel(channel_id)
            if channel:
                channel_mentions.append(channel.mention)

        embed = discord.Embed(title = f"Media Only Channels for {ctx.guild.name}", color=0x2f3136)
        
        for i, mention in enumerate(channel_mentions, 1):
            embed.add_field(name = f"{i}", value = mention, inline = False)

        embed.set_footer(text = f"Requested by {ctx.author.name}", icon_url = ctx.author.avatar)

        await ctx.send(embed = embed)

    @media.command(name="reset", description="Removes all the channels from media only channels for the server")
    @commands.has_permissions(administrator = True)
    async def reset(self, ctx):
        self.reset_media_channels(ctx.guild.id)
        
        await ctx.send(embed=discord.Embed(description="<:whitecheck:1243577701638475787> | Successfully cleared media database of this server.", color=0x2f3136))

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return
            
            if message.guild is None:
                return
                
            channels = self.get_media_channels(message.guild.id)
            
            if message.channel.id in channels:
                if not message.attachments:
                    await message.delete()
                    await message.channel.send(f"<:alert:1199317330790993960> This channel is configured for media only. You are only allowed to send media files.", delete_after = 2)
        
        except Exception as e:
            error_logs = self.client.get_channel(1372261842772299807)
            await error_logs.send(e)


        