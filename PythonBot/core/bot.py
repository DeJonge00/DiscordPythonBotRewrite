from config import constants
from core import logging as log
from discord.ext.commands.formatter import HelpFormatter
from database.general import delete_commands, prefix, banned_commands, command_counter
from secret.secrets import prefix

from discord import Message, TextChannel, DMChannel, Forbidden, Embed, Member
from discord.ext.commands import Bot, Context
import re


class PythonBot(Bot):
    def __init__(self, music=False, rpggame=False, api=False, embed_list=False):
        self.running = True

        self.commands_counters = {}

        self.MUSIC = music
        self.RPGGAME = rpggame
        self.API = api
        self.EMBED_LIST = embed_list
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
        is_private = isinstance(ctx.channel, DMChannel)

        m = question
        for x in range(min(len(group), 10)):
            m += '\n{}) {}'.format(x + 1, str(group[x]))
        m = await self.send_message(ctx.channel, m)

        def check(message: Message):
            return message.author is ctx.message.author and message.channel is ctx.channel

        r = await self.wait_for(event='message', timeout=60, check=check)

        if is_private or delete_commands.get_delete_commands(ctx.guild.id):
            await self.delete_message(m)
            if r:
                await self.delete_message(r)

        if not r:
            if errors:
                error = errors.get('no_reaction') if errors.get('no_reaction') else 'Or not...'
                await self.send_message(ctx.channel, error)
            raise ValueError
        try:
            num = int(r.content) - 1
            if not (0 <= num < min(10, len(group))):
                raise ValueError
        except ValueError:
            await self.send_message(ctx.channel, 'That was not a valid number')
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

        if len(args) <= 0 or (isinstance(ctx.channel, DMChannel) and not from_all_members):
            return ctx.message.author

        if not in_text:
            if errors:
                error = errors.get('no_mention') if errors.get('no_mention') else 'Please mention a user'
                await self.send_message(ctx.channel, error)
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
                await self.send_message(ctx.channel, error)
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
            p = prefix.get_prefix(message.guild.id)
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
                await log.error_on_message(message, 'No permissions to delete message')

    async def send_message(self, destination, content: str = None, *, file=None, tts: bool = False,
                           embed: Embed = None):
        """
        Function that allows extra checks to be done before sending a message.
        :param destination: The destination the message should be send to
        :param content: The content of the message
        :param file: The file attached to the message
        :param tts: Whether the message is text-to-speech or not
        :param embed: An embed to be send as part of the message
        :return:
        """

        if isinstance(destination, Context):
            destination: TextChannel = destination.channel

        # Exceptions
        if not isinstance(destination, DMChannel):
            perms = destination.permissions_for(destination.guild.me)
            if not perms.send_messages:
                log.error_before_message(destination=destination, author=self.user.name, content=content,
                                         error_message='No permissions to send message')
                return
            if embed and not perms.embed_links:
                log.error_before_message(destination=destination, author=self.user.name, content='<Embedded message>',
                                         error_message='No permissions to send embedded messages')
                m = 'Sorry, it seems I cannot send embedded messages in this channel...'
                return await self.send_message(destination, content=m)
            if file and not perms.attach_files:
                log.error_before_message(destination=destination, author=self.user.name, content='<File attached>',
                                         error_message='No permissions to send files')
                m = 'Sorry, it seems I cannot send files in this channel...'
                return await self.send_message(destination, content=m)

        # Send and log message
        m = await destination.send(content=content, tts=tts, embed=embed)
        if content:
            log.message(m)
        if file:
            log.message(m)
        if embed:
            log.message(m)
        return m

    @staticmethod
    def command_allowed_in(location_type: str, identifier: int, command_name: str):
        """
        Checks whether the issued command is allowed in the issued location
        :param location_type: either 'server' of 'channel'
        :param identifier: the id of the server or channel (depending on location_type)
        :param command_name: the name of the command issued
        :return: A boolean stating the command is allowed (True) or banned here (False)
        """
        return command_name == 'togglecommand' or not (
                banned_commands.get_banned_command(location_type, identifier, command_name)
                or banned_commands.get_banned_command(location_type, identifier, 'all'))

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

    async def pre_command(self, message: Message, channel: (TextChannel, DMChannel), command: str, is_typing=True,
                          delete_message=True,
                          cannot_be_private=False, must_be_private=False, must_be_nsfw=False, owner_check=False,
                          perm_needed=None):
        """
        This command should be run first in each command, substitutes the premade wrappers.
        :param message: The send message
        :param channel: The channel (DMChannel or TextChannel) the message was send in
        :param command: the command issued
        :param is_typing: Indicate whether to show the bot typing in the channel
        :param delete_message: Indicate whether to delete the message afterwards
        :param cannot_be_private: Indicate whether the command can be issued in a private channel
        :param must_be_private: Indicate whether the command must be issued in a private channel
        :param must_be_nsfw: Indicate whether the command can be issued outside of NSFW channels
        :param owner_check: Indicate whether the user must be a guild owner to issue the command
        :param perm_needed: Additional permission checks, the user must have at least one of these to issue the command
        :return:
        """
        # Check permissions
        if message.author.id not in [constants.KAPPAid, constants.NYAid]:
            if owner_check:
                await channel.send("Hahahaha, no")
                await log.message(message, 'Command "{}" used, but owner rights needed'.format(command))
                return False
            elif perm_needed:
                user_perms = [perm for perm, v in iter(channel.permissions_for(message.author)) if v]
                if not any(set(perm_needed).intersection(set(user_perms))):
                    await channel.send("Hahahaha, no")
                    m = 'Command "{}" used, but one of the perms \'{}\' needed'.format(command, ', '.join(perm_needed))
                    await log.message(message, m)
                    return False

        # Check whether the message can be send in this specific server and channel
        if isinstance(channel, DMChannel):
            if cannot_be_private:
                await channel.send('This command cannot be used in private channels')
                await log.message(message, 'Command "{}" used, but cannot be private'.format(command))
                return False
        else:
            channel: TextChannel
            if must_be_private:
                await channel.send('This command has to be used in a private conversation')
                await log.message(message, 'Command "{}" used, but must be private'.format(command))
                return False
            if must_be_nsfw and not channel.is_nsfw():
                await channel.send('This command cannot be used outside NSFW channels')
                await log.message(message, 'Command "{}" used, but must be an NSFW channel'.format(command))
                return False
            if not self.command_allowed_in_server(channel.guild.id, command):
                await log.message(message, 'Command "{}" used, but is serverbanned'.format(command))
                return False
            if not self.command_allowed_in_channel(channel.id, command):
                await log.message(message, 'Command "{}" used, but is channelbanned'.format(command))
                return False
            if delete_message and delete_commands.get_delete_commands(channel.guild.id):
                await self.delete_message(message)

        # Log and send the message
        log.message(message, type='Command \'{}\' used'.format(command))
        if is_typing:
            await channel.trigger_typing()
        command_counter.command_counter(command, message)
        return True
