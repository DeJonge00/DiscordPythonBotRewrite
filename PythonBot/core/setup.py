from config import constants
from config.constants import STAR_EMOJI
from core import logging as log
from core.handlers import message_handler, channel_handlers
from core.bot import PythonBot
from core.utils import get_cogs, update_member_counter, on_member_message
from database.general import bot_information, general
from secret.secrets import game_name
from commands.rpg.rpg_main import RPGGame

from datetime import datetime
from discord import Member, Status, Game, Spotify, Message, Forbidden, DMChannel, Guild, VoiceChannel, User, Activity, \
    VoiceState


def create_bot():
    bot = PythonBot(music=True, rpggame=True)
    for cog in get_cogs():
        bot.load_extension(cog)
    if bot.RPGGAME:
        bot.load_extension('commands.rpg.rpg_main')
    if bot.MUSIC:
        bot.load_extension('commands.music.music')

    @bot.event
    async def on_ready():
        print('\nStarted bot', bot.user.name)
        print("Disc: " + bot.user.discriminator)
        print("ID: " + str(bot.user.id))
        print("Started at: " + datetime.utcnow().strftime("%H:%M:%S") + "\n")
        if not hasattr(bot, 'uptime'):
            bot.uptime = datetime.utcnow()
        await bot.change_presence(activity=Game(name=game_name), status=Status.do_not_disturb)

        bot_information.update_server_list(bot.guilds)
    return bot
