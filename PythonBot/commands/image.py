from core.bot import PythonBot

from discord.ext import commands
from discord.ext.commands import Cog, Context


class ImageCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        print('Image commands cog started')


def setup(bot):
    bot.add_cog(ImageCommands(bot))
