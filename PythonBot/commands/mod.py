from core.bot import PythonBot
from config.constants import TEXT, KICK_REASON, member_counter_message
from database.general.general import WELCOME_TABLE, GOODBYE_TABLE
from database.general.welcome import set_message

from discord import Member, TextChannel, PermissionOverwrite
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

    @commands.command(name='banish', help="BANHAMMER")
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

    @staticmethod
    async def command_membercount(user: Member, channel: TextChannel):
        if not channel.permissions_for(user).manage_channels:
            return {TEXT: 'I need permission to manage channels'}
        name = member_counter_message.format(channel.guild.member_count)
        permissions = {channel.guild.default_role: PermissionOverwrite(connect=False, read_messages=True)}
        channel = await channel.guild.create_voice_channel(name=name, position=0, overwrites=permissions)
        return {TEXT: 'Channel \'{}\' created'.format(name)}

    @commands.command(name='membercount', help="Count the people in this server for everyone to see",
                      aliases=['membercounter'])
    async def membercount(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='purge', is_typing=False,
                                          perm_needed=['administrator', 'manage_channels']):
            return
        answer = await ModCommands.command_membercount(ctx.guild.me, ctx.channel)
        await self.bot.send_message(ctx.channel, answer.get(TEXT))

    @commands.command(name='purge', help="Remove a weird chat")
    async def purge(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='purge', is_typing=False,
                                          perm_needed=['administrator', 'manage_messages']):
            return
        match = re.match('.*?(\d+)?.*((<@!?\d+>)+)?', ' '.join(args))
        limit = int(match.groups()[0]) if match else 10

        if len(ctx.message.mentions) > 0:
            await ctx.channel.purge(check=lambda m: m.author in ctx.message.mentions, limit=limit)
            return
        await ctx.channel.purge(limit=limit)

    @staticmethod
    def set_welcome(args: [str], table: str, type: str, guild_id: int, channel_id: int):
        if len(" ".join(args)) > 120:
            return {TEXT: "Sorry, this message is too long..."}
        if re.match('.*{.+}.*', " ".join(args)):
            return {TEXT: "Something went terribly wrong..."}
        set_message(table, guild_id, channel_id, " ".join(args))
        if len(args) > 0:
            return {TEXT: "{} message for this server is now: ".format(type) + " ".join(args).format("<username>")}
        return {TEXT: "{} message for this server has been reset".format(type)}

    @commands.command(pass_context=1, help="Sets a goodbye message", aliases=['goodbye'])
    async def setgoodbye(self, ctx, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='setgoodbye'):
            return

        answer = ModCommands.set_welcome(args, GOODBYE_TABLE, 'Goodbye', ctx.guild.id, ctx.channel.id)
        await self.bot.send_message(ctx.channel, content=answer.get(TEXT))

    # {prefix}setwelcome <message>
    @commands.command(pass_context=1, help="Sets a welcome message", aliases=['welcome'])
    async def setwelcome(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='setwelcome',
                                          perm_needed=['manage_server', 'administrator']):
            return

        answer = ModCommands.set_welcome(args, WELCOME_TABLE, 'Welcome', ctx.guild.id, ctx.channel.id)
        await self.bot.send_message(ctx.channel, content=answer.get(TEXT))


def setup(bot):
    bot.add_cog(ModCommands(bot))
