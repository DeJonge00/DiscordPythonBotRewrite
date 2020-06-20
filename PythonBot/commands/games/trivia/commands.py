import json
import requests
import logging
from discord.ext import commands
from discord.ext.commands import Cog
from commands.games.trivia import game_instance
from config.running_options import LOG_LEVEL

logging.basicConfig(
    filename="logs/trivia.log",
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

CATEGORIES_URL = "https://opentdb.com/api_category.php"


class Trivia(Cog):
    def __init__(self, mybot):
        self.bot = mybot
        self.categories = self.get_cats()
        self.game_instances = {}

    # {prefix}trivia <categories>
    @commands.group(pass_context=1, help="Trivia", aliases=["tr"])
    async def trivia(self, ctx):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="trivia"
        ):
            return
        if not ctx.invoked_subcommand:
            await self.bot.send_message(
                ctx,
                "[Usage] To start a new game use: {}trivia new".format(
                    await self.bot.get_prefix(ctx.message)
                ),
            )
            return

    @trivia.command(pass_context=1, aliases=["categories"])
    async def cat(self, ctx):
        display_cat = "Trivia categories are: \n"
        for cat in self.categories:
            display_cat += str(cat["nbr"]) + ") " + cat["name"] + ".\n"
        await self.bot.send_message(ctx, display_cat)
        return

    @trivia.command(pass_context=1)
    async def new(self, ctx):
        if ctx.message.channel in self.game_instances:
            await self.bot.send_message(
                ctx, "There's already a trivia game on this channel!"
            )
            return
        await self.bot.send_message(
            ctx,
            "New trivia game requested!\nPlease chose a game mode: 1)time attack  2)turn by turn",
        )

        def check_channel(msg):
            return msg.channel != ctx.channel or msg.author != ctx.message.author

        game_mode = await self.bot.wait_for("message", check=check_channel)
        if game_mode.content == "1":
            await self.bot.send_message(ctx, "Time attack mode selected!")
            game_mode = "time"
        elif game_mode.content == "2":
            await self.bot.send_message(ctx, "Turn by turn mode selected!")
            game_mode = "turn"
        else:
            await self.bot.send_message(
                ctx, ctx.message.author.mention + " stop wasting my time."
            )
            return
        self.game_instances[ctx.message.channel] = game_instance.TriviaInstance(
            my_bot=self.bot,
            channel=ctx.message.channel,
            author=ctx.message.author,
            categories=self.categories,
            mode=game_mode,
        )
        # get game parameters, then start and play it until the end
        await self.game_instances[ctx.message.channel].get_params(ctx)
        # goobye fren
        self.delete_instance(ctx.message.channel)
        return

    @trivia.command(pass_context=1)
    async def join(self, ctx):
        if await self.is_game_running(
            ctx=ctx, channel=ctx.message.channel, author=ctx.message.author
        ):
            await self.game_instances[ctx.message.channel].player_turn_join(
                ctx=ctx, author=ctx.message.author
            )
        return

    @trivia.command(pass_context=1)
    async def quit(self, ctx):
        if await self.is_game_running(
            ctx=ctx, channel=ctx.message.channel, author=ctx.message.author
        ):
            await self.game_instances[ctx.message.channel].player_quit(
                ctx=ctx, author=ctx.message.author
            )
        return

    @trivia.command(pass_context=1)
    async def cancel(self, ctx):
        if await self.is_game_running(
            ctx=ctx, channel=ctx.message.channel, author=ctx.message.author
        ):
            if (
                self.game_instances[ctx.message.channel].game_creator
                == ctx.message.author
            ):
                self.game_instances[ctx.message.channel].stop_playing()
                self.delete_instance(ctx.message.channel)
            else:
                await self.bot.send_message(
                    ctx,
                    ctx.message.author.mention
                    + " only the game creator can cancel the game",
                )
        return

    def delete_instance(self, channel):
        try:
            del self.game_instances[channel]
            return
        except KeyError as e:
            logging.error(e)

    @staticmethod
    def get_cats():
        categories = json.loads(requests.get(url=CATEGORIES_URL).text)[
            "trivia_categories"
        ]
        i = 0
        while i < len(categories):
            categories[i]["nbr"] = i + 1
            i += 1
        return categories

    async def is_game_running(self, ctx, channel, author):
        if channel in self.game_instances:
            return True
        await self.bot.send_message(
            ctx, author.mention + " there's currently no running game on this channel."
        )
        return False


def setup(bot):
    bot.add_cog(Trivia(bot))
