import discord
from discord.ext import commands
import os
from core import Cog, Astroz, Context
from utils.Tools import *
import random
import asyncio
#from utils.Tools import Timer
import discord_games as games
from discord_games import button_games


# define games Cog
class Games(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.twenty_48_emojis = {
            "0": "<:grey:821404552783855658>",
            "2": "<:twoo:821396924619161650>",
            "4": "<:fourr:821396936870723602>",
            "8": "<:eightt:821396947029983302>",
            "16": "<:sixteen:821396959616958534>",
            "32": "<:thirtytwo:821396969632169994>",
            "64": "<:sixtyfour:821396982869524563>",
            "128": "<:onetwentyeight:821396997776998472>",
            "256": "<:256:821397009394827306>",
            "512": "<:512:821397040247865384>",
            "1024": "<:1024:821397097453846538>",
            "2048": "<:2048:821397123160342558>",
            "4096": "<:4096:821397135043067915>",
            "8192": "<:8192:821397156127965274>",
        }


    @commands.command(name="connect4")
    async def connect4(self, ctx: commands.Context[commands.Bot], member: discord.User):
        game = games.ConnectFour(
            red=ctx.author,
            blue=member,
        )
        await game.start(ctx)

    @commands.command(name="hangman")
    async def hangman(self, ctx: commands.Context[commands.Bot]):
        game = games.Hangman()
        await game.start(ctx, delete_after_guess=True)

    @commands.command(name="chess")
    async def chess(self, ctx: commands.Context[commands.Bot], member: discord.User):

        game = games.Chess(
            white=ctx.author,
            black=member,
        )
        await game.start(ctx, timeout=60, add_reaction_after_move=True)

    @commands.command(name="typerace")
    async def typerace(self, ctx: commands.Context[commands.Bot]):

        game = games.TypeRacer()
        await game.start(ctx, timeout=30)

    @commands.command(name="battleship")
    async def battleship(
        self, ctx: commands.Context[commands.Bot], member: discord.User
    ):

        game = games.BattleShip(ctx.author, member)
        await game.start(ctx)

    # Button Games: Requires discord.py >= v2.0.0

    @commands.command(name="tictactoe")
    async def tictactoe(
        self, ctx: commands.Context[commands.Bot], member: discord.User
    ):
        game = button_games.BetaTictactoe(cross=ctx.author, circle=member)
        await game.start(ctx)

    @commands.command(name="wordle")
    async def worldle(self, ctx: commands.Context[commands.Bot]):

        game = button_games.BetaWordle(color=ctx.bot.color)
        await game.start(ctx)

    @commands.command(name="guess")
    async def guess(self, ctx: commands.Context[commands.Bot]):

        game = button_games.BetaAkinator()
        await game.start(ctx, timeout=120, delete_button=True)

    @commands.command(name="twenty48")
    async def twenty48(self, ctx: commands.Context[commands.Bot]):

        game = button_games.BetaTwenty48(self.twenty_48_emojis)
        await game.start(ctx)

    @commands.command(name="memory")
    async def memory_game(self, ctx: commands.Context[commands.Bot]):

        game = button_games.MemoryGame()
        await game.start(ctx)

    @commands.command(name="rps")
    async def rps(
        self, ctx: commands.Context[commands.Bot], player: discord.User = None
    ):

        game = button_games.BetaRockPaperScissors(
            player
        )  # defaults to playing with bot if player = None
        await game.start(ctx)

