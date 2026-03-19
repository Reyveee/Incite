import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from utils.Tools import *
import json


class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    async def add_role(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.add_roles(role, reason="Incite | Role Added ")

    async def remove_role(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.remove_roles(role, reason="Incite | Role Removed")
 

    @commands.command(name="staff",
                             description="Gives the staff role to the user .",
                             aliases=['official'],
                             help="Gives the staff role to the user .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def _staff(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            lol = data['reqrole']
            own = data['staff']  
            role = context.guild.get_role(own)
            if data["reqrole"] != None:
                req = context.guild.get_role(lol)
                if context.author == context.guild.owner or req in context.author.roles:
                    if data["staff"] != None:
                        if role not in member.roles:
                            await self.add_role(role=own, member=member)
                            
                            hacker = discord.Embed(
                description=
                f"Successfully added <@&{own}> role to {member.mention}.",
                color=0x2f3136)
                            await context.send(embed=hacker)
                        elif role in member.roles:
                            await self.remove_role(role=own, member=member)
                            hacker6 = discord.Embed(
                description=
                f"Successfully removed <@&{own}> role from {member.mention}.",
                color=0x2f3136)
                            hacker6.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker6)                             
                    else:
                        hacker1 = discord.Embed(
                description=
                f"`Staff` role is not setuped in {context.guild.name}.",
                color=0x2f3136)
                        await context.send(embed=hacker1)
                else:
                    hacker3 = discord.Embed(
                description=
                f"You lack {req.mention} role to use this command .",
                color=0x2f3136)
                    hacker3.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                    
                    await context.send(embed=hacker3)

            else:
                hacker4 = discord.Embed(
                description=
                f"Required role for role commands is not setuped in {context.guild.name}.\n\nUse `/setup reqrole` to set it up.",
                color=0x2f3136)
                hacker4.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                
                await context.send(embed=hacker4)  


    @commands.command(name="girl",
                             description="Gives the girl role to the user .",
                             aliases=['cuties', 'qt'],
                             help="Gives the girl role to the user .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def _girl(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            lol = data['reqrole']
            own = data['girl']  
            role = context.guild.get_role(own)
            if data["reqrole"] != None:
                req = context.guild.get_role(lol)
                if context.author == context.guild.owner or req in context.author.roles:
                    if data["girl"] != None:
                        if role not in member.roles:
                            await self.add_role(role=own, member=member)
                            
                            hacker = discord.Embed(
                description=
                f"Successfully added <@&{own}> role to {member.mention}.",
                color=0x2f3136)
                            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker)
                        elif role in member.roles:
                            await self.remove_role(role=own, member=member)
                            hacker6 = discord.Embed(
                description=
                f"Successfully removed <@&{own}> role from {member.mention}.",
                color=0x2f3136)
                            hacker6.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker6)       
                    else:
                        hacker1 = discord.Embed(
                description=
                f"`Girl` role is not setuped in {context.guild.name}.",
                color=0x2f3136)
                        hacker1.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                        hacker1.set_thumbnail(url=f"{context.author.avatar}")
                        await context.send(embed=hacker1)
                else:
                    hacker3 = discord.Embed(
                description=
                f"You lack {req.mention} role to use this command .",
                color=0x2f3136)
                    hacker3.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                    
                    await context.send(embed=hacker3)

            else:
                hacker4 = discord.Embed(
                description=
                f"Required role for role commands is not setuped in {context.guild.name}.\n\nUse `/setup reqrole` to set it up.",
                color=0x2f3136)
                hacker4.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                
                await context.send(embed=hacker4)  
    
    @commands.command(name="vip",
                             description="Gives the vip role to the user .",
                             help="Gives the vip role to the user .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def _vip(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            lol = data['reqrole']
            own = data['vip']  
            role = context.guild.get_role(own)
            if data["reqrole"] != None:
                req = context.guild.get_role(lol)
                if context.author == context.guild.owner or req in context.author.roles:
                    if data["vip"] != None:
                        if role not in member.roles:
                            await self.add_role(role=own, member=member)
                            
                            hacker = discord.Embed(
                description=
                f"Successfully added <@&{own}> role to {member.mention}.",
                color=0x2f3136)
                            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker)
                        elif role in member.roles:
                            await self.remove_role(role=own, member=member)
                            hacker6 = discord.Embed(
                description=
                f"Successfully removed <@&{own}> role from {member.mention}.",
                color=0x2f3136)
                            hacker6.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker6)       
                    else:
                        hacker1 = discord.Embed(
                description=
                f"`Vip` role is not setuped in {context.guild.name}.",
                color=0x2f3136)
                        hacker1.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                        hacker1.set_thumbnail(url=f"{context.author.avatar}")
                        await context.send(embed=hacker1)
                else:
                    hacker3 = discord.Embed(
                description=
                f"You lack {req.mention} role to use this command .",
                color=0x2f3136)
                    hacker3.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                    
                    await context.send(embed=hacker3)

            else:
                hacker4 = discord.Embed(
                description=
                f"Required role for role commands is not setuped in {context.guild.name}.\n\nUse `/setup reqrole` to set it up.",
                color=0x2f3136)
                hacker4.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                
                await context.send(embed=hacker4)


    @commands.command(name="guest",
                             description="Gives the guest role to the user .",
                             help="Gives the guest role to the user .")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def _guest(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            lol = data['reqrole']
            own = data['guest']
            role = context.guild.get_role(own)  
            if data["reqrole"] != None:
                req = context.guild.get_role(lol)
                if context.author == context.guild.owner or req in context.author.roles:
                    if data["guest"] != None:
                        if role not in member.roles:
                            await self.add_role(role=own, member=member)
                            
                            hacker = discord.Embed(
                description=
                f"Successfully added <@&{own}> role to {member.mention}.",
                color=0x2f3136)
                            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker)
                        elif role in member.roles:
                            await self.remove_role(role=own, member=member)
                            hacker6 = discord.Embed(
                description=
                f"Successfully removed <@&{own}> role from {member.mention}.",
                color=0x2f3136)
                            hacker6.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker6)       
                    else:
                        hacker1 = discord.Embed(
                description=
                f"`Guest` role is not setuped in {context.guild.name}.",
                color=0x2f3136)
                        hacker1.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                        hacker1.set_thumbnail(url=f"{context.author.avatar}")
                        await context.send(embed=hacker1)
                else:
                    hacker3 = discord.Embed(
                description=
                f"You lack {req.mention} role to use this command .",
                color=0x2f3136)
                    hacker3.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                    
                    await context.send(embed=hacker3)

            else:
                hacker4 = discord.Embed(
                description=
                f"Required role for role commands is not setuped in {context.guild.name}.\n\nUse `/setup reqrole` to set it up.",
                color=0x2f3136)
                hacker4.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                
                await context.send(embed=hacker4)

    
    @commands.command(name="friend",
                             description="Gives the friend role to the user .",
                             aliases=['frnd'],
                             help="Gives the friend role to the user .")
    @ignore_check()
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def _friend(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            lol = data['reqrole']
            own = data['frnd'] 
            role = context.guild.get_role(own) 
            if data["reqrole"] != None:
                req = context.guild.get_role(lol)
                if context.author == context.guild.owner or req in context.author.roles:
                    if data["frnd"] != None:
                        if role not in member.roles:
                            await self.add_role(role=own, member=member)
                            
                            hacker = discord.Embed(
                description=
                f"Successfully added <@&{own}> role to {member.mention}.",
                color=0x2f3136)
                            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker)
                        elif role in member.roles:
                            await self.remove_role(role=own, member=member)
                            hacker6 = discord.Embed(
                description=
                f"Successfully removed <@&{own}> role from {member.mention}.",
                color=0x2f3136)
                            hacker6.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
                            await context.send(embed=hacker6)       
                    else:
                        hacker1 = discord.Embed(
                description=
                f"`Friend` role is not setuped in {context.guild.name}.",
                color=0x2f3136)
                        hacker1.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                        hacker1.set_thumbnail(url=f"{context.author.avatar}")
                        await context.send(embed=hacker1)
                else:
                    hacker3 = discord.Embed(
                description=
                f"You lack {req.mention} role to use this command .",
                color=0x2f3136)
                    hacker3.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                    
                    await context.send(embed=hacker3)

            else:
                hacker4 = discord.Embed(
                description=
                f"Required role for role commands is not setuped in {context.guild.name}.\n\nUse `/setup reqrole` to set it up.",
                color=0x2f3136)
                hacker4.set_author(name=f"{context.author}",
                               icon_url=f"{context.author.avatar}")
                
                await context.send(embed=hacker4)


    
    @commands.hybrid_group(name="setup",
                           description="Setups custom roles for the server .",
                           help="Setups custom roles for the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def set(self, context: Context):
        if context.subcommand_passed is None:
            await context.send_help(context.command)
            context.command.reset_cooldown(context)

    @set.command(name="staff",
                 description="Setups staff role for the server .",
                 help="Setups staff role for the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def staff(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            if data := getConfig(context.guild.id):

                data['staff'] = role.id
                updateConfig(context.guild.id, data)
                hacker = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | `Staff` role has been set to {role.mention}.",
                    color=0x2f3136)
                hacker.set_author(name=f"{context.author}",
                                  icon_url=f"{context.author.avatar}")
                hacker.set_thumbnail(url=f"{context.author.avatar}")
                await context.send(embed=hacker)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{context.author.name}",
                               icon_url=f"{context.author.avatar}")
            await context.send(embed=hacker5)

    @set.command(name="girl",
                 description="Setups girl role for the server .",
                 help="Setups girl role for the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def girl(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            if data := getConfig(context.guild.id):

                data['girl'] = role.id
                updateConfig(context.guild.id, data)
                hacker = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | `Girl` role has been set to {role.mention}.",
                    color=0x2f3136)
                hacker.set_author(name=f"{context.author}",
                                  icon_url=f"{context.author.avatar}")
                hacker.set_thumbnail(url=f"{context.author.avatar}")
                await context.send(embed=hacker)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{context.author.name}",
                               icon_url=f"{context.author.avatar}")
            await context.send(embed=hacker5)

    @set.command(name="vip",
                 description="Setups vip role for the server .",
                 help="Setups vip role for the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def vip(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            if data := getConfig(context.guild.id):

                data['vip'] = role.id
                updateConfig(context.guild.id, data)
                hacker = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | `Vip` role has been set to {role.mention}.",
                    color=0x2f3136)
                hacker.set_author(name=f"{context.author}",
                                  icon_url=f"{context.author.avatar}")
                hacker.set_thumbnail(url=f"{context.author.avatar}")
                await context.send(embed=hacker)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{context.author.name}",
                               icon_url=f"{context.author.avatar}")
            await context.send(embed=hacker5)

    @set.command(name="guest",
                 description="Setups guest role for the server .",
                 help="Setups guest role for the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def guest(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            if data := getConfig(context.guild.id):

                data['guest'] = role.id
                updateConfig(context.guild.id, data)
                hacker = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | `Guest` role has been set to {role.mention}.",
                    color=0x2f3136)
                hacker.set_author(name=f"{context.author}",
                                  icon_url=f"{context.author.avatar}")
                hacker.set_thumbnail(url=f"{context.author.avatar}")
                await context.send(embed=hacker)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{context.author.name}",
                               icon_url=f"{context.author.avatar}")
            await context.send(embed=hacker5)

    @set.command(name="friend",
                 description="Setups friend role for the server .",
                 help="Setups friend role for the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def friend(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            if data := getConfig(context.guild.id):

                data['frnd'] = role.id
                updateConfig(context.guild.id, data)
                hacker = discord.Embed(
                    description=
                    f"<:whitecheck:1243577701638475787> | `Friend` role has been set to {role.mention}.",
                    color=0x2f3136)
                hacker.set_author(name=f"{context.author}",
                                  icon_url=f"{context.author.avatar}")
                hacker.set_thumbnail(url=f"{context.author.avatar}")
                await context.send(embed=hacker)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{context.author.name}",
                               icon_url=f"{context.author.avatar}")
            await context.send(embed=hacker5)



    @set.command(name="config",
                 description="Shows custom role settings for the server .",
                 aliases=['show'],
                 help="Shows custom role settings for the server .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def rsta(self, context: Context) -> None:
        if data := getConfig(context.guild.id):
            staff = data['staff']
            girl = data['girl']
            vip = data['vip']
            guest = data['guest']
            friends = data['frnd']

            if data["staff"] != None:
                stafff = discord.utils.get(context.guild.roles, id=staff)
                staffr = stafff.mention
            else:
                staffr = "None"
            if data["girl"] != None:
                girll = discord.utils.get(context.guild.roles, id=girl)
                girlr = girll.mention
            else:
                girlr = "None"
            if data["vip"] != None:
                vipp = discord.utils.get(context.guild.roles, id=vip)
                vipr = vipp.mention
            else:
                vipr = "None"
            if data["guest"] != None:
                guestt = discord.utils.get(context.guild.roles, id=guest)
                guestr = guestt.mention
            else:
                guestr = "None"
            if data["frnd"] != None:
                frndr = discord.utils.get(context.guild.roles, id=friends)
                frndr = frndr.mention
            else:
                frndr = "None"



            embed = discord.Embed(
                title=f"Custom roles settings for {context.guild.name}",
                color=0x2f3136)
            embed.add_field(
                name="<:right:1199668086916263956> Staff Role:",
                value=f"{staffr}",
                inline=False)
            embed.add_field(
                name="<:right:1199668086916263956> Girl Role:",
                value=f"{girlr}",
                inline=False)
            embed.add_field(name="<:right:1199668086916263956> Vip Role:",
                            value=f"{vipr}",
                            inline=False)
            embed.add_field(
                name="<:right:1199668086916263956> Guest Role:",
                value=f"{guestr}",
                inline=False)
            embed.add_field(
                name="<:right:1199668086916263956> Friend Role:",
                value=f"{frndr}",
                inline=False)
            #embed.set_thumbnail(url = f"{context.author.avatar}")
            await context.send(embed=embed)



    @set.command(name="reqrole",
                 description="setup reqrole for custom role commands .",
                 aliases=['r'],
                 help="setup reqrole for custom role commands .")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def req_role(self, ctx, role: discord.Role):
        data = getConfig(ctx.guild.id)
        data["reqrole"] = role.id
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            updateConfig(ctx.guild.id, data)
            hacker4 = discord.Embed(
                color=0x2f3136,
                
                description=
                f"<:whitecheck:1243577701638475787> | Reqiured role to run custom role commands has been updated to {role.mention}."
            )
            await ctx.reply(embed=hacker4, mention_author=False)

        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")
            await ctx.reply(embed=hacker5, mention_author=False)


            




    @commands.hybrid_group(name="remove",
                           description="remove roles",
                           aliases=['r'])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def remove(self, context: Context):
        if context.subcommand_passed is None:
            await context.send_help(context.command)
            context.command.reset_cooldown(context)

    @remove.command(name="staff",
                    description="Removes the staff role from the member .",
                    aliases=['official'],
                    help="Removes the staff role from the member .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(member="member to remove staff")
    async def rstaff(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            role = data['staff']
            await self.remove_role(role=role, member=member)
            hacker = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> Successfully removed <@&{role}> role from {member.mention}.",
                color=0x2f3136)
            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
            hacker.set_thumbnail(url=f"{context.author.avatar}")
            await context.send(embed=hacker)

    @remove.command(name="girl",
                    description="Removes the girl role from the member .",
                    aliases=['cuties', 'qt'],
                    hep="Removes the girl role from the member .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(member="member to remove girl")
    async def rgirl(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            role = data['girl']
            await self.remove_role(role=role, member=member)
            hacker = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> Successfully removed <@&{role}> role from {member.mention}.",
                color=0x2f3136)
            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
            hacker.set_thumbnail(url=f"{context.author.avatar}")
            await context.send(embed=hacker)

    @remove.command(name="vip",
                    description="Removes the vip role from the member .",
                    help="Removes the vip role from the member .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(member="member to remove vip")
    async def rvip(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            role = data['vip']
            await self.remove_role(role=role, member=member)
            hacker = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> Successfully removed <@&{role}> role from {member.mention}.",
                color=0x2f3136)
            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
            hacker.set_thumbnail(url=f"{context.author.avatar}")
            await context.send(embed=hacker)

    @remove.command(name="guest",
                    description="Removes the guest role from the member .",
                    help="Removes the guest role from the member .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(member="member to remove guest")
    async def rguest(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            role = data['guest']
            await self.remove_role(role=role, member=member)
            hacker = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> Successfully removed <@&{role}> role from {member.mention}.",
                color=0x2f3136)
            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
            hacker.set_thumbnail(url=f"{context.author.avatar}")
            await context.send(embed=hacker)

    @remove.command(name="friend",
                    description="Removes the friend role from the member .",
                    aliases=['frnd'],
                    help="Removes the friend role from the member .")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(member="member to remove friend")
    async def rfriend(self, context: Context, member: discord.Member) -> None:
        if data := getConfig(context.guild.id):
            role = data['frnd']
            await self.remove_role(role=role, member=member)
            hacker = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> Successfully removed <@&{role}> role from {member.mention}.",
                color=0x2f3136)
            hacker.set_author(name=f"{context.author}",
                              icon_url=f"{context.author.avatar}")
            hacker.set_thumbnail(url=f"{context.author.avatar}")
            await context.send(embed=hacker)



    @commands.hybrid_group(name="autoresponder",
                    invoke_without_command=True,
                    aliases=['ar'])
    @blacklist_check()
    @ignore_check()
    async def _ar(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_ar.command(name="create", description="create an autoresponder")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    @ignore_check()
    async def _create(self, ctx, name, *, message):
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS autoresponses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                response TEXT NOT NULL,
                UNIQUE(guild_id, name)
            )
            ''')
            
            cursor.execute('SELECT COUNT(*) FROM autoresponses WHERE guild_id = ?', (ctx.guild.id,))
            count = cursor.fetchone()[0]
            
            if count >= 15:
                conn.close()
                hacker6 = discord.Embed(
                description=
                f"<:warn:1199645241729368084> You cannot create more than 15 autoresponses.",
                color=0x2f3136)
                hacker6.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.avatar}")
                hacker6.set_thumbnail(url=f"{ctx.author.avatar}")
                return await ctx.send(embed=hacker6)
            
            cursor.execute('SELECT name FROM autoresponses WHERE guild_id = ? AND name = ?', 
                          (ctx.guild.id, name))
            exists = cursor.fetchone()
            
            if exists:
                conn.close()
                hacker = discord.Embed(
                description=
                f"<:warn:1199645241729368084> The autoresponse: `{name}` is already present in {ctx.guild.name}.",
                color=0x2f3136)
                hacker.set_author(name=f"{ctx.author}",
                              icon_url=f"{ctx.author.avatar}")
                hacker.set_thumbnail(url=f"{ctx.author.avatar}")
                return await ctx.send(embed=hacker)
            
            try:
                cursor.execute('INSERT INTO autoresponses (guild_id, name, response) VALUES (?, ?, ?)',
                             (ctx.guild.id, name, message))
                conn.commit()
                conn.close()
                
                hacker1 = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Successfully created autoresponder for `{name}` in {ctx.guild.name}.",
                color=0x2f3136)
                hacker1.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.avatar}")
                hacker1.set_thumbnail(url=f"{ctx.author.avatar}")
                return await ctx.reply(embed=hacker1)
            except Exception as e:
                conn.close()
                print(f"Error creating autoresponder: {e}")
                return await ctx.send("An error occurred while creating the autoresponder.")
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=0x2f3136)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar}")

            await ctx.send(embed=hacker5, mention_author=False)

    @_ar.command(name="delete", description="delete an autoresponder")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    @ignore_check()
    async def _delete(self, ctx, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM autoresponses WHERE guild_id = ? AND name = ?', 
                      (ctx.guild.id, name))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('DELETE FROM autoresponses WHERE guild_id = ? AND name = ?',
                         (ctx.guild.id, name))
            conn.commit()
            conn.close()
            
            hacker1 = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Successfully deleted autoresponder for `{name}` in {ctx.guild.name}.",
                color=0x2f3136)
            hacker1.set_author(name=f"{ctx.author}",
                           icon_url=f"{ctx.author.avatar}")
            hacker1.set_thumbnail(url=f"{ctx.author.avatar}")
            return await ctx.reply(embed=hacker1)
        else:
            conn.close()
            hacker = discord.Embed(
                description=
                f"<:warn:1199645241729368084> No autoresponder found for `{name}` in {ctx.guild.name}.",
                color=0x2f3136)
            hacker.set_author(name=f"{ctx.author}",
                          icon_url=f"{ctx.author.avatar}")
            hacker.set_thumbnail(url=f"{ctx.author.avatar}")
            return await ctx.reply(embed=hacker)

    @_ar.command(name="config", description="shows the autoresponder config")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    @ignore_check()
    async def _config(self, ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM autoresponses WHERE guild_id = ? ORDER BY name', (ctx.guild.id,))
        autoresponses = cursor.fetchall()
        conn.close()
        
        if not autoresponses:
            hacker2 = discord.Embed(
                description=
                f"<:warn:1199645241729368084> There are no autoresponders in {ctx.guild.name}.",
                color=0x2f3136)
            hacker2.set_author(name=f"{ctx.author}",
                           icon_url=f"{ctx.author.avatar}")
            hacker2.set_thumbnail(url=f"{ctx.author.avatar}")
            return await ctx.reply(embed=hacker2)
        
        embed = discord.Embed(color=0x2f3136)
        st, count = "", 1
        
        for ar in autoresponses:
            st += f"`{'0' + str(count) if count < 20 else count}. `    **{ar[0].upper()}**\n"
            count += 1
        
        embed.title = f"{len(autoresponses)} Autoresponders In {ctx.guild.name}"
        embed.description = st
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
        embed.set_thumbnail(url=f"{ctx.author.avatar}")
        await ctx.send(embed=embed)

    @_ar.command(name="edit", description="edit an autoresponder")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def _edit(self, ctx, name, *, message):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM autoresponses WHERE guild_id = ? AND name = ?', 
                      (ctx.guild.id, name))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('UPDATE autoresponses SET response = ? WHERE guild_id = ? AND name = ?',
                         (message, ctx.guild.id, name))
            conn.commit()
            conn.close()
            
            hacker1 = discord.Embed(
                description=
                f"<:whitecheck:1243577701638475787> | Successfully updated the autoresponse message for `{name}` to `{message}` in {ctx.guild.name}.",
                color=0x2f3136)
            hacker1.set_author(name=f"{ctx.author}",
                           icon_url=f"{ctx.author.avatar}")
            hacker1.set_thumbnail(url=f"{ctx.author.avatar}")
            return await ctx.send(embed=hacker1)
        else:
            conn.close()
            hacker2 = discord.Embed(
                description=
                f"<:warn:1199645241729368084> No autoresponder found with the name `{name}` in {ctx.guild.name}",
                color=0x2f3136)
            hacker2.set_author(name=f"{ctx.author}",
                           icon_url=f"{ctx.author.avatar}")
            hacker2.set_thumbnail(url=f"{ctx.author.avatar}")
            return await ctx.send(embed=hacker2)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return
        try:
            if message is not None and message.guild is not None:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT response FROM autoresponses WHERE guild_id = ? AND name = ?', 
                             (message.guild.id, message.content.lower()))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return await message.channel.send(result[0])
        except Exception as e:
            print(f"Error in autoresponder: {e}")
