import asyncio
import logging
import re

from discord import Guild, Member, Embed

from config.constants import WELCOME_EMBED_COLOR, member_counter_message
from core import logging as log
from database.general import banned_commands, welcome, member_counter
from secret.secrets import LOG_LEVEL

logging.basicConfig(filename='logs/utils.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

REMOVE_JOIN_MESSAGE = False
REMOVE_LEAVE_MESSAGE = False


def get_cogs():
    return [
        'commands.admin',
        'commands.basic',
        'commands.config',
        'commands.image',
        'commands.lookup',
        'commands.misc',
        'commands.mod',
        'commands.games.hangman.commands',
        'commands.games.minesweeper.commands',
        'commands.games.trivia.trivia',
        'core.listeners'
    ]


def prep_str_for_print(s: str):
    return s.encode("ascii", "replace").decode("ascii")


def prep_str(s):
    """
    Strip text of weird characters
    :param s: The text
    :return: filtered text
    """
    return ''.join([l for l in s if re.match('[a-zA-Z0-9]', l)])


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


def command_allowed_in_server(server_id: int, command_name: str):
    split = command_name.split(' ')
    return command_allowed_in('server', server_id, command_name) and (
            len(split) <= 1 or command_allowed_in('server', server_id, split[0]))


def command_allowed_in_channel(channel_id: int, command_name: str):
    split = command_name.split(' ')
    return command_allowed_in('channel', channel_id, command_name) and (
            len(split) <= 1 or command_allowed_in('channel', channel_id, split[0]))


async def on_member_message(guild: Guild, member: Member, func_name, text, do_log=True) -> bool:
    if do_log:
        log.announcement(guild_name=guild.name, announcement_text='Member {} just {}'.format(member, text))
    channel, mes = welcome.get_message(func_name, guild.id)
    if not channel or not mes:
        return False
    embed = Embed(colour=WELCOME_EMBED_COLOR)
    embed.add_field(name="User {}!".format(text), value=prep_str_for_print(mes.format(member.mention)))
    embed.set_footer(text='Display name: ' + prep_str_for_print(member.display_name))
    channel = guild.get_channel(channel)
    if not channel:
        return False
    m = await channel.send(embed=embed)
    if REMOVE_JOIN_MESSAGE:
        await asyncio.sleep(30)
        await m.delete()
    return True


async def update_member_counter(guild: Guild):
    channel_id = member_counter.get_member_counter_channel(guild.id)
    if not channel_id:
        return
    # channel: VoiceChannel
    channel = guild.get_channel(channel_id)
    if not channel:
        member_counter.delete_member_counter_channel(guild.id)
        return
    await channel.edit(name=member_counter_message.format(guild.member_count), reason='User left/joined')
