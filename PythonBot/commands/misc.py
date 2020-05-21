import logging

from discord.ext import commands
from discord.ext.commands import Cog, Context

from core.bot import PythonBot
from secret.secrets import LOG_LEVEL

logging.basicConfig(filename='logs/misc_commands.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


class MiscCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot

    @commands.command(name='inviteme', help="Invite me to your own server")
    async def inviteme(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='inviteme'):
            return
        url = "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=506588243".format(
            self.bot.user.id)
        await self.bot.send_message(ctx.channel, "Here is a link to invite me:\n" + url)

    @commands.command(name='helpserver', help="Join my masters discord server for anything")
    async def helpserver(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='helpserver'):
            return
        await self.bot.send_message(ctx.channel, "A link to the past:\nhttps://discord.gg/KBxRd7x")

    @commands.command(name='vote', help='Voting for me helps me help other servers too! Some features are '
                                        'even multi-server compatible!')
    async def vote(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='vote'):
            return
        await self.bot.send_message(ctx.channel, "Vote for me here:\nhttps://top.gg/bot/244410964693221377")


def setup(bot):
    bot.add_cog(MiscCommands(bot))
