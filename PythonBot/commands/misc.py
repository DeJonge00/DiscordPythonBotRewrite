import logging

from discord.ext import commands
from discord.ext.commands import Cog, Context

from core.bot import PythonBot
from secret.secrets import LOG_LEVEL
from config.constants import PRIVATESERVERid, SNOWFLAKE_GENERAL

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

    async def print_to_admin_channel(self, ctx: Context, type: str, content: str):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command=type):
            return
        m = 'A {} from `{}`:\n```{}```'.format(type, ctx.message.author, content)
        channel = self.bot.get_channel(SNOWFLAKE_GENERAL)
        await self.bot.send_message(destination=channel, content=m)
        m = 'Your {} has been received and will be processed shortly'.format(type)
        await self.bot.send_message(destination=ctx.channel, content=m)

    @commands.command(name='suggestion', help='Make a suggestion to improve this bot', aliases=['suggest'])
    async def suggestion(self, ctx: Context, *args):
        await self.print_to_admin_channel(ctx, 'suggestion', content=' '.join(args))

    @commands.command(name='complaint', help='Make a complaint to the owners of this bot', aliases=['complain'])
    async def complaint(self, ctx: Context, *args):
        await self.print_to_admin_channel(ctx, 'complaint', content=' '.join(args))

    @commands.command(name='bugreport', help='Notify the owners of this bot of a bug or fault you experienced',
                      aliases=['bug', 'report'])
    async def bugreport(self, ctx: Context, *args):
        await self.print_to_admin_channel(ctx, 'bugreport', content=' '.join(args))


def setup(bot):
    bot.add_cog(MiscCommands(bot))
