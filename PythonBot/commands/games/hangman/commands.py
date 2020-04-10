from config.command_text import hangmanwords
import logging
import random
import string

from discord import TextChannel, Member, DMChannel
from discord.ext import commands
from discord.ext.commands import Cog, Context

from commands.games.hangman.game_instance import HangmanInstance, MAX_FAULTS, WIN, GAME_OVER, RIGHT, WRONG
from config.command_text import hangmanwords
from core.bot import PythonBot
from secret.secrets import LOG_LEVEL

logging.basicConfig(filename='logs/hangman.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

CUSTOM_WORD = 'custom'
RANDOM_WORD = 'random'


class Hangman(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        self.games = {}
        self.prev = {}
        print('Hangman started')

    async def show(self, channel: TextChannel, game: HangmanInstance, message="", win=False):
        embed = game.get_win_embed(message) if win else game.get_loss_embed(message)
        m = await self.bot.send_message(channel, embed=embed)
        if channel.id in self.prev.keys():
            await self.bot.delete_message(self.prev.get(channel.id))
        if not isinstance(channel, DMChannel):
            if game.faults >= 6:
                self.prev[channel.id] = None
            else:
                self.prev[channel.id] = m

    @commands.group(name='hangman', help="Hangman game", aliases=["hm"])
    async def hangman(self, ctx: Context, *args):
        if args and args[0] in ['new', 'create']:
            await self.new_game(ctx, *args[1:])
            return
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='hangman'):
            return
        game = self.games.get(ctx.channel.id)
        if not game:
            await self.bot.send_message(ctx.channel, 'There is no game running here')
            return

        # Guess sentence
        if " ".join(args).lower().translate(
                str.maketrans('', '', string.punctuation)) == \
                game.word.lower().translate(str.maketrans('', '', string.punctuation)):
            self.games.pop(ctx.channel.id)
            await self.show(ctx.message.channel, game, message=ctx.message.author.name, win=True)
            return
        if len(args[0]) > 1:
            game.faults += 1
            if game.faults >= MAX_FAULTS:
                self.games.pop(ctx.channel.id)
            await self.show(ctx.message.channel, game, "Sorry, the word was not \"" + " ".join(args) + "\"...")
            return

        # Guess letter
        result = game.guess(args[0])
        if result == WIN:
            self.games.pop(ctx.channel.id)
            await self.show(ctx.channel, game, message=ctx.message.author.name, win=True)
            return
        if result == RIGHT:
            await self.show(ctx.channel, game,
                            "You guessed right, the letter \"" + " ".join(args) + "\" is in the sentence")
            return
        if result == WRONG:
            await self.show(ctx.channel, game,
                            "Sorry, the letter \"" + " ".join(args) + "\" is not in the sentence")
            return
        if result == GAME_OVER:
            self.games.pop(ctx.channel.id)
            await self.show(ctx.message.channel, game)
            return

    async def new_game(self, ctx: Context, *args):
        if not args:
            await self.bot.send_message(ctx.channel, 'Please specify \'custom\' or \'random\'')
            return
        if args[0] in ['random', 'r']:
            await self.new_random_game(ctx, *args[1:])
            return
        if args[0] in ['custom', 'c']:
            await self.new_custom_game(ctx, *args[1:])
            return
        await self.bot.send_message(ctx.channel, 'Please specify \'custom\' or \'random\'')

    async def new_random_game(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='hangman new random'):
            return

        game = self.games.get(ctx.channel.id)
        if game:
            await self.bot.send_message(ctx.channel, 'There is already a game running here...')
            return
        self.games[ctx.channel.id] = HangmanInstance(random.choice(hangmanwords))
        await self.bot.send_message(ctx.channel, content='New hangman game initialized')

    async def ask_custom_word(self, member: Member):
        c = member.dm_channel
        if not c:
            c = await member.create_dm()
        await self.bot.send_message(c, "Hi there!\nWhat would you like the sentence for the hangman game to be?")
        m = await self.bot.wait_for('message', check=lambda m: m.author.id == member.id and m.channel.id == c.id,
                                    timeout=60)
        return m.content if m else None

    async def new_custom_game(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='hangman new custom'):
            return
        game = self.games.get(ctx.channel.id)
        if game:
            await self.bot.send_message(ctx.channel, 'There is already a game running here...')
            return
        if args:
            word = ' '.join(args)
        else:
            word = await self.ask_custom_word(ctx.author)
            if not word:
                m = "Senpai hasn't responded in a while, I guess we will stop playing then..."
                await self.bot.send_message(ctx.channel, m)
                return
        self.games[ctx.channel.id] = HangmanInstance(word)
        await self.bot.send_message(ctx.channel, content='New hangman game initialized')


def setup(bot):
    bot.add_cog(Hangman(bot))
