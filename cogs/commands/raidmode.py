from discord.ext import commands
from utils.Tools import *
import discord, typing
from core import Cog,Astroz, Context


class Raidmode(Cog):
    """Enable/Disable Anti-raid in your server to be protected from unknown raids!"""

    def __init__(self, client: Astroz):
        self.client = client

    @commands.hybrid_group(
        name="automod",
        aliases=["Automoderation"],
        help="Shows help about Automoderation feature of bot.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _antiraid(self, ctx: commands.Context):
        data = getConfig(ctx.guild.id)
        spam = data["antiSpam"]
        link = data["antiLink"]
        punishment = data["punishment"]
        embed = discord.Embed(title="Automod Commands",
                              color=0x2f3136)
        embed.add_field(
            name="<:right:1199668086916263956> antispam",
            value=f"Toggles antispam feature. Currently Its {spam}",
            inline=False)
        embed.add_field(
            name="<:right:1199668086916263956> antilink",
            value=f"Toggles antilink feature. Currently Its {link}",
            inline=False)
        embed.add_field(
            name="<:right:1199668086916263956> whitelist",
            value=f"Manage whitelisted users: Add, remove, list, or reset.",
            inline=False)
        embed.add_field(
            name="<:right:1199668086916263956> Punishment",
            value=f"Sets suitable punishment for automod rules. Currently Its {punishment}",
            inline=False)
        await ctx.reply(embed=embed, mention_author=False)

    @_antiraid.command(name="antispam",
                             aliases=['anti-spam'],
                             help="Enables or Disables anti spam feature")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _antispam(self, ctx: commands.Context, type: str):

        onOroff = type.lower()

        data = getConfig(ctx.guild.id)
        if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
            if onOroff == "on" or onOroff == "enable":
                if data["antiSpam"] is True:
                    hacker = discord.Embed(
                        description=
                        f"<:alert:1199317330790993960> | Anti-Spam is already enabled for **`{ctx.guild.name}`**",
                        color=0x2f3136)
                    await ctx.reply(embed=hacker, mention_author=False)
                else:
                    data["antiSpam"] = True
                    updateConfig(ctx.guild.id, data)
                    hacker1 = discord.Embed(
        
                        description=
                        f"<:whitecheck:1243577701638475787> | Successfully enabled anti-spam for **`{ctx.guild.name}`**",
                        color=0x2f3136)
                    await ctx.reply(embed=hacker1, mention_author=False)

            elif onOroff == "off" or onOroff == "disable":
                data = getConfig(ctx.guild.id)
                data["antiSpam"] = False
                updateConfig(ctx.guild.id, data)
                hacker2 = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | Successfully disabled anti-spam for **`{ctx.guild.name}`**",
                    color=0x2f3136)
                await ctx.reply(embed=hacker2, mention_author=False)
            else:
                hacker3 = discord.Embed(
                    description=
                    f"<:alert:1199317330790993960> | Invalid Type.\nValid values are: `enable` and `on`.",
                    color=0x2f3136)
                await ctx.reply(embed=hacker3, mention_author=False)

        else:
            hacker5 = discord.Embed(
                color=0x2f3136,
                description=
                f"<:alert:1199317330790993960> | Only owner of the server can run this command"
            )
            await ctx.reply(embed=hacker5, mention_author=False)

    @_antiraid.command(aliases=['anti-link'],
                             name="antilink",
                             help="Enables or Disables antilink feature")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _antilink(self, ctx: commands.Context, type: str):

        onOroff = type.lower()

        data = getConfig(ctx.guild.id)
        if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
            if onOroff == "on" or onOroff == "enable":
                if data["antiLink"] is True:
                    hacker = discord.Embed(
                        description=
                        f"<:alert:1199317330790993960> | Anti-link is already enabled for **`{ctx.guild.name}`**",
                        color=0x2f3136)
                    await ctx.reply(embed=hacker, mention_author=False)
                else:
                    data["antiLink"] = True
                    updateConfig(ctx.guild.id, data)
                    hacker1 = discord.Embed(
                        description=
                        f"<:whitecheck:1243577701638475787> | Successfully enabled anti-link for **`{ctx.guild.name}`**",
                        color=0x2f3136)
                    await ctx.reply(embed=hacker1, mention_author=False)

            elif onOroff == "off" or onOroff == "disable":
                data = getConfig(ctx.guild.id)
                data["antiLink"] = False
                updateConfig(ctx.guild.id, data)
                hacker2 = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | Successfully disabled anti-link for **`{ctx.guild.name}`**",
                    color=0x2f3136)
                await ctx.reply(embed=hacker2, mention_author=False)
            else:
                hacker3 = discord.Embed(
            
                    description=
                    f"<:alert:1199317330790993960> | Invalid Type.\nValid values are: `enable` and `on`.",
                    color=0x2f3136)
                await ctx.reply(embed=hacker3, mention_author=False)

        else:
            hacker5 = discord.Embed(
                color=0x2f3136,
                description=
                f"<:alert:1199317330790993960> | Only owner of the server can run this command"
            )
            await ctx.reply(embed=hacker5, mention_author=False)

    @_antiraid.command(name="whitelist",
                             aliases=['automod whitelist'],
                             help="Manage whitelist for automod events.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _whitelist(self, ctx: Context, action: str, 
                        user: discord.Member = None,
                        role: discord.Role = None,
                        channel: discord.TextChannel = None):
        if action.lower() == "add":
            if not any([user, role, channel]):
                hacker = discord.Embed(
                    description=f"<:alert:1199317330790993960> | Please mention a user, role, or channel to add to the whitelist.",
                    color=0x2f3136)
                await ctx.reply(embed=hacker, mention_author=False)
                return

            data = getConfig(ctx.guild.id)
            
            if user:
                if "whitelisted" not in data:
                    data["whitelisted"] = []
                if str(user.id) in data["whitelisted"]:
                    return await ctx.reply(embed=discord.Embed(description=f"<:alert:1199317330790993960> | {user.mention} is already whitelisted.", color=0x2f3136), mention_author=False)
                data["whitelisted"].append(str(user.id))
                msg = f"{user.mention} user"
                
            elif role:
                if "whitelisted_roles" not in data:
                    data["whitelisted_roles"] = []
                if str(role.id) in data["whitelisted_roles"]:
                    return await ctx.reply(embed=discord.Embed(description=f"<:alert:1199317330790993960> | {role.mention} role is already whitelisted.", color=0x2f3136), mention_author=False)
                data["whitelisted_roles"].append(str(role.id))
                msg = f"{role.mention} role"
                
            elif channel:
                if "whitelisted_channels" not in data:
                    data["whitelisted_channels"] = []
                if str(channel.id) in data["whitelisted_channels"]:
                    return await ctx.reply(embed=discord.Embed(description=f"<:alert:1199317330790993960> | {channel.mention} channel is already whitelisted.", color=0x2f3136), mention_author=False)
                data["whitelisted_channels"].append(str(channel.id))
                msg = f"{channel.mention} channel"

            updateConfig(ctx.guild.id, data)
            await ctx.reply(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Successfully whitelisted {msg}.", color=0x2f3136), mention_author=False)

        elif action.lower() == "remove":
            if not any([user, role, channel]):
                hacker = discord.Embed(
                    description=f"<:alert:1199317330790993960> | Please mention a user, role, or channel to remove from the whitelist.",
                    color=0x2f3136)
                await ctx.reply(embed=hacker, mention_author=False)
                return

            data = getConfig(ctx.guild.id)
            removed = False
            
            if user and str(user.id) in data.get("whitelisted", []):
                data["whitelisted"].remove(str(user.id))
                msg = f"{user.mention} user"
                removed = True
            elif role and str(role.id) in data.get("whitelisted_roles", []):
                data["whitelisted_roles"].remove(str(role.id))
                msg = f"{role.mention} role"
                removed = True
            elif channel and str(channel.id) in data.get("whitelisted_channels", []):
                data["whitelisted_channels"].remove(str(channel.id))
                msg = f"{channel.mention} channel"
                removed = True

            if removed:
                updateConfig(ctx.guild.id, data)
                await ctx.reply(embed=discord.Embed(description=f"<:whitecheck:1243577701638475787> | Successfully removed {msg} from whitelist.", color=0x2f3136), mention_author=False)
            else:
                target = user or role or channel
                await ctx.reply(embed=discord.Embed(description=f"<:alert:1199317330790993960> | {target.mention} is not whitelisted.", color=0x2f3136), mention_author=False)

        elif action.lower() == "reset":
            data = getConfig(ctx.guild.id)
            data["whitelisted"] = []
            data["whitelisted_roles"] = []
            data["whitelisted_channels"] = []
            updateConfig(ctx.guild.id, data)
            await ctx.reply(embed=discord.Embed(description="<:whitecheck:1243577701638475787> | All whitelists have been reset.", color=0x2f3136), mention_author=False)

        elif action.lower() == "show":
            data = getConfig(ctx.guild.id)
            embed = discord.Embed(title="Whitelisted Elements", color=0x2f3136)
            
            users = [f"<@{uid}>" for uid in data.get("whitelisted", [])]
            roles = [f"<@&{rid}>" for rid in data.get("whitelisted_roles", [])]
            channels = [f"<#{cid}>" for cid in data.get("whitelisted_channels", [])]
            
            if users:
                embed.add_field(name="Users", value="\n".join(users) or "None", inline=False)
            if roles:
                embed.add_field(name="Roles", value="\n".join(roles) or "None", inline=False)
            if channels:
                embed.add_field(name="Channels", value="\n".join(channels) or "None", inline=False)
                
            if not (users or roles or channels):
                embed.description = "No whitelisted elements found."
                
            await ctx.reply(embed=embed, mention_author=False)

        else:
            hacker = discord.Embed(
                description=f"<:alert:1199317330790993960> | Invalid action.\nValid actions are: `add`, `remove`, `reset`, `show`.",
                color=0x2f3136)
            await ctx.reply(embed=hacker, mention_author=False)

    
    @_antiraid.command(name="punishment",
                             aliases=['automod punishment'],
                             help="Change or show the punishment for automod events.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _punishment(self, ctx: Context, action: str, punishment: str = None):
        data = getConfig(ctx.guild.id)

        if action.lower() == "set":
            if punishment is None:
                hacker = discord.Embed(
                    description=f"<:alert:1199317330790993960> | Please provide a valid punishment type.",
                    color=0x2f3136)
                await ctx.reply(embed=hacker, mention_author=False)
                return

            punishments = ["none", "kick", "ban"]

            if punishment.lower() not in punishments:
                hacker = discord.Embed(
                    description=f"<:alert:1199317330790993960> | Invalid punishment type.\nValid types are: `none`, `kick`, `ban`.",
                    color=0x2f3136)
                await ctx.reply(embed=hacker, mention_author=False)
                return

            data["punishment"] = punishment.lower()
            updateConfig(ctx.guild.id, data)

            hacker = discord.Embed(
                description=f"<:whitecheck:1243577701638475787> | Successfully changed the punishment type to `{punishment}`.",
                color=0x2f3136)
            await ctx.reply(embed=hacker, mention_author=False)

        elif action.lower() == "show":
            punishment_type = data["punishment"]
            hacker = discord.Embed(
                title="Automod Punishment",
                description=f"The current punishment type for automod events is `{punishment_type}`.",
                color=0x2f3136)
            await ctx.reply(embed=hacker, mention_author=False)

        else:
            hacker = discord.Embed(
                description=f"<:alert:1199317330790993960> | Invalid action.\nValid actions are: `set`, `show`.",
                color=0x2f3136)
            await ctx.reply(embed=hacker, mention_author=False)