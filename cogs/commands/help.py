import discord
import asyncio
from discord.ext import commands
from difflib import get_close_matches
from contextlib import suppress
from core import Context
from core.Astroz import Astroz
from core.Cog import Cog
from utils.Tools import getConfig
from itertools import chain
import json
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from discord import app_commands

class CommandHelpView(discord.ui.View):
    def __init__(self, timeout=60):
        super().__init__(timeout=timeout)
        self.add_item(discord.ui.Button(label="View All Commands", url="https://incitebot.xyz/commands"))

class EnhancedHelpCommand(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.color = 0x2f3136
        self.commands_url = "https://incitebot.xyz/commands"
    
    async def is_blacklisted(self):
        """Check if the user is blacklisted and send a message if they are."""
        try:
            with open('blacklist.json', 'r') as f:
                data = json.load(f)
            
            if str(self.context.author.id) in data.get("ids", []):
                embed = discord.Embed(
                    description="You've been blacklisted from Incite, restricting access to my commands. If you wish to appeal this, kindly visit our Discord server at [Encoders'](https://discord.gg/encoders-community-1058660812182519921)",
                    color=self.color
                )
                await self.context.reply(embed=embed, mention_author=False)
                return True
            return False
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    async def on_help_command_error(self, ctx, error):
        ignored_errors = [
            commands.CommandOnCooldown, 
            commands.CommandNotFound,
            discord.HTTPException, 
            commands.CommandInvokeError
        ]
        
        if type(error) in ignored_errors:
            if isinstance(error, commands.CommandOnCooldown):
                return
            return await super().on_help_command_error(ctx, error)
        
        await self.context.reply(
            f"Unknown Error Occurred\n{getattr(error, 'original', error)}", 
            mention_author=False
        )

    async def command_not_found(self, string: str) -> None:
        print(f"Command not found triggered for: {string}")
        if await self.is_blacklisted():
            return
            
        special_cogs = {
            "security": "Security", 
            "anti": "Security", 
            "antinuke": "Security",
            "stick": "Sticky", 
            "stickremove": "Sticky",
            "gw": "Giveaway", 
            "gstart": "Giveaway",
            "media": "Media",
            "captcharole": "giveRoleAfterCaptcha command", 
            "verified": "giveRoleAfterCaptcha command",
            "timer": "Timer", 
            "remind": "Timer"
        }
        
        if string in special_cogs:
            cog_name = special_cogs[string]
            print(f"Looking for special cog: {cog_name}")
            cog = self.context.bot.get_cog(cog_name)
            if cog:
                print(f"Found cog: {cog.qualified_name}")
                try:
                    await self.send_cog_help(cog)
                    return
                except Exception as e:
                    print(f"Error sending cog help: {e}")
            else:
                print(f"Cog not found: {cog_name}")
                print(f"Available cogs: {[c.qualified_name for c in self.context.bot.cogs.values()]}")

        all_commands = {}
        for cmd in self.context.bot.walk_commands():
            all_commands[cmd.name.lower()] = cmd
            if hasattr(cmd, 'aliases') and isinstance(cmd.aliases, list):
                for alias in cmd.aliases:
                    if isinstance(alias, str):
                        all_commands[alias.lower()] = cmd

        string_lower = string.lower()
        if string_lower in all_commands:
            await self.send_command_help(all_commands[string_lower])
            return

        matches = get_close_matches(string_lower, all_commands.keys(), n=3, cutoff=0.6)
        
        if not matches:
            embed = discord.Embed(
                color=self.color,
                title="Command Not Found",
                description=f"No command found matching `{string}`.\nUse `{self.context.prefix}help` to see all available commands."
            )
            embed.set_footer(text="Visit https://incitebot.xyz/commands for a complete command list")
            await self.context.reply(embed=embed, mention_author=False)
            return

        class CommandSelect(discord.ui.Select):
            def __init__(self, matches, all_commands, help_command):
                self.help_command = help_command
                self.all_cmds = all_commands
                
                options = [
                    discord.SelectOption(
                        label=match[:25], 
                        description=f"View help for {match[:50]}",
                        value=match
                    ) for match in matches
                ]
                
                super().__init__(
                    placeholder="Available commands...",
                    min_values=1,
                    max_values=1,
                    options=options
                )
                
            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != self.help_command.context.author.id:
                    return await interaction.response.send_message("This isn't your help menu!", ephemeral=True)
                
                selected = self.values[0].lower()
                if selected in self.all_cmds:
                    await interaction.response.defer()
                    await self.help_command.send_command_help(self.all_cmds[selected])
        
        view = discord.ui.View(timeout=60)
        view.add_item(CommandSelect(matches, all_commands, self))
        
        suggestions = "\n".join([f"`{match}`" for match in matches])
        
        embed = discord.Embed(
            color=self.color,
            title="Command Not Found",
            description=f"Command `{string}` not found. Did you mean one of these?\n\n{suggestions}\n\nSelect an option below to see help for that command."
        )
        
        embed.set_footer(text="Incite • Command Suggestions")
        await self.context.reply(embed=embed, view=view, mention_author=False)

    async def send_bot_help(self, mapping):
        if await self.is_blacklisted():
            return
            
        view = CommandHelpView()
        
        await self.context.reply(
            content=f"{self.context.author.mention} visit {self.commands_url} for full list of commands.", 
            view=view,
            mention_author=False
        )

    async def send_command_help(self, command):
        if await self.is_blacklisted():
            return
            
        help_text = f">>> {command.help}" if command.help else '>>> None.'
        
        embed = discord.Embed(
            description=f"""```yaml
- [] = optional argument
- <> = required argument
- Do NOT Type These When Using Commands!```
{help_text}""",
            color=self.color
        )

        aliases = ' | '.join(command.aliases)
        embed.add_field(
            name="**Aliases**",
            value=f"{aliases}" if command.aliases else "None",
            inline=False
        )
        
        embed.add_field(
            name="**Usage**",
            value=f"`{self.context.prefix}{command.signature}`\n"
        )
        
        if hasattr(command, 'cog') and command.cog:
            embed.set_author(
                name=f"{command.cog.qualified_name.title()}",
                icon_url=self.context.bot.user.display_avatar.url
            )
        
        await self.context.reply(embed=embed, mention_author=False, delete_after=10)

    def get_command_signature(self, command: commands.Command) -> str:
        parent = command.full_parent_name
        
        if len(command.aliases) > 0:
            aliases = ' | '.join(command.aliases)
            alias = f'[{command.name} | {aliases}]'
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
            
        return f'{alias} {command.signature}'

    def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        
        if command.description:
            embed_like.description = f'{command.description}\n\n{command.help}'
        else:
            embed_like.description = command.help or 'None'

    async def send_group_help(self, group):
        if await self.is_blacklisted():
            return
            
        entries = [
            (f"`{self.context.prefix}{cmd.qualified_name}`", 
             f"{cmd.short_doc if cmd.short_doc else 'None'}\n\n")
            for cmd in group.commands
        ]
        
        paginator = Paginator(
            source=FieldPagePaginator(
                entries=entries,
                title=f"{group.qualified_name} Commands",
                description="<> Required | [] Optional\n\n",
                color=self.color,
                per_page=10
            ),
            ctx=self.context
        )
        await paginator.paginate()

    async def send_cog_help(self, cog):
        if await self.is_blacklisted():
            return None
            
        entries = [
            (f"`{self.context.prefix}{cmd.qualified_name}`",
             f"{cmd.short_doc if cmd.short_doc else 'None'}\n\n")
            for cmd in cog.get_commands()
        ]
        
        paginator = Paginator(
            source=FieldPagePaginator(
                entries=entries,
                title=f"{cog.qualified_name.title()} ({len(cog.get_commands())})",
                description="<> Required | [] Optional\n\n",
                color=self.color,
                per_page=10
            ),
            ctx=self.context
        )
        await paginator.paginate()

class Help(Cog, name="help"):
    def __init__(self, client: Astroz):
        self.client = client
        self._original_help_command = client.help_command
      
        attributes = {
            'name': "help",
            'aliases': ['h'],
            'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
            'help': 'Provides information of any command, modules'
        }
        
        client.help_command = EnhancedHelpCommand(command_attrs=attributes)
        client.help_command.cog = self
        
        self.setup_app_commands()
        
    def setup_app_commands(self):
        @self.client.tree.command(name="help", description="Get help with bot commands")
        @app_commands.describe(command="The command to get help with")
        async def help_slash(interaction: discord.Interaction, command: str = None):
            ctx = await self.client.get_context(interaction)
            
            if command:
                await ctx.send_help(command)
            else:
                await ctx.send_help()
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            try:
                with open('info.json', 'r') as f:
                    info_data = json.load(f)
                    np_users = info_data.get("np", [])
            except:
                np_users = []
            
            content = ctx.message.content
            
            if not content.startswith(";"):
                return
            cmd_name = content.split()[0][1:]
            
            self.client.help_command.context = ctx
            await self.client.help_command.command_not_found(cmd_name.lower())
            return
                
    async def cog_unload(self):
        self.client.help_command = self._original_help_command

def setup(client):
    client.add_cog(Help(client))