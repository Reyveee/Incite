import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Cog
import json
from utils import blacklist_check, ignore_check

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counting_data = self.load_counting_data()
        self.count_scores = self.load_count_scores()
        self.warns = {}

    def load_counting_data(self):
        try:
            with open('counting.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_counting_data(self):
        with open('counting.json', 'w') as f:
            json.dump(self.counting_data, f, indent=4)

    def load_count_scores(self):
        try:
            with open('countscores.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_count_scores(self):
        with open('countscores.json', 'w') as f:
            json.dump(self.count_scores, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return

            if not message.guild:
                return
                
            guild_id = str(message.guild.id)

            if guild_id not in self.counting_data:
                return

            if 'channel' not in self.counting_data[guild_id]:
                return
                
            counting_channel = self.counting_data[guild_id]['channel']
            last_count = self.counting_data[guild_id]['last_count']
            last_user_id = self.counting_data[guild_id].get('last_user_id')

            if message.channel.id == counting_channel:
                try:
                    count = int(message.content)
                except ValueError:
                    await message.delete()
                    return

                if count != last_count + 1:
                    await message.delete()
                    nxt = last_count + 1
                    error = discord.Embed(description=f"Next number is {nxt}. You get -5 score.", color=0x2f3136)
                    errorm = await message.channel.send(embed=error)
                    await asyncio.sleep(4)
                    await errorm.delete()
                    self.update_user_score(message.author, -5)
                    return
                
                if last_user_id == str(message.author.id):
                    await message.delete()
                    error_embed = discord.Embed(description="You can't count two numbers in a row.", color=0x2f3136)
                    error = await message.channel.send(content=message.author.mention ,embed=error_embed)
                    await asyncio.sleep(4)
                    await error.delete()
                    return

                self.counting_data[guild_id]['last_count'] = count
                self.counting_data[guild_id]['last_user_id'] = str(message.author.id)
                if count == 100:
                    await message.add_reaction('💯')
                else:
                    await message.add_reaction('☑')

                self.save_counting_data()
                self.update_user_score(message.author, 5)
        except Exception as e:
            print(f"Error in Counting Module On Message: {e}")




    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            if before.author.bot:
                return

            guild_id = str(before.guild.id)
            if guild_id not in self.counting_data:
                return

            counting_channel = self.counting_data[guild_id]['channel']
            if before.channel.id != counting_channel:
                return

            if str(self.counting_data[guild_id]['last_count']) in before.content:
                overwrites = before.channel.overwrites_for(before.author)
                overwrites.read_messages = False
                await before.channel.set_permissions(before.author, overwrite=overwrites)
                
                self.update_user_score(before.author, -20)

                self.counting_data[guild_id]['last_count'] -= 1
                self.save_counting_data()
                    
                embed = discord.Embed(
                    description=f"{before.author.mention} edited their count message! (-20 points)\nThey have been banned from the counting channel.\nThe count has been decremented to {self.counting_data[guild_id]['last_count']} so others can continue.",
                    color=0x2f3136
                )
                await before.channel.send(embed=embed, delete_after=5)
                
                await after.delete()

        except Exception as e:
            print(f"Error in Counting Module On Message Edit: {e}")


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            if message.author.bot:
                return

            guild_id = str(message.guild.id)
            if guild_id not in self.counting_data:
                return

            counting_channel = self.counting_data[guild_id]['channel']
            if message.channel.id != counting_channel:
                return

            try:
                count = int(message.content)
                if count == self.counting_data[guild_id]['last_count'] and str(message.author.id) == self.counting_data[guild_id]['last_user_id']:
                    self.counting_data[guild_id]['last_count'] = count - 1
                    self.counting_data[guild_id]['last_user_id'] = None
                    self.save_counting_data()

                    self.update_user_score(message.author, -5)

                    embed = discord.Embed(
                        description=f"{message.author.mention} deleted their count of **{count}**! (-5 points)\nContinue counting from **{count-1}**",
                        color=0x2f3136
                    )
                    await message.channel.send(embed=embed)
            except ValueError:
                pass

        except Exception as e:
            print(f"Error in Counting Module On Message Delete: {e}")


    def update_user_score(self, user, points):
        user_id = str(user.id)

        if user_id not in self.count_scores:
            self.count_scores[user_id] = {'score': 0}

        self.count_scores[user_id]['score'] += points
        self.save_count_scores()



    @commands.hybrid_group(name='counting', help="Setup counting module")
    @blacklist_check()
    @ignore_check()
    async def counting(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @counting.command(name='setchannel', description="Set counting channel.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def set_counting_channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        self.counting_data[guild_id] = {'channel': channel.id, 'last_count': 0, 'blacklist': []}
        self.save_counting_data()
        embeds = discord.Embed(description='Lets Start counting from `1`.',
                      color=0x2f3136)
        await channel.send(embed=embeds)
        embed=discord.Embed(description=f'Counting channel set to {channel.mention}', color=0x2f3136)
        await ctx.send(embed=embed)

    @counting.command(name='removechannel', description="remove counting channel.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def remove_counting_channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)

        if guild_id in self.counting_data:
            del self.counting_data[guild_id]
            self.save_counting_data()
            embed=discord.Embed(description=f'Counting channel configuration removed from this {channel.mention}.', color=0x2f3136)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(description='Counting channel configuration not found for this server.', color=0x2f3136)
            await ctx.send(embed=embed)


    @counting.command(name='stats', description="list top scorers in the current guild.")
    @blacklist_check()
    @ignore_check()
    async def guild_stats(self, ctx):
        guild_id = str(ctx.guild.id)

        if guild_id not in self.counting_data:
            embed=discord.Embed(description=f'Counting module not set up for this server.', color=0x2f3136)
            await ctx.send(embed=embed)
            return

        scores = [(int(user_id), data['score']) for user_id, data in self.count_scores.items()]
        scores.sort(key=lambda x: x[1], reverse=True)
 
        embed = discord.Embed(title=f'Top 5 Scorers in {ctx.guild.name}', color=0x2f3136)

        if not scores:
            embed.add_field(name='No Scorers', value='No users have scores yet.', inline=False)
        else:
            for i, (user_id, score) in enumerate(scores[:5]):
                user = self.bot.get_user(user_id)
                user_name = user.name if user else 'None'

                embed.add_field(name=f'{i + 1}. {user_name}', value=f'Score: {score}', inline=False)

        await ctx.send(embed=embed)

    @counting.command(name='leaderboard', description="leaderboard for top scorers overall.")
    async def global_leaderboard(self, ctx):
        scores = [(int(user_id), data['score']) for user_id, data in self.count_scores.items()]
        scores.sort(key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title='Global Top 10 Scorers', color=0x2f3136)
        for i, (user_id, score) in enumerate(scores[:10]):
            user = self.bot.get_user(user_id)
            if user:
                embed.add_field(name=f'{i + 1}. {user.name}', value=f'Score: {score}', inline=False)

        await ctx.send(embed=embed)

    @counting.command(name='points', description="see user counting points.")
    async def user_points(self, ctx, user: discord.Member=None):
        user = user
        if user is None:
            user = ctx.author

        user_id = str(user.id)

        if user_id not in self.count_scores:
            embed=discord.Embed(title=f"{user.name}", description=f'You have no recorded points.', color=0x2f3136)
            await ctx.send(embed=embed)
            return

        score = self.count_scores[user_id]['score']
        embed=discord.Embed(title=f"{user.name}", description=f'Your current score is: **{score}**', color=0x2f3136)
        await ctx.send(embed=embed)

    @counting.command(name='setcount', help="Set the server counting last count (Admin Only)")
    async def set_count(self, ctx, number: int):
        if ctx.author.guild_permissions.administrator:
            guild_id = str(ctx.guild.id)
            self.counting_data.setdefault(guild_id, {}).update({'last_count': number})
            self.save_counting_data()

            embed = discord.Embed(
                description=f"The last count has been updated to {number}.",
                color=0x2f3136
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You need administrator permissions to use this command.",
                color=0x2f3136
            )
            await ctx.send(embed=embed, delete_after=10)

    @counting.command(name='disablemaths', description="Disable counting with maths. Messages like 1+1 will not count as a valid number.", help="Disable counting with maths. Messages like 1+1 will not count as a valid number.")
    @commands.has_permissions(administrator=True)
    async def disable_maths(self, ctx, status: str):
        guild_id = str(ctx.guild.id)

        if guild_id not in self.counting_data:
            embed=discord.Embed(description=f"Counting module not set up for this server.", color=0x2f3136)
            await ctx.send(embed=embed)
            return

        if status.lower() == 'on':
            self.counting_data[guild_id]['disable_maths'] = True
            self.save_counting_data()
            embed=discord.Embed(description=f"Math counting is now disabled.", color=0x2f3136)
            await ctx.send(embed=embed)
        elif status.lower() == 'off':
            self.counting_data[guild_id]['disable_maths'] = False
            self.save_counting_data()
            embed=discord.Embed(description=f"Math counting is now enabled.", color=0x2f3136)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Invalid type. Use `on` or `off`.')


