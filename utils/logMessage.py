import json
import discord
from discord.ext import commands
from utils.Tools import getConfig, updateConfig

async def sendLogMessage(bot, event, channel, embed, messageFile=None):
    """Send the message in the log channel"""
    
    if channel is False:
        return 

    if isinstance(channel, int):
        channel = bot.get_channel(channel) 

    if channel is None:
        try:
            channel = await event.guild.create_text_channel(f"verification-logs") 

            perms = channel.overwrites_for(event.guild.default_role)
            perms.read_messages=False
            await channel.set_permissions(event.guild.default_role, overwrite=perms)

        except Exception as error:
            if hasattr(error, 'code') and error.code == 50013:
                embed = discord.Embed(description=f"Couldn't create a log channel ({error.text})", color=0x2f3136)
                return await event.channel.send(embed=embed)
            return await event.channel.send(str(error))

        data = getConfig(channel.guild.id)
        data["logChannel"] = channel.id

        updateConfig(channel.guild.id, data)

    # Send the message
    await channel.send(embed=embed, file=messageFile)