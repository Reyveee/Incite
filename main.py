import os
from typing import Literal, Optional
import requests
from core.Astroz import Astroz
import asyncio, json
import jishaku, cogs
from discord.ext import commands, tasks
import discord
from datetime import datetime
from discord import app_commands
import traceback
from discord.ext.commands import Context
from discord import Spotify
import aiohttp
import base64
import time
import json
from io import BytesIO
from utils.Tools import *
from utils.config import TOKEN

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.system('cls')

client = Astroz()
tree = client.tree

#T2 = ""
@commands.cooldown(1, 2, commands.BucketType.user)
@commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
@commands.guild_only()
@client.command()
@premium_only()
async def generate(ctx: commands.Context, *, prompt: str):
    ETA = int(time.time() + 60)
    await ctx.send(f"**Processing your prompt, this may take some time... ETA: <t:{ETA}:R>**")

    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "stabilityai/stable-diffusion-xl", 
            "prompt": prompt
        }

        headers = {
            "Authorization": "Bearer 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", 
            "Content-Type": "application/json"
        }

        async with session.post("https://openrouter.ai/api/v1/generate-image", 
                                json=payload, headers=headers) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return await ctx.reply(f"❌ API Error: {resp.status}\n```{error_text}```")

            response = await resp.json()
            image_url = response["image_url"] 

        async with session.get(image_url) as img_resp:
            if img_resp.status != 200:
                return await ctx.reply("❌ Failed to fetch the generated image.")
            image_data = BytesIO(await img_resp.read())

        await ctx.reply(content="Here's your generated image by\n- **OpenRouter**",
                        file=discord.File(image_data, "generated.png"))


@generate.error
async def generate_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
       embed = discord.Embed(
             description="This command is for premium users only. Click [here](https://discord.gg/encoders-community-1058660812182519921) to subscribe to premium.",
             color=0x2f3136
           )
       button1 = discord.ui.Button(label="Premium",
                               style=discord.ButtonStyle.url,
                               url="https://discord.gg/encoders-community-1058660812182519921")
       view = discord.ui.View()
       view.add_item(button1)
       await ctx.send(embed=embed, view=view)


