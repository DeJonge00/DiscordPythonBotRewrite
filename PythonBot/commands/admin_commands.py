from core.setup import get_cogs
from core.bot import PythonBot

from discord.ext import commands
from discord.ext.commands import Cog, Context


# Mod commands
class AdminCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        print('Admin started')

    @commands.command(pass_context=1, hidden=True)
    async def reload(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='reload', owner_check=True):
            return

        cog = ' '.join(args)
        if cog not in get_cogs():
            await self.bot.send_message(ctx, "That cog is either")
            return

        self.bot.unload_extension(cog)
        self.bot.load_extension(cog)

        await self.bot.send_message(ctx, "Loaded {}!".format(cog))


def setup(bot):
    bot.add_cog(AdminCommands(bot))
