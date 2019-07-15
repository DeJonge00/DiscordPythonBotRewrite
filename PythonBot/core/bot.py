from config import constants
from core import logging as log
from discord.ext.commands.formatter import HelpFormatter
from database import general as dbcon
from secret.secrets import prefix

from datetime import datetime
from discord.ext.commands import Bot, Context
from discord import Message, TextChannel, DMChannel, Forbidden, Embed, Member
import re


class PythonBot(Bot):
    def __init__(self, music=False, rpggame=False, api=False):
        self.running = True

        self.commands_counters = {}

        self.MUSIC = music
        self.RPGGAME = rpggame
        self.API = api

        # TODO Add custom help formatter
        super(PythonBot, self, ).__init__(command_prefix=prefix, pm_help=True)  # , formatter=HelpFormatter)

    """ Helper functions """

    @staticmethod
    def prep_str(s):
        """
        Strip text of weird characters
        :param s: The text
        :return: filtered text
        """
        return ''.join([l for l in s if re.match('[a-zA-Z0-9]', l)])

    async def ask_one_from_multiple(self, ctx: Context, group: list, question='', errors: dict = {}):
        """
        Ask a user to select one object from a list by name
        :param ctx: Where the question should be asked
        :param group: The list of items to be chosen from
        :param question: The question to ask
        :param errors: The possible error messages
        :return:
        """
        m = question
        for x in range(min(len(group), 10)):
            m += '\n{}) {}'.format(x + 1, str(group[x]))
        m = await self.send_message(ctx, m)

        def check(message: Message):
            return message.author is ctx.message.author and message.channel is ctx.channel

        r = await self.wait_for(event='message', timeout=60, check=check)

        if dbcon.get_delete_commands(ctx.guild.id):
            await self.delete_message(m)
            if r:
                await self.delete_message(r)

        if not r:
            if errors:
                error = errors.get('no_reaction') if errors.get('no_reaction') else 'Or not...'
                await self.send_message(ctx, error)
            raise ValueError
        try:
            num = int(r.content) - 1
            if not (0 <= num < min(10, len(group))):
                raise ValueError
        except ValueError:
            await self.send_message(ctx, 'That was not a valid number')
            raise
        return group[num]

    async def get_member_from_message(self, ctx: Context, args: [str], in_text=False,
                                      errors: dict = {'none': ''}, from_all_members=False) -> Member:
        """
        Determine the Member object of the user in the given message
        :param ctx: Where to send the answer
        :param args: The text to search through
        :param in_text: Text only mentions allowed (as opposed to mentions)
        :param errors: The custom errors to return
            errors_example = {
              'no_mention': No user was mentioned in the message,
              'no_user': No user was found with the given name,
              'no_reaction': The user did not react to the choice within a minute
            }
        :param from_all_members: Indicate whether to limit the search to members in the current server
        :return:
        """
        # Exceptions
        if len(ctx.message.mentions) > 0:
            return ctx.message.mentions[0]

        if len(args) <= 0 or (isinstance(ctx.message.channel, DMChannel) and not from_all_members):
            return ctx.message.author

        if not in_text:
            if errors:
                error = errors.get('no_mention') if errors.get('no_mention') else 'Please mention a user'
                await self.send_message(ctx.message.channel, error)
            raise ValueError

        # Look for users with the given name
        name = PythonBot.prep_str(' '.join(args)).lower()
        if from_all_members:
            users = [x for x in self.get_all_members() if PythonBot.prep_str(x.name).lower().startswith(name) or
                     PythonBot.prep_str(x.display_name).lower().startswith(name)]
        else:
            users = [x for x in ctx.message.guild.members if PythonBot.prep_str(x.name).lower().startswith(name) or
                     PythonBot.prep_str(x.display_name).lower().startswith(name)]
        users.sort(key=lambda s: len(s.name))

        # Check validity of lookup results
        if len(users) <= 0:
            if errors:
                error = errors.get('no_users') if errors.get(
                    'no_users') else 'I could not find a user with that name'
                await self.send_message(error)
            raise ValueError
        if len(users) == 1:
            return users[0]

        # Give options if multiple users were found
        return await self.ask_one_from_multiple(ctx, users, question='Which user did you mean?')

    @staticmethod
    def prep_str_for_print(s: str):
        return s.encode("ascii", "replace").decode("ascii")

    async def quit(self):
        self.running = False
        for key in self.commands_counters.keys():
            print('Command "{}" was used {} times'.format(key, self.commands_counters.get(key)))
        if self.RPGGAME:
            self.rpggame.quit()
        if self.MUSIC:
            await self.musicplayer.quit()

    """ Overwiting functions """

    async def get_prefix(self, message):
        """
        Overwrites default get_prefix, adds lookup in the database first. Defaults to the super function.
        :param message: The message (including server) to find prefix for
        :return:
        """
        try:
            p = dbcon.get_prefix(message.guild.id)
            return p if p else await super(PythonBot, self).get_prefix(message)
        except (KeyError, AttributeError):
            return await super(PythonBot, self).get_prefix(message)

    @staticmethod
    async def delete_message(message: Message):
        """
        Function that allows extra checks to be done before deleting a message.
        :param message: The message to be deleted
        :return:
        """
        if not isinstance(message.channel, DMChannel):
            try:
                return await message.delete()
            except Forbidden:
                m = '{} | {} | No permissions to delete message \'{}\''
                m = m.format(message.guild.name, message.channel.name, message.content)
                await log.error(m, filename=message.guild.name)

    async def send_message(self, destination: Context, content: str = None, *, file=None, tts: bool = False,
                           embed: Embed = None) -> Message:
        """
        Function that allows extra checks to be done before sending a message.
        :param destination: The destination the message should be send to
        :param content: The content of the message
        :param file: The file attached to the message
        :param tts: Whether the message is text-to-speech or not
        :param embed: An embed to be send as part of the message
        :return:
        """
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
                # TODO Adjust logging for embedded messages
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
        # Check permissions
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
        # Check whether the message can be send in this specific server and channel
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

        # Log and send the message
        await log.message(ctx.message, 'Command "{}" used'.format(command))
        if is_typing:
            await ctx.channel.trigger_typing()
        dbcon.command_counter(command, ctx.message)
        return True
