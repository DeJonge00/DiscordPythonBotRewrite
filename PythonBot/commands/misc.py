from core.bot import PythonBot

from discord.ext import commands
from discord.ext.commands import Cog, Context


class MiscCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        print('Misc commands cog started')

    @commands.command(name='inviteme', help="Invite me to your own server")
    async def inviteme(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='inviteme'):
            return
        await self.bot.send_message(ctx.channel, "Here is a link to invite me:\nhttps://discordapp.com/api/oauth2/aut"
                                                 "horize?client_id=244410964693221377&permissions=472951872&scope=bot")

    @commands.command(name='helpserver', help="Join my masters discord server for anything")
    async def helpserver(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='helpserver'):
            return
        await self.bot.send_message(ctx.channel, "A link to the past:\nhttps://discord.gg/KBxRd7x")


def setup(bot):
    bot.add_cog(MiscCommands(bot))
