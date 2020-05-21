import logging
from datetime import datetime

from discord import Status, Game

from core.bot import PythonBot
from core.utils import get_cogs
from database.general import bot_information
from secret.secrets import game_name, LOG_LEVEL

logging.basicConfig(filename='logs/setup.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

START_COG_MESSAGE = 'Cog started: {}'


def create_bot():
    bot = PythonBot(music=True, rpggame=True)
    for cog in get_cogs():
        bot.load_extension(cog)
        print(START_COG_MESSAGE.format(cog))
    if bot.RPGGAME:
        bot.load_extension('commands.rpg.rpg_main')
        bot.load_extension('commands.rpg.rpggameactivities')
        bot.loop.create_task(bot.time_loop())
        print(START_COG_MESSAGE.format('RPG game'))
    if bot.MUSIC:
        bot.load_extension('commands.music.music')
        print(START_COG_MESSAGE.format('Music player'))

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
