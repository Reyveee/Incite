import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import asyncio
from utils.Tools import *
import chat_exporter
from github import Github
import datetime
import time

GTOKEN = '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'

# GET TRANSCRIPTS
async def get_transcripts(member: discord.Member, channel: discord.TextChannel):
    export = await chat_exporter.export(channel=channel)
    file_name = f'{member.id}.html'
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(export)

# UPLOAD TO GITHUB
def upload(file_path: str, member_name: str):
    github = Github(GTOKEN)
    repo = github.get_repo("ashleft/Incite")
    file_name = f"{int(time.time())}"
    repo.create_file(
        path=f"tickets/{file_name}.html",
        message="Ticket log for {0}".format(member_name),
        branch="main",
        content=open(f"{file_path}", "r", encoding="utf-8").read()
    )

    return file_name

class close(Button):
    def __init__(self):
        super().__init__(label=f'Close', emoji='🔒', style=discord.ButtonStyle.red, custom_id="close")
        self.callback = self.button_callback
    
    async def button_callback(self, interaction: discord.Interaction):
        try:
            # Try to defer, but handle if interaction is already expired
            try:
                await interaction.response.defer(ephemeral=True)
            except (discord.NotFound, discord.InteractionResponded):
                return  # Silently return if interaction is invalid
            
            channel = interaction.channel
            creator_name = channel.topic
            creator = discord.utils.get(interaction.guild.members, name=creator_name)

            if creator is None:
                embed = discord.Embed(
                description=f"The ticket has already been closed.",
                color=0x2f3136
                )
                await interaction.followup.send(embed=embed, view=reopenTicket())
                return
            
            overwrite_creator = channel.overwrites_for(creator)
            overwrite_creator.view_channel = False
            await channel.set_permissions(creator, overwrite=overwrite_creator)
            await channel.edit(topic=f"Ticket closed | {creator}", name=f"closed-{creator_name}")

            await get_transcripts(member=creator, channel=interaction.channel)
            file_name= upload(f"{creator.id}.html", creator_name)

            link = f"https://incitebot.xyz/tickets/{file_name}"

            button1 = discord.ui.Button(label="Transcripts",
                                        style=discord.ButtonStyle.url,
                                        url=link)
            view = discord.ui.View()
            view.add_item(button1)



            embed = discord.Embed(
            description=f"Ticket closed by {interaction.user.mention}.",
            color=0x2f3136
            )
            userembed = discord.Embed(
                title="Ticket Closed",
                description=f"{creator.mention} your ticket is closed in the {interaction.guild.name}.\n\nReason: Ticket was closed using button.\nClosed by: {interaction.user.mention}\n\nNote: Transcripts will take a some time to update.",
                color=0x2f3136
            )
            userembed.set_footer(text=f'Incite - {interaction.guild.name}')
            await creator.send(embed=userembed, view=view)

            await interaction.followup.send(embed=embed, view=reopenTicket())
        except discord.NotFound:
            # Handle webhook/interaction not found
            pass
        except Exception as e:
            # Log the error but don't try to respond
            print(f"Error in close button: {e}")
            try:
                await interaction.followup.send(str(e), ephemeral=True)
            except discord.errors.InteractionResponded:
                pass


