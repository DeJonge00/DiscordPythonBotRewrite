import logging

from discord.ext import commands
from discord.ext.commands import Cog, Context

from commands.games.minesweeper.game_instance import MinesweeperInstance, LOSS
from core.bot import PythonBot
from secret.secrets import LOG_LEVEL

logging.basicConfig(filename='logs/minesweeper.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


# Normal commands
class Minesweeper(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        self.games = {}
        print('Minesweeper cog started')

    @staticmethod
    def read_parameters(height: str, width: str, mines: str):
        try:
            height = min(max(int(height), 1), 50)
        except ValueError:
            height = 10
        try:
            width = min(max(int(width), 1), 50)
        except ValueError:
            width = 15
        try:
            mines = min(max(int(mines), 1), height * width)
        except ValueError:
            mines = 20
        if height > width:
            height, width = width, height
        return height, width, mines

    async def minesweeper_new(self, ctx: Context, *args):
        if len(args) < 3:
            await self.bot.send_message(ctx.channel, 'Please specify height, width and mines')
            return
        game = self.games.get(ctx.channel.id)
        if game:
            await self.bot.send_message(ctx.channel, 'Another game is busy in this channel...')
            return
        game = MinesweeperInstance(*Minesweeper.read_parameters(*args[0:3]))
        self.games[ctx.channel.id] = game
        await self.bot.send_message(ctx.channel, game.as_parameter_str())
        await self.bot.send_message(ctx.channel, str(game))

    async def minesweeper_quit(self, ctx: Context, *args):
        game = self.games.get(ctx.channel.id)
        if not game:
            await self.bot.send_message(ctx.channel, 'There is no game to quit')
            return
        del self.games[ctx.channel.id]
        await self.bot.send_message(ctx.channel, 'Game quit successfully')

    async def minesweeper_guess(self, ctx: Context, *args):
        game = self.games.get(ctx.channel.id)
        if not game:
            await self.bot.send_message(ctx.channel, 'There is no game to guess in')
            return
        try:
            x, y = min(max(int(args[0]), 1), game.width), min(max(int(args[1]), 1), game.height)
        except IndexError:
            await self.bot.send_message(ctx.channel, 'Please enter the parameters \'x\' and \'y\'')
            return
        except ValueError:
            await self.bot.send_message(ctx.channel, 'Those arent whole numbers...')
            return

        result = game.guess(x - 1, y - 1)
        if result == LOSS:
            del self.games[ctx.channel.id]
        await self.bot.send_message(ctx.channel, str(game))

    @commands.command(name='minesweeper', help="Minesweeper game", aliases=["ms"])
    async def minesweeper(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='minesweeper'):
            return
        if not args:
            m = "Specify 'new' {height} {width} {mines} | <x> <y> | 'quit'"
            await self.bot.send_message(ctx.channel, m)
            return
        if args[0] == 'new':
            await self.minesweeper_new(ctx, *args[1:])
            return
        if args[0] == 'quit':
            await self.minesweeper_quit(ctx, *args[1:])
            return
        if len(args) >= 2:
            await self.minesweeper_guess(ctx, *args[0:])
            return
        m = "Specify 'new' {height} {width} {mines} | <x> <y> | 'quit'"
        await self.bot.send_message(ctx.channel, m)


def setup(bot):
    bot.add_cog(Minesweeper(bot))
