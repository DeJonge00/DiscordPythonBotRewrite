from discord.ext.commands import Bot

from secret.secrets import prefix

from core.customHelpFormatter import customHelpFormatter


class PythonBot(Bot):
    def __init__(self, music=True, rpggame=True, api=True):
        self.running = True

        self.commands_counters = {}

        self.MUSIC = music
        self.RPGGAME = rpggame
        self.API = api

        super(PythonBot, self, ).__init__(command_prefix=prefix, pm_help=True)#, formatter=customHelpFormatter)

    def pre_command(self):
        return True
