from core import constants
from core.bot import PythonBot
from database import general as dbcon
from secret.secrets import game_name

from datetime import datetime
from discord import Member, Status, Game

COGS = [
    'commands.admin_commands',
    'commands.commands',
    'commands.config_commands'
]


def create_bot():
    bot = PythonBot()
    for cog in COGS:
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
    async def on_member_update(before: Member, after: Member):
        if before.id == constants.NYAid:
            if before.activity != after.activity:
                activity = after.activity if after.activity else Game(name=game_name)
                await bot.change_presence(activity=activity, status=Status.do_not_disturb)
                return

    return bot
