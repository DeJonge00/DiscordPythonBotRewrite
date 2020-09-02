import logging

from discord import TextChannel, Member
from discord.ext import commands
from discord.ext.commands import Cog, Context

from commands.games.blackjack.game_instance import BlackjackGame, GAME_OVER, PLAYING
from core.bot import PythonBot
from config.running_options import LOG_LEVEL

logging.basicConfig(
    filename="logs/blackjack.log",
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


class Blackjack(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        self.games = {}
        self.prev = {}

    async def show(self, channel: TextChannel, game: BlackjackGame):
        await self.bot.send_message(destination=channel, embed=game.as_embed())

    def get_game(self, player: Member):
        game = self.games.get(player.id)
        if not game or game.game_over:
            game = BlackjackGame(player)
            self.games[player.id] = game
        return game

    async def help(self, channel: TextChannel):
        await self.bot.send_message(
            destination=channel, content="Choose 'draw' or 'fold"
        )

    async def draw(self, channel: TextChannel, game: BlackjackGame):
        game.draw()
        await self.show(channel=channel, game=game)

    async def fold(self, channel: TextChannel, game: BlackjackGame):
        await self.bot.send_message(destination=channel, embed=game.fold())

    @commands.group(name="blackjack", help="Play a game of blackjack", aliases=["bj"])
    async def blackjack(self, ctx: Context, *args):
        if len(args) > 0:
            if args[0] in ["d", "draw"]:
                await self.draw(channel=ctx.channel, game=self.get_game(ctx.author))
                return

            if args[0] in ["f", "fold", "s", "stop"]:
                await self.fold(channel=ctx.channel, game=self.get_game(ctx.author))
                return
        await self.help(ctx.channel)


def setup(bot):
    bot.add_cog(Blackjack(bot))
