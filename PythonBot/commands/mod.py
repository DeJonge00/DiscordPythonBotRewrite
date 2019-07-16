from core.bot import PythonBot
from config.constants import TEXT, KICK_REASON

from discord import Member
from discord.ext import commands
from discord.ext.commands import Cog, Context

import re


class ModCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        print('Mod commands cog started')

    @staticmethod
    def command_banish(mod: Member, users: [Member], text: str):
        if len(users) <= 0:
            return {TEXT: 'Mention one or more users to banish them from the server'}

        matched_groups = re.match('^.*?( <@!?\d+>)+ ?(.*)$', text).groups()

        if not matched_groups[-1]:
            return {KICK_REASON: 'The basnish command was used by {} to kick you'.format(mod)}
        return {KICK_REASON: '{} banned you with the reason: \'{}\''.format(mod, matched_groups[-1])}

    @commands.command(pass_context=1, help="BANHAMMER")
    async def banish(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='banish',
                                          perm_needed=['kick_members', 'administrator']):
            return

        answer = ModCommands.command_banish(ctx.author, ctx.message.mentions, ctx.message.content)
        if answer.get(TEXT):
            await self.bot.send_message(ctx.channel, answer.get(TEXT))
            return

        for user in ctx.message.mentions:
            await user.kick(reason=answer.get(KICK_REASON))


def setup(bot):
    bot.add_cog(ModCommands(bot))
