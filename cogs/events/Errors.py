import discord
from discord.ext import commands
from core import Astroz, Cog, Context
from utils.Tools import get_db_connection

class Errors(Cog):
  def __init__(self, client:Astroz):
    self.client = client


  @commands.Cog.listener()
  async def on_command_error(self, ctx: Context, error):
    # Check if user is blacklisted or channel is ignored using database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user is blacklisted
    cursor.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (ctx.author.id,))
    user_blacklisted = cursor.fetchone() is not None
    
    # Check if channel is ignored
    channel_ignored = False
    if ctx.guild:
        cursor.execute('SELECT channel_id FROM ignore WHERE guild_id = ? AND channel_id = ?', 
                      (ctx.guild.id, ctx.channel.id))
        channel_ignored = cursor.fetchone() is not None
    
    conn.close()
    
    if isinstance(error, commands.CommandNotFound):
      return
    elif isinstance(error, commands.MissingRequiredArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.CheckFailure):
      # This handles failures from blacklist_check() and ignore_check()
      if user_blacklisted or channel_ignored:
        pass  # The check already handled the response

    elif isinstance(error, commands.NoPrivateMessage):
      hacker = discord.Embed(color=0x2f3136,description=f"You can\'t use the commands in DMs.", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker,delete_after=20)
    elif isinstance(error, commands.TooManyArguments):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
        
            
    elif isinstance(error, commands.CommandOnCooldown):
      hacker = discord.Embed(color=0x2f3136,description=f" <:whitecross:1243852723753844736> | {ctx.author.name} is on cooldown retry after {error.retry_after:.2f} second(s)", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
      #hacker.set_thumbnail(url =f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker,delete_after=10)
    elif isinstance(error, commands.MaxConcurrencyReached):
      hacker = discord.Embed(color=0x2f3136,description=f"<:whitecross:1243852723753844736> | This command is already being executed, let it finish and retry.", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
      #hacker.set_thumbnail(url =f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker,delete_after=10)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.MissingPermissions):
      missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
      if len(missing) > 2:
                fmt = "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
      else:
                fmt = " and ".join(missing)
      hacker = discord.Embed(color=0x2f3136,description=f"<:whitecross:1243852723753844736> | You lack `{fmt}` permission(s) to run `{ctx.command.name}` command!", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
      #hacker.set_thumbnail(url =f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker,delete_after=6)
      ctx.command.reset_cooldown(ctx)

    elif isinstance(error, commands.BadArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.BotMissingPermissions):
      missing = ", ".join(error.missing_perms)
      await ctx.send(f'<:whitecross:1243852723753844736> | I need the **{missing}** to run the **{ctx.command.name}** command!', delete_after=10)
      
    elif isinstance(error, discord.HTTPException):
      pass
    elif isinstance(error, commands.CommandInvokeError):
      pass
      