class reopen(Button):
    def __init__(self):
        super().__init__(label=f'Reopen', emoji='🔓', style=discord.ButtonStyle.grey, custom_id="reopen")
        self.callback = self.button_callback
    
    async def button_callback(self, interaction: discord.Interaction):
        try:
            # Try to defer first
            try:
                await interaction.response.defer(ephemeral=True)
            except (discord.NotFound, discord.InteractionResponded):
                return  # Silently return if interaction is invalid
            
            channel = interaction.channel
            channel_topic = channel.topic

            if not channel_topic or not channel_topic.startswith("Ticket closed"):
                embed = discord.Embed(
                    description=f"The ticket is not closed yet.",
                    color=0x2f3136
                )
                await interaction.followup.send(embed=embed, view=closeTicket())
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            
            category_name = channel.category.name
            

            cursor.execute('SELECT panel_name FROM ticket_panels WHERE guild_id = ? AND category_name = ?', 
                          (interaction.guild.id, category_name))
            panel_result = cursor.fetchone()
            
            conn.close()
            
            if panel_result is None:
                panel_name = "ticket"  # fallback
            else:
                panel_name = panel_result[0]

            creator_name = channel_topic[len("Ticket closed |"):].strip()
            creator = discord.utils.get(interaction.guild.members, name=creator_name)

            if creator is None:
                embed = discord.Embed(
                    description=f"Creator '{creator_name}' not found in the server.",
                    color=0x2f3136
                )
                await interaction.followup.send(embed=embed)
                return

            overwrite_creator = channel.overwrites_for(creator)

            if overwrite_creator is None:
                embed = discord.Embed(
                    description=f"No overwrites found for '{creator_name}' on this channel.",
                    color=0x2f3136
                )
                await interaction.followup.send(embed=embed)
                return

            overwrite_creator.view_channel = True
            await channel.set_permissions(creator, overwrite=overwrite_creator)
            await channel.edit(name=f"{panel_name}-{creator}", topic=f"{creator}")

            embed = discord.Embed(
                description=f"Ticket reopened by {interaction.user.mention}.",
                color=0x2f3136
            )
            userembed = discord.Embed(
                title="Ticket Reopened",
                description=f"{creator.mention} your ticket is reopened in the {interaction.guild.name} Discord.\n\nReopened by: {interaction.user.name}",
                color=0x2f3136
            )
            userembed.set_footer(text=f'Incite - {interaction.guild.name}')
            if interaction.user != creator:
                await creator.send(embed=userembed)
                
            await interaction.followup.send(embed=embed, view=closeTicket())
        except Exception as e:
            try:
                await interaction.followup.send(str(e), ephemeral=True)
            except discord.errors.InteractionResponded:
                print(f"Error in reopen button: {e}")
                pass

class Delete(Button):
    def __init__(self):
        super().__init__(label=f'Delete', emoji='🗑️', style=discord.ButtonStyle.red, custom_id="delete")
        self.callback = self.button_callback
    
    async def button_callback(self, interaction: discord.Interaction):
        try:
            channel = interaction.channel
            ETA = int(time.time() + 4)
            if "closed" in channel.name.lower():
                await interaction.response.send_message(f"Ticket is closed. Deleting this ticket <t:{ETA}:R>", ephemeral=True)
                await asyncio.sleep(5)
                await channel.delete(reason=f"Ticket deleted by {interaction.user.name}")
            elif "Ticket closed" in channel.topic:
                await interaction.response.send_message(f"Ticket is closed. Deleting this ticket <t:{ETA}:R>", ephemeral=True)
                await asyncio.sleep(5)
                await channel.delete(reason=f"Ticket deleted by {interaction.user.name}")
            else:
                await interaction.response.send_message(f"This channel is either not a ticket or the ticket is not closed. Please close the ticket before deleting it.", ephemeral=True)
        except Exception as e:
            print(f"Error in Ticket Delete button: {e}")
            await interaction.response.send_message("An error occurred while deleting this ticket.", ephemeral=True)





class closeTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(close())

class reopenTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Delete())
        self.add_item(reopen())

class DeleteTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Delete())


class CombinedTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(close())
        self.add_item(reopen())


# In the create class
class create(Button):
    def __init__(self):
        super().__init__(label='Create ticket', style=discord.ButtonStyle.blurple, custom_id=f'create', emoji='🎫')
        self.callback = self.button_callback
    
    async def button_callback(self, interaction: discord.Interaction):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            guild = interaction.guild
            user_id = str(interaction.user.id)

            cursor.execute('SELECT panel_name, category_name FROM ticket_panels WHERE guild_id = ? AND message_id = ?', 
                          (guild.id, interaction.message.id))
            panel_data = cursor.fetchone()
            
            conn.close()
            
            if panel_data is None:
                await interaction.response.send_message("An error occurred while retrieving the ticket panel information.", ephemeral=True)
                return
                
            panel_name = panel_data[0]
            category_name = panel_data[1]

            category = discord.utils.get(guild.categories, name=category_name)

            if category is None:
                await interaction.response.send_message("An error occurred while retrieving the ticket category.", ephemeral=True)
                return

            for ch in category.channels:
                if ch.topic == interaction.user.name:
                    await interaction.response.send_message(f"You already have a ticket opened. {ch.mention}", ephemeral=True)
                    return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True),
                discord.utils.get(guild.roles, name="Ticket Support"): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            channel = await category.create_text_channel(f"{panel_name}-{interaction.user.name}", overwrites=overwrites, topic=f'{interaction.user}')
            await interaction.response.send_message(f"<:whitecheck:1243577701638475787> Ticket created {channel.mention}!", ephemeral=True)

            embed = discord.Embed(
                description=f'{interaction.user.name}, your ticket has been created! We will help you as soon as possible.',
                color=0x2f3136
            )
            embed.set_footer(text=f'{interaction.guild.name}')

            await channel.send(f'{discord.utils.get(interaction.guild.roles, name="Ticket Support").mention}', embed=embed, view=closeTicket())

        except discord.NotFound:
            await interaction.response.send_message("Error: Unable to create the ticket. Please try again later.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Error: The bot does not have the necessary permissions to create channels. Please contact a server administrator.", ephemeral=True)
        except Exception as e:
            print(f"An unexpected error occurred during ticket creation: {e}")
            await interaction.response.send_message("An unexpected error occurred. Please try again later or contact support.", ephemeral=True)

class createTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(create())


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()
    
    def initialize_database(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket_panels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            panel_name TEXT NOT NULL,
            category_name TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_ticket_panels(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT message_id, panel_name, category_name FROM ticket_panels WHERE guild_id = ?', (guild_id,))
        panels = cursor.fetchall()
        
        conn.close()
        
        return panels
    
    def add_ticket_panel(self, guild_id, message_id, panel_name, category_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO ticket_panels (guild_id, message_id, panel_name, category_name) VALUES (?, ?, ?, ?)',
            (guild_id, message_id, panel_name, category_name)
        )
        
        conn.commit()
        conn.close()
    
    def delete_ticket_panel(self, guild_id, message_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM ticket_panels WHERE guild_id = ? AND message_id = ?', (guild_id, message_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def count_ticket_panels(self, guild_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM ticket_panels WHERE guild_id = ?', (guild_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return count

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild

        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                if member.name.lower() in (channel.topic or '').lower():
                    creator_name = channel.topic
                    creator = discord.utils.get(guild.members, name=creator_name)

                    new_channel_name = f"closed-{creator_name}"
                    if len(new_channel_name) > 100:
                        new_channel_name = new_channel_name[:100]

                    await channel.edit(
                        topic=f"Ticket automatically closed, {creator_name} left the server.",
                        name=new_channel_name
                    )

                    embed = discord.Embed(
                        description=f"Ticket automatically closed, {creator_name} left the server.",
                        color=0x2f3136
                    )
                    await channel.send(embed=embed, view=DeleteTicket())

    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.hybrid_group(name="ticket", description="Setup ticket panel.")
    async def ticket(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_role("Ticket Support")
    @ticket.command(name="delete", description="Delete a ticket.")
    async def delete(self, ctx: commands.Context, ticket: discord.TextChannel = None):
        try:
            channel = ctx.channel or ticket
            ETA = int(time.time() + 4)
            if "closed" in channel.name.lower():
                await ctx.send(f"Ticket is closed. Deleting this ticket <t:{ETA}:R>")
                await asyncio.sleep(5)
                await channel.delete(reason=f"Ticket deleted by {ctx.author.name}")
            
            elif "Ticket closed by" in channel.topic:
                await ctx.send(f"Ticket is closed. Deleting this ticket <t:{ETA}:R>")
                await asyncio.sleep(5)
                await channel.delete(reason=f"Ticket deleted by {ctx.author.name}")
        
            else:
                await ctx.send(f"This channel is either not a ticket or the ticket is not closed. Please close the ticket before deleting it.")
        except Exception as e:
            print(f"Errpr in ticket delete command: {e}")
            await ctx.send("An error occurred while deleting this ticket.")
    
    
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_role("Ticket Support")
    @ticket.command(name="close", description="Close the ticket.")
    async def _close(self, ctx: commands.Context, reason: str = None, ticket: discord.TextChannel = None):
        try:
            guild = ctx.guild
            channel = ticket or ctx.channel

            creator_name = channel.topic
            creator = discord.utils.get(ctx.guild.members, name=creator_name)

            Reason = reason
            if reason is None:
                Reason = "None"

            if creator is None:
                embed = discord.Embed(
                description=f"The ticket has already been closed.",
                color=0x2f3136
                )
                await ctx.send(embed=embed, view=reopenTicket())
                return

            overwrite_creator = channel.overwrites_for(creator)
            overwrite_creator.view_channel = False
            await channel.set_permissions(creator, overwrite=overwrite_creator)
            await channel.edit(topic=f"Ticket closed | {creator_name}", name=f"closed-{creator_name}")

            await get_transcripts(member=creator, channel=channel)
            file_name = upload(f"{creator.id}.html", creator_name)

            link = f"https://incitebot.xyz/tickets/{file_name}"

            button1 = discord.ui.Button(label="Transcripts",
                                        style=discord.ButtonStyle.url,
                                        url=link)
            view = discord.ui.View()
            view.add_item(button1)

            embed = discord.Embed(
                description=f"Ticket closed by {ctx.author.mention}.",
                color=0x2f3136
            )
            userembed = discord.Embed(
                title="Ticket Closed",
                description=f"{creator.mention} your ticket is closed in the {guild.name}.\n\nReason: {Reason}\nClosed by: {ctx.author.mention}\n\nNote: Transcripts will take a some time to update.",
                color=0x2f3136
            )
            userembed.set_footer(text=f'Incite - {guild.name}')
            await creator.send(embed=userembed, view=view)

            await ctx.send(embed=embed, view=reopenTicket())
        except Exception as e:
            await ctx.send(e)
    
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_role("Ticket Support")
    @ticket.command(name="reopen", description="Reopen the ticket.")
    async def _reopen(self, ctx: commands.Context, ticket: discord.TextChannel = None):
        try:
            channel = ticket or ctx.channel
            channel_topic = channel.topic

            if not channel_topic or not channel_topic.startswith("Ticket closed"):
                embed = discord.Embed(
                    description=f"The ticket is not closed yet.",
                    color=0x2f3136
                )
                await ctx.send(embed=embed, view=closeTicket())
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            
            category_name = channel.category.name
            
            cursor.execute('SELECT panel_name FROM ticket_panels WHERE guild_id = ? AND category_name = ?', 
                          (ctx.guild.id, category_name))
            panel_result = cursor.fetchone()
            
            conn.close()
            
            if panel_result is None:
                panel_name = "ticket"  # fallback
            else:
                panel_name = panel_result[0]

            creator_name = channel_topic[len("Ticket closed |"):].strip()
            creator = discord.utils.get(ctx.guild.members, name=creator_name)

            if creator is None:
                embed = discord.Embed(
                    description=f"Creator '{creator_name}' not found in the server.",
                    color=0x2f3136
                )
                await ctx.send(embed=embed)
                return

            overwrite_creator = channel.overwrites_for(creator)
            if overwrite_creator is None:
                embed = discord.Embed(
                    description=f"No overwrites found for '{creator_name}' on this channel.",
                    color=0x2f3136
                )
                await ctx.send(embed=embed)
                return

            overwrite_creator.view_channel = True
            await channel.set_permissions(creator, overwrite=overwrite_creator)
            await channel.edit(name=f"{panel_name}-{creator}", topic=f"{creator}")

            embed = discord.Embed(
                description=f"Ticket reopened by {ctx.author.mention}.",
                color=0x2f3136
            )
            userembed = discord.Embed(
                title="Ticket Reopened",
                description=f"{creator.mention} your ticket is reopened in the {ctx.guild.name} Discord.\n\nReopened by: {ctx.author.mention}",
                color=0x2f3136
            )
            userembed.set_footer(text=f'{self.bot.user.name} - {ctx.guild.name}')
            if ctx.author != creator:
                await creator.send(embed=userembed)

            await ctx.send(embed=embed, view=closeTicket())
        except Exception as e:
            await ctx.send(e)

            # TRANSCRIPTS COMMANDS

    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_role("Ticket Support")
    @ticket.command(name="transcripts", description="Send transcripts for this ticket.", aliases=['trans'])
    async def transc(self, ctx: commands.Context, user: discord.Member):
        try:
            channel = ctx.channel
            if ctx.channel.topic.startswith("Ticket closed"):
                creator_name = ctx.channel.topic[len("Ticket closed |"):].strip()
            else:
                creator_name = ctx.channel.topic

            creator = discord.utils.get(ctx.guild.members, name=creator_name)

            await get_transcripts(member=creator, channel=channel)
            file_name = upload(f"{creator.id}.html", creator_name)

            link = f"https://incitebot.xyz/tickets/{file_name}"

            button1 = discord.ui.Button(label="Transcripts",
                                        style=discord.ButtonStyle.url,
                                        url=link)
            view = discord.ui.View()
            view.add_item(button1)

            embed = discord.Embed(title="Ticket Transcripts",
                                  description=f"Click the button below for transcripts for your ticket.",
                                  color=0x2f3136)
            await user.send(embed=embed, view=view)
        except Exception as e:
            await ctx.send(str(e))

    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_role("Ticket Support")
    @ticket.group(name="user", description="ticket user add/remove.")
    async def _user(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
    
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_role("Ticket Support")
    @_user.command(name="add", description="Add user to ticket.")
    async def _add(self, ctx: commands.Context, user: discord.Member, ticket: discord.TextChannel = None):
        channel = ticket or ctx.channel
        overwrite = channel.overwrites_for(user)
        overwrite.view_channel = True
        await channel.set_permissions(user, overwrite=overwrite)
        embed = discord.Embed(description=f"Successfully added {user.mention} to {channel}.", color=0x2f3136)
        await ctx.reply(embed=embed, mention_author=False)
    
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_role("Ticket Support")
    @_user.command(name="remove", description="Remove user from ticket.")
    async def _remove(self, ctx: commands.Context, user: discord.Member, ticket: discord.TextChannel = None):
        channel = ticket or ctx.channel
        overwrite = channel.overwrites_for(user)
        overwrite.view_channel = False
        await channel.set_permissions(user, overwrite=overwrite)
        embed = discord.Embed(description=f"Successfully removed {user.mention} from {channel}.", color=0x2f3136)
        await ctx.reply(embed=embed, mention_author=False)
    
    

    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @ticket.group(name="panel", description="Manage ticket panels.")
    @commands.has_permissions(manage_guild=True)
    async def panel(self, ctx: commands.Context):
       if ctx.subcommand_passed is None:
          await ctx.send_help(ctx.command)
          ctx.command.reset_cooldown(ctx)
    
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    # Update the panel commands
    @panel.command(name="list", description="List all ticket panels.")
    async def list_panels(self, ctx: commands.Context):
        panels = self.get_ticket_panels(ctx.guild.id)
        
        if not panels:
            embed = discord.Embed(description="No ticket panels found.", color=0x2f3136)
            await ctx.send(embed=embed)
            return

        panel_info_list = []
        for panel_data in panels:
            panel_id = panel_data[0]
            panel_name = panel_data[1]
            panel_category = panel_data[2]
            panel_info_list.append(f"Panel Name: **{panel_name}**\nPanel ID: **{panel_id}**\nPanel Category: **{panel_category}**\n")

        panel_list = "\n".join(panel_info_list)
        embed = discord.Embed(title="List of ticket panels", description=panel_list, color=0x2f3136)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @panel.command(name="create", description="Create a ticket panel.")
    async def create_panel(self, ctx: commands.Context, channel: discord.TextChannel, panel_name: str, category_name: str = "incite-tickets"):
        try:
            guild = ctx.guild

            panel_count = self.count_ticket_panels(guild.id)
            if panel_count >= 3:
                embed = discord.Embed(
                    description="<:warn:1199645241729368084> You cannot create more than 3 ticket panels.",
                    color=0x2f3136
                )
                embed.set_footer(text=f"Use /ticket panel delete <panel> to delete panel.")
                await ctx.send(embed=embed)
                return

            role = discord.utils.get(guild.roles, name="Ticket Support")
            if role is None:
                role = await guild.create_role(name="Ticket Support")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            embed = discord.Embed(title=panel_name, description='To create a ticket react with 🎫', color=0x2f3136)
            embed.set_footer(text=f'{self.bot.user.name} - {guild.name}')

            message = await channel.send(embed=embed, view=createTicket())
            
            self.add_ticket_panel(guild.id, message.id, panel_name, category_name)

            category = discord.utils.get(guild.categories, name=category_name)

            if category is None:
                category = await guild.create_category_channel(name=category_name, overwrites=overwrites)

            for ch in category.channels:
                await ch.set_permissions(role, overwrite=overwrites[role])

            saved_message_id = message.id
            embed = discord.Embed(title="Success!", description=f"<:whitecheck:1243577701638475787> Ticket panel created in {channel.mention}.\nPanel ID: {saved_message_id}\nCategory: {category_name}\n\nNote: *To delete a ticket panel, please use `/ticket panel delete <panel_id>.`*", color=0x2f3136)
            await ctx.send(embed=embed, delete_after=20)
        except Exception as e:
            print(f"An error occurred during ticket panel creation: {e}")

    @panel.command(name="delete", description="Delete a ticket panel.")
    async def delete_panel(self, ctx: commands.Context, panel_id: str):
        try:
            success = self.delete_ticket_panel(ctx.guild.id, int(panel_id))
            
            if not success:
                embed = discord.Embed(
                description="Panel not found in the database.",
                color=0x2f3136
                )
                await ctx.send(embed=embed)
                return

            try:
                panel_message = await ctx.channel.fetch_message(int(panel_id))
                await panel_message.delete()
            except discord.NotFound:
                pass  # Message already deleted, that's fine

            embed = discord.Embed(
            description="<:whitecheck:1243577701638475787> Ticket panel deleted successfully.",
            color=0x2f3136
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in ticket panel delete command: {e}")
            embed = discord.Embed(
            description="An error occurred while deleting the ticket panel.",
            color=0x2f3136
            )
            await ctx.send(embed=embed)
        
            
