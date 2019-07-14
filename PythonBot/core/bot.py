from core import constants, logging as log
from core.customHelpFormatter import customHelpFormatter
from database import general as dbcon
from secret.secrets import prefix

from datetime import datetime
from discord.ext.commands import Bot, Context
from discord import Message, TextChannel, DMChannel, Forbidden


class PythonBot(Bot):
    def __init__(self, music=False, rpggame=False, api=False):
        self.running = True

        self.commands_counters = {}

        self.MUSIC = music
        self.RPGGAME = rpggame
        self.API = api

        super(PythonBot, self, ).__init__(command_prefix=prefix, pm_help=True)  # , formatter=customHelpFormatter)

    async def _get_prefix(self, message):
        try:
            p = dbcon.get_prefix(message.server.id)
            return p if p else await super(PythonBot, self)._get_prefix(message)
        except (KeyError, AttributeError):
            return await super(PythonBot, self)._get_prefix(message)

    @staticmethod
    async def delete_message(message: Message):
        if not isinstance(message.channel, DMChannel):
            try:
                return await message.delete()
            except Forbidden:
                m = '{} | {} | No permissions to delete message \'{}\''
                m = m.format(message.guild.name, message.channel.name, message.content)
                await log.error(m, filename=message.guild.name)

    async def send_message(self, destination: Context, content=None, *, file=None, tts=False, embed=None):
        try:
            try:
                guild = destination.guild
            except AttributeError:
                guild = None

            if content:
                await log.message_content(content, destination.channel, guild, self.user, datetime.now(), [],
                                          "send message:")
            if file:
                await log.message_content(content, destination.channel, guild, self.user, datetime.now(), [],
                                          "pic")
            if embed:
                await log.log("send a message", str(self.user), 'embedded message',
                              str(guild) if guild else str(destination))
            return await destination.send(content=content, tts=tts, embed=embed)
        except Forbidden:
            if embed:
                m = 'Sorry, it seems I cannot send embedded messages in this channel...'
                await self.send_message(destination, content=m)
            elif file:
                m = 'Sorry, it seems I cannot send files in this channel...'
                await self.send_message(destination, content=m)
            else:
                m = '{} | {} | No permissions to send message \'{}\''
                if isinstance(destination, TextChannel):
                    m = m.format(destination.guild.name, str(destination), content)
                else:
                    m = m.format('direct message', str(destination), content)
                await log.error(m, filename=str(destination))

    @staticmethod
    def command_allowed_in(location_type: str, identifier: int, command_name: str):
        """
        Checks whether the issued command is allowed in the issued location
        :param location_type: either 'server' of 'channel'
        :param identifier: the id of the server or channel (depending on location_type)
        :param command_name: the name of the command issued
        :return: A boolean stating the command is allowed (True) or banned here (False)
        """
        return command_name == 'togglecommand' or not (dbcon.get_banned_command(location_type, identifier, command_name)
                                                       or dbcon.get_banned_command(location_type, identifier, 'all'))

    @staticmethod
    def command_allowed_in_server(server_id: int, command_name: str):
        split = command_name.split(' ')
        return PythonBot.command_allowed_in('server', server_id, command_name) and (
                len(split) <= 1 or PythonBot.command_allowed_in('server', server_id, split[0]))

    @staticmethod
    def command_allowed_in_channel(channel_id: int, command_name: str):
        split = command_name.split(' ')
        return PythonBot.command_allowed_in('channel', channel_id, command_name) and (
                len(split) <= 1 or PythonBot.command_allowed_in('channel', channel_id, split[0]))

    async def pre_command(self, ctx: Context, command: str, is_typing=True, delete_message=True,
                          cannot_be_private=False, must_be_private=False, must_be_nsfw=False, owner_check=False,
                          checks=[]):
        """
        This command should be run first in each command, substitutes the premade wrappers.
        :param ctx: The context of the send message
        :param command: the command issued
        :param is_typing: Indicate whether to show the bot typing in the channel
        :param delete_message: Indicate whether to delete the message afterwards
        :param cannot_be_private: Indicate whether the command can be issued in a private channel
        :param must_be_private: Indicate whether the command must be issued in a private channel
        :param must_be_nsfw: Indicate whether the command can be issued outside of NSFW channels
        :param owner_check: Indicate whether the user must be a guild owner to issue the command
        :param checks: Additional permission checks, the user must have at least one of these to issue the command
        :return:
        """
        if ctx.message.author.id not in [constants.KAPPAid, constants.NYAid]:
            if owner_check:
                await ctx.send("Hahahaha, no")
                await log.message(ctx.message, 'Command "{}" used, but owner rights needed'.format(command))
                return False
            elif checks:
                perms = ctx.channel.permissions_for(ctx.message.author)
                check_names = [constants.permissions.get(y) for y in checks]
                if not any([x[1] for x in list(perms) if x[0] in check_names]):
                    await ctx.send("Hahahaha, no")
                    m = 'Command "{}" used, but either of [{}] needed'.format(command, ' '.join(check_names))
                    await log.message(ctx.message, m)
                    return False
        if isinstance(ctx.channel, DMChannel):
            if cannot_be_private:
                await ctx.send('This command cannot be used in private channels')
                await log.message(ctx.message, 'Command "{}" used, but cannot be private'.format(command))
                return False
        else:
            if must_be_private:
                await ctx.send('This command has to be used in a private conversation')
                await log.message(ctx.message, 'Command "{}" used, but must be private'.format(command))
                return False
            if must_be_nsfw and not ctx.channel.is_nsfw():
                await ctx.send('This command cannot be used outside NSFW channels')
                await log.message(ctx.message, 'Command "{}" used, but must be an NSFW channel'.format(command))
                return False
            if not self.command_allowed_in_server(ctx.guild.id, command):
                await log.message(ctx.message, 'Command "{}" used, but is serverbanned'.format(command))
                return False
            if not self.command_allowed_in_channel(ctx.channel.id, command):
                await log.message(ctx.message, 'Command "{}" used, but is channelbanned'.format(command))
                return False
            if delete_message and dbcon.get_delete_commands(ctx.guild.id):
                await ctx.message.delete()

        await log.message(ctx.message, 'Command "{}" used'.format(command))
        if is_typing:
            await ctx.channel.trigger_typing()
        dbcon.command_counter(command, ctx.message)
        return True
