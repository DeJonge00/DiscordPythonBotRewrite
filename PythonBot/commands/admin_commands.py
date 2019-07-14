from discord.ext.commands import Cog


# Mod commands
class AdminCommands(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        print('Admin started')


def setup(bot):
    bot.add_cog(AdminCommands(bot))
