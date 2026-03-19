import discord
import asyncio
import json
from discord import app_commands
from discord.ext import commands
from discord.utils import get
from utils.Tools import *
import time

# ------------------------ COGS ------------------------ #  

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

# ------------------------------------------------------ #  
 
    @commands.hybrid_command(name='verification',
                             aliases=["captcha", 'captchaverification'],
                             description="Enable or disable the verification system.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def setup(self, ctx, on_or_off):

        onOrOff = on_or_off.lower()

        if onOrOff == "on":
            start_time = time.time()

            embed = discord.Embed(title="Captcha Setup", description="<:en_tick:1199658108532826252> Initializing Quick Setup!", color=0x2f3136)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            status_message = await ctx.send(embed=embed)

            try:
                data = getConfig(ctx.guild.id)
                embed.description += "\n<:en_tick:1199658108532826252> Checking for permissions..."
                await status_message.edit(embed=embed)
                embed.description += "\n<:en_tick:1199658108532826252> Checking role..."
                await status_message.edit(embed=embed)

                temporaryRole = await ctx.guild.create_role(name="Unverified")
                embed.description += "\n<:en_tick:1199658108532826252> Checking if there's an existing unverified Role..."
                await status_message.edit(embed=embed)

                embed.description += "\n<:en_tick:1199658108532826252> Setting up unverified role across all channels..."
                await status_message.edit(embed=embed)

                for channel in ctx.guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        perms = channel.overwrites_for(temporaryRole)
                        perms.read_messages = False
                        await channel.set_permissions(temporaryRole, overwrite=perms)

                    elif isinstance(channel, discord.VoiceChannel):
                        perms = channel.overwrites_for(temporaryRole)
                        perms.read_messages = False
                        perms.connect = False
                        await channel.set_permissions(temporaryRole, overwrite=perms)

                embed.description += "\n<:en_tick:1199658108532826252> Ensuring unverified role is placed properly..."
                await status_message.edit(embed=embed)

                embed.description += "\n<:en_tick:1199658108532826252> Checking if there's an existing Captcha channel..."
                await status_message.edit(embed=embed)

                captchaChannel = await ctx.guild.create_text_channel('verification')
                perms = captchaChannel.overwrites_for(temporaryRole)
                perms.read_messages = True
                perms.send_messages = False
                await captchaChannel.set_permissions(temporaryRole, overwrite=perms)

                perms = captchaChannel.overwrites_for(ctx.guild.default_role)
                perms.read_messages = False
                await captchaChannel.set_permissions(ctx.guild.default_role, overwrite=perms)

                embed.description += "\n<:en_tick:1199658108532826252> Checking if there's an existing Logging Channel..."
                await status_message.edit(embed=embed)

                if data["logChannel"] is False:
                    logChannel = await ctx.guild.create_text_channel(f"verification-logs")
                    perms = logChannel.overwrites_for(ctx.guild.default_role)
                    perms.read_messages = False
                    await logChannel.set_permissions(ctx.guild.default_role, overwrite=perms)

                    data["logChannel"] = logChannel.id

                embed.description += "\n<:en_tick:1199658108532826252> Saving changes..."
                await status_message.edit(embed=embed)

                data["captcha"] = True
                data["temporaryRole"] = temporaryRole.id
                data["captchaChannel"] = captchaChannel.id

                updateConfig(ctx.guild.id, data)

                end_time = time.time()
                elapsed_time = end_time - start_time  #Calculate

                embed.description += f"\n<:en_tick:1199658108532826252> Setup Finished!\nThe setup finished successfully in `{elapsed_time:.2f}s`."
                await status_message.edit(embed=embed)

            except Exception as error:
                embed = discord.Embed(description=f"An error occurred: {error}", color=0xe00000)  # Red
                embed.set_author(name="Error!", icon_url=ctx.author.display_avatar)
                await ctx.send(embed=embed)

        elif onOrOff == "off":
            start_time = time.time()

            embed = discord.Embed(title="Captcha Setup", description="<:en_tick:1199658108532826252> Initializing Quick Teardown!", color=0x2f3136)
            embed.set_author(name="Processing...", icon_url=ctx.author.display_avatar)
            status_message = await ctx.send(embed=embed)

            data = getConfig(ctx.guild.id)
            data["captcha"] = False

            noDeleted = []
            try:
                temporaryRole = get(ctx.guild.roles, id=data["temporaryRole"])
                await temporaryRole.delete()
                embed.description += "\n<:en_tick:1199658108532826252> Deleted temporary role."
            except:
                noDeleted.append("temporaryRole")
                embed.description += "\n<:en_cross:1199658158059159654> Failed to delete temporary role."
            await status_message.edit(embed=embed)

            try:  
                captchaChannel = self.bot.get_channel(data["captchaChannel"])
                await captchaChannel.delete()
                embed.description += "\n<:en_tick:1199658108532826252> Deleted captcha channel."
            except:
                noDeleted.append("captchaChannel")
                embed.description += "\n<:en_cross:1199658158059159654> Failed to delete captcha channel."
            await status_message.edit(embed=embed)

            data["captchaChannel"] = False
            
            updateConfig(ctx.guild.id, data)
            
            end_time = time.time()
            elapsed_time = end_time - start_time

            embed.description += f"\n<:en_tick:1199658108532826252> Teardown Finished!\nThe teardown finished successfully in `{elapsed_time:.2f}s`."
            await status_message.edit(embed=embed)

            if len(noDeleted) > 0:
                errors = ", ".join(noDeleted)
                embed = discord.Embed(description=f"An error occurred while removing verification system\n\n{errors}", color=0xe00000)  # Red
                embed.set_author(name="Error!", icon_url=ctx.author.display_avatar)
                #await ctx.send(embed=embed)

        else:
            prefix = "/"
            embed = discord.Embed(description= f"The setup argument must be on or off\nFollow the example: `{prefix}setup <on/off>`", color=0x000000) # Red
            embed.set_author(name="Error!", icon_url=ctx.author.display_avatar)
            
            return await ctx.send(embed=embed)
            pass

# ------------------------ BOT ------------------------ #  

async def setup(bot):
      await bot.add_cog(SetupCog(bot=bot))