@commands.cooldown(1, 2, commands.BucketType.user)
@commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
@commands.guild_only()
@blacklist_check()
@ignore_check()
@client.hybrid_command(name="gpt", description="Interact with AI model.")
#@premium_only()
async def gpt(ctx: commands.Context, *, prompt: str):
    async with ctx.typing():  
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "anthropic/claude-3.5-haiku:beta",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            headers = {
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            }

            async with session.post("https://openrouter.ai/api/v1/chat/completions",
                                    json=payload,
                                    headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    await ctx.reply(f"❌ API Error: {resp.status}\n```{error_text}```")
                    return

                response = await resp.json()
                respo = response["choices"][0]["message"]["content"]

                hacker5 = discord.Embed(description=f"```\n{respo}\n```",
                                        color=0x2f3136)
                hacker5.set_author(name="Claude 3.5",
                                   icon_url=ctx.author.avatar.url if ctx.author.avatar
                                   else ctx.author.default_avatar.url)
                hacker5.timestamp = discord.utils.utcnow()
                hacker5.set_footer(text=f"Requested By {ctx.author}",
                                   icon_url=ctx.author.avatar.url if ctx.author.avatar
                                   else ctx.author.default_avatar.url)
                await ctx.reply(embed=hacker5)


@commands.cooldown(1, 2, commands.BucketType.user)
@commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
@commands.guild_only()
@blacklist_check()
@ignore_check()
@client.command(name='vanity')
async def vanity(ctx, *, vanity_code: str):
  vanity_code = vanity_code.replace("https://discord.gg/", "").replace("discord.gg/", "")

  vanity_url = f"https://discord.com/api/v9/invites/{vanity_code}"
  response = requests.get(vanity_url)

  embed = discord.Embed(title="Vanity URL",
                        description=f"`https://discord.gg/{vanity_code}`",
                        color=0x2f3136)
  embed.timestamp = datetime.utcnow()

  if response.status_code == 200:
    guild_info = response.json()  
    guild_name = guild_info['guild']['name']
    guild_id = guild_info['guild']['id']
    guild_description = guild_info['guild']['description'] if 'description' in guild_info['guild'] else "No description available"
    guild_icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{guild_info['guild']['icon']}.png"
    guild_banner_url = f"https://cdn.discordapp.com/banners/{guild_id}/{guild_info['guild']['banner']}.png"

    embed.set_thumbnail(url=guild_icon_url)  
    embed.add_field(name="Server Name", value=guild_name, inline=False)
    embed.add_field(name="Server ID", value=guild_id, inline=False)
    embed.add_field(name="Server Description", value=guild_description, inline=False)
    embed.add_field(name="Availability", value="<:cross:1199413326065705000> Not Availabile", inline=False)
  else:
    embed.add_field(name="Availability", value=":white_check_mark: Availabile", inline=False)
  await ctx.send(embed=embed)

@gpt.error
async def gpt_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
       embed = discord.Embed(
             description="This command is for premium users only. Click [here](https://discord.gg/encoders-community-1058660812182519921) to subscribe to premium.",
             color=0x2f3136
           )
       button1 = discord.ui.Button(label="Premium",
                               style=discord.ButtonStyle.url,
                               url="https://discord.gg/encoders-community-1058660812182519921")
       view = discord.ui.View()
       view.add_item(button1)
       await ctx.send(embed=embed, view=view)


class Hacker(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title='Embed Configuration')
        
        self.content = discord.ui.TextInput(
            label='Message Content',
            placeholder='Optional message content (e.g., @here)',
            required=False,
        )
        self.tit = discord.ui.TextInput(
            label='Embed Title',
            placeholder='Embed title here',
            required=False,
        )
        self.description = discord.ui.TextInput(
            label='Embed Description',
            style=discord.TextStyle.long,
            placeholder='Embed description optional',
            max_length=4000,
        )
        self.thumbnail = discord.ui.TextInput(
            label='Thumbnail URL',
            placeholder='Thumbnail URL (optional) | Image URL (optional)',
            required=False,
        )
        self.footer = discord.ui.TextInput(
            label='Footer Text',
            placeholder='Footer text (optional)',
            required=False,
        )
        
        self.add_item(self.content)
        self.add_item(self.tit)
        self.add_item(self.description)
        self.add_item(self.thumbnail)
        self.add_item(self.footer)

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
            return
            
        embed = discord.Embed(title=self.tit.value,
                            description=self.description.value,
                            color=0x2f3136)
        if self.thumbnail.value:
            if '|' in self.thumbnail.value:
                thumbnail_url, image_url = map(str.strip, self.thumbnail.value.split('|'))
                if thumbnail_url:
                    embed.set_thumbnail(url=thumbnail_url)
                if image_url:
                    embed.set_image(url=image_url)
            else:
                embed.set_thumbnail(url=self.thumbnail.value)
                
        if self.footer.value:
            embed.set_footer(text=self.footer.value)
            
        await interaction.response.send_message("Message sent!", ephemeral=True)
        await interaction.channel.send(
            content=self.content.value if self.content.value else None,
            embed=embed
        )

    async def on_error(self, interaction: discord.Interaction,  
                      error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.',
                                              ephemeral=True)
        traceback.print_tb(error.__traceback__)


# @commands.has_permissions(administrator=True)
@tree.command(name="embed", description="Create a customizable embed.")
@blacklist_check()
@ignore_check()
@app_commands.default_permissions(manage_messages=True) 
async def _embed(interaction: discord.Interaction) -> None:
    await interaction.response.send_modal(Hacker())



################################################

@client.command()
@commands.guild_only()
@commands.is_owner()
async def syncslash(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


########################################


@client.event
async def on_ready():
  print("Loaded & Online!")
  print(f"Logged in as: {client.user}")
  print(f"Connected to: {len(client.guilds)} guilds")
  print(f"Connected to: {len(client.users)} users")
  try:
    synced = await client.tree.sync()
    print(f"synced {len(synced)} commands")
  except Exception as e:
    print(f"ERROR Syncing commands: {e}")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        role_name = "Ticket Support"
        embed = discord.Embed(description="You are missing a required role to run this command.", color=0x2f3136)
        await ctx.send(embed=embed)

@client.event
async def on_command_completion(context: Context) -> None:
  from utils.Tools import get_db_connection
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands_used (
        user_id INTEGER PRIMARY KEY,
        commands_used INTEGER DEFAULT 1
    )
    ''')
    conn.commit()
    
    cursor.execute('SELECT commands_used FROM commands_used WHERE user_id = ?', (context.author.id,))
    result = cursor.fetchone()
    
    if result:
      cursor.execute('UPDATE commands_used SET commands_used = commands_used + 1 WHERE user_id = ?', 
                    (context.author.id,))
    else:
      cursor.execute('INSERT INTO commands_used (user_id, commands_used) VALUES (?, ?)', 
                    (context.author.id, 1))
    
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"Error tracking command usage: {e}")


  full_command_name = context.command.qualified_name
  split = full_command_name.split("\n")
  executed_command = str(split[0])
  hacker = client.get_channel(1216312097961676851)
  if context.guild is not None:
    try:
      embed = discord.Embed(color=0x2f3136)
      embed.set_author(
        name=f"Executed {executed_command} Command By : {context.author}",
        icon_url=f"{context.author.avatar}")
      embed.set_thumbnail(url=f"{context.author.avatar}")
      embed.add_field(name="<:right:1199668086916263956> Command Name :",
                      value=f"`{executed_command}`",
                      inline=False)
      embed.add_field(name="<:right:1199668086916263956> Command Content:",
                      value=f"`{context.message.content}`",
                      inline=False)
      embed.add_field(
        name="<:right:1199668086916263956> Command Executed By :",
        value=
        f"{context.author} | ID: [{context.author.id}](https://discord.com/users/{context.author.id})",
        inline=False)
      embed.add_field(
        name="<:right:1199668086916263956> Command Executed In :",
        value=
        f"{context.guild.name}  | ID: [{context.guild.id}](https://discord.com/users/{context.author.id})",
        inline=False)
      embed.add_field(
        name="<:right:1199668086916263956> Command Executed In Channel :",
        value=
        f"{context.channel.name}  | ID: [{context.channel.id}](https://discord.com/channel/{context.author.id}/{context.channel.id})",
        inline=False)
      embed.set_footer(text="Incite",
                       icon_url=client.user.display_avatar.url)
      await hacker.send(embed=embed)
    except Exception as e:
      await hacker.send(e)
  else:
    try:

      embed1 = discord.Embed(color=0x2f3136)
      embed1.set_author(
        name=f"Executed {executed_command} Command By : {context.author}",
        icon_url=f"{context.author.avatar}")
      embed1.set_thumbnail(url=f"{context.author.avatar}")
      embed1.add_field(name="<:right:1199668086916263956> Command Name :",
                       value=f"{executed_command}",
                       inline=False)
      embed1.add_field(
        name="<:right:1199668086916263956> Command Executed By :",
        value=
        f"{context.author} | ID: [{context.author.id}](https://discord.com/users/{context.author.id})",
        inline=False)
      embed1.set_footer(text="Powered By Incite",
                        icon_url=client.user.display_avatar.url)
      await hacker.send(embed=embed1)
    except Exception as e:
      await hacker.send(f"{executed_command}ERROR: {e}")


@commands.cooldown(1, 4, commands.BucketType.user)
@client.event
async def on_message(message):
    try:
        await client.process_commands(message)
        if message.content == (f'<@{client.user.id}>'):
            embed = discord.Embed(color=0x2f3136, description=f"Hey! I'm Incite\n\nTry using the `;help` command to get a list of commands\n\nIf you continue to have problems, consider asking for help on our discord server.")
        
            button = discord.ui.Button(
                label="Invite",
                style=discord.ButtonStyle.url,
                url=f"https://discord.com/api/oauth2/authorize?client_id=1117073053256527952&permissions=2056&scope=bot%20applications.commands"
            )
            button1 = discord.ui.Button(
                label="Support Server",
                style=discord.ButtonStyle.url,
                url="https://discord.gg/encoders-community-1058660812182519921"
            )
            button3 = discord.ui.Button(
                label="Website",
                style=discord.ButtonStyle.url,
                url="https://incitebot.xyz/"
            )

            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button1)
            view.add_item(button3)

            await message.reply(embed=embed, view=view)
    except discord.Forbidden:
        try:
            await message.author.send(embed=embed, view=view)
        except discord.Forbidden:
            pass
    except Exception as e:
        print(f"Error in on message main.py: {e}")

    
#from flask import Flask
#from threading import Thread

#app = Flask(__name__)


#@app.route('/')
#def home():
  #return "© Incite 2024"


#def run():
  #app.run(host='0.0.0.0', port=8080)


#def keep_alive():
  #server = Thread(target=run)
  #server.start()


#keep_alive()


async def main():
  async with client:
    os.system("clear")
    await client.load_extension("cogs")
    await client.load_extension("jishaku")
    await client.start(TOKEN)


if __name__ == "__main__":
  asyncio.run(main())