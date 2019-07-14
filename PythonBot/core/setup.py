from core.bot import PythonBot

COGS = [
    'commands.admin_commands',
    'commands.commands'
]


def create_bot():
    bot = PythonBot()
    for cog in COGS:
        bot.load_extension(cog)
    return bot
