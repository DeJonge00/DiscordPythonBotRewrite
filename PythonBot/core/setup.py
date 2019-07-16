from config import constants
from config.constants import STAR_EMOJI
from core import message_handler, logging as log
from core.bot import PythonBot
from database import general as dbcon
from secret.secrets import game_name

from datetime import datetime
from discord import Member, Status, Game, Spotify, Message, Forbidden, DMChannel


def get_cogs():
    return [
        'commands.admin',
        'commands.commands',
        'commands.config',
        'commands.image',
        'commands.lookup',
        'commands.misc',
        'commands.mod'
    ]


def create_bot():
    bot = PythonBot()
    for cog in get_cogs():
        bot.load_extension(cog)

    @bot.event
    async def on_ready():
        print('\nStarted bot')
        print("User: " + bot.user.name)
        print("Disc: " + bot.user.discriminator)
        print("ID: " + str(bot.user.id))
        print("Started at: " + datetime.utcnow().strftime("%H:%M:%S") + "\n")
        if not hasattr(bot, 'uptime'):
            bot.uptime = datetime.utcnow()
        await bot.change_presence(activity=Game(name=game_name), status=Status.do_not_disturb)

        dbcon.update_server_list(bot.guilds)

    @bot.event
    async def on_message(message: Message):
        if message.author.bot:
            return
        if isinstance(message.channel, DMChannel):
            await log.log("direct message", message.author.name, message.content, "dm")
            for pic in message.attachments:
                await log.message(message, "pic", pic["url"])
            await message_handler.new_message(bot, message)
        else:
            if message.content and message.guild.id not in constants.bot_list_servers:
                await message_handler.new_message(bot, message)

        # Commands in the message
        try:
            await bot.process_commands(message)
        except Forbidden:
            await log.message(message, 'Forbidden Exception')

        # Send message to rpggame for exp
        if bot.RPGGAME and (len(message.content) < 2 or (message.content[:2] == '<@') or
                            (message.content[0].isalpha() and message.content[1].isalpha())):
            bot.rpggame.handle(message)

    @bot.event
    async def on_member_update(before: Member, after: Member):
        if before.id == constants.NYAid:
            if before.activity != after.activity:
                if isinstance(after.activity, Spotify):
                    activity = Game(name='🎵 {}: {} 🎵'.format(after.activity.artist, after.activity.title))
                else:
                    activity = after.activity if after.activity else Game(name=game_name)
                await bot.change_presence(activity=activity, status=Status.do_not_disturb)
                return

    @bot.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return
        if reaction.emoji == "\N{BROKEN HEART}":
            if reaction.message.author.id is bot.user.id:
                await bot.delete_message(reaction.message)
                return
        if bot.MUSIC:
            await bot.musicplayer.handle_reaction(reaction)
        if bot.RPGGAME:
            await bot.rpggame.handle_reaction(reaction)
        if bot.EMBED_LIST:
            await bot.embed_list.handle_reaction(reaction)
        if reaction.emoji == STAR_EMOJI:
            await message_handler.handle_star_reaction(bot, reaction)

    return bot
