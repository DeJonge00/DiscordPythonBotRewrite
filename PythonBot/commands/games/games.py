from discord import Reaction
from discord.ext import commands
from discord.ext.commands import Cog, Context

from core.bot import PythonBot

EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
ROW_NUMS = {"1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5, "6️⃣": 6, "7️⃣": 7}

C4_HEIGHT = 7
C4_WIDTH = 7
WIN_LENGTH = 4


def c4_convert(i: int) -> str:
    if i == PLAYER1:
        return "🟥"
    if i == PLAYER2:
        return "🟨"
    return "⬛"


class ConnectFourGame:
    def __init__(self, p1):
        self.board = [[EMPTY for _ in range(C4_WIDTH)] for _ in range(C4_HEIGHT)]
        self.turn = PLAYER1
        self.player1 = p1.id
        self.player1_name = p1.display_name
        self.player2 = None
        self.player2_name = None
        self.running = True

    def get_first_empty(self, column: int):
        for i in range(C4_HEIGHT):
            if self.board[C4_HEIGHT - i - 1][column] == EMPTY:
                return C4_HEIGHT - i - 1
        return -1

    def right_player(self, player):
        if self.turn == PLAYER1:
            return player.id == self.player1
        if self.player2:
            return player.id == self.player2
        self.player2 = player.id
        self.player2_name = player.display_name
        return True

    def move(self, move: int, player):
        if not self.running or not self.right_player(player):
            return False
        h = self.get_first_empty(move)
        if h < 0:
            return False
        self.board[h][move] = self.turn
        self.turn = PLAYER1 if self.turn == PLAYER2 else PLAYER2
        return True

    def check_h(self):
        for h in range(C4_HEIGHT):
            for w in range(int(C4_WIDTH / 2) + 1):
                a = self.board[h][w : w + WIN_LENGTH - 1]
                if a.count(PLAYER1) == WIN_LENGTH or a.count(PLAYER2) == WIN_LENGTH:
                    return self.board[h][w]
        return EMPTY

    def check_v(self):
        for h in range(int(C4_HEIGHT / 2) + 1):
            for w in range(C4_WIDTH):
                a = [self.board[h + i][w] for i in range(WIN_LENGTH)]
                if a.count(PLAYER1) == WIN_LENGTH or a.count(PLAYER2) == WIN_LENGTH:
                    return self.board[h][w]
        return EMPTY

    def check_d(self):
        for h in range(int(C4_HEIGHT / 2) + 1):
            for w in range(int(C4_WIDTH / 2) + 1):
                a = [self.board[h + i][w + i] for i in range(4)]
                if a.count(PLAYER1) == WIN_LENGTH or a.count(PLAYER2) == WIN_LENGTH:
                    return self.board[h][w]
        for h in range(int(C4_HEIGHT / 2) + 1):
            for w in range(int(C4_WIDTH / 2 + 1), C4_WIDTH):
                a = [self.board[h + i][w - i] for i in range(4)]
                if a.count(PLAYER1) == WIN_LENGTH or a.count(PLAYER2) == WIN_LENGTH:
                    return self.board[h][w]
        return EMPTY

    def check(self):
        r = self.check_h() or self.check_v() or self.check_d()
        if r == PLAYER1:
            self.running = False
            return self.player1_name + " has won!"
        if r == PLAYER2:
            self.running = False
            return self.player2_name + " has won!"
        if self.turn == PLAYER1:
            return self.player1_name + "'s turn"
        return (self.player2_name if self.player2_name else "Player 2") + "'s turn"

    def __str__(self):
        return "\n".join(
            [" ".join([c4_convert(i) for i in r]) for r in self.board]
            + [" ".join(ROW_NUMS.keys())]
            + [self.check()]
        )


class GamesCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        self.bot.games_cog = self
        self.connect_four_games = {}
        self.connect_four_messages = {}

    async def handle_reaction(self, reaction: Reaction, member):
        if reaction.message.id not in self.connect_four_messages.values():
            return
        g = self.connect_four_games.get(reaction.message.guild.id)
        if not g:
            return
        g.move(ROW_NUMS.get(reaction.emoji) - 1, member)
        await reaction.message.remove_reaction(reaction, member)
        await reaction.message.edit(content=str(g))

    def get_connect_four_game(self, server_id: int, player):
        g = self.connect_four_games.get(server_id)
        if not g or not g.running:
            g = ConnectFourGame(player)
            self.connect_four_games[server_id] = g
        return g

    @commands.command(
        name="connectfour", help="Play a game of connect 4", aliases=["c4"]
    )
    async def connectfour(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="connectfour"
        ):
            return

        if len(args) > 0 and args[0] in ["reset", "stop", "quit"]:
            del self.connect_four_messages[ctx.guild.id]
            del self.connect_four_games[ctx.guild.id]
            return

        game = self.get_connect_four_game(ctx.guild.id, ctx.author)
        m = await self.bot.send_message(destination=ctx.channel, content=str(game))
        self.connect_four_messages[ctx.guild.id] = m.id
        for r in ROW_NUMS.keys():
            await m.add_reaction(emoji=r)


def setup(bot):
    bot.add_cog(GamesCommands(bot))
