import database.common as common
from discord import Message, Guild, TextChannel, DMChannel

GENERAL_DATABASE = 'general'
WELCOME_TABLE = 'welcome'
GOODBYE_TABLE = 'goodbye'
DO_NOT_DELETE_TABLE = 'delete_comm'
BANNED_COMMANDS_TABLE = 'banned_comm'
PREFIX_TABLE = 'prefix'
SELF_ASSIGNABLE_ROLES_TABLE = 'selfassignable'
COMMAND_COUNTER_TABLE = 'count_comm'
STARBOARD_CHANNEL_TABLE = 'starchannels'
STARBARD_MESSAGES_TABLE = 'starmessages'
SERVER_TABLE = 'servers'
CHANNEL_TABLE = 'channels'
MEMBER_COUTER_VOICECHANNEL_TABLE = 'membercountervc'

SERVER_ID = 'serverid'
USER_ID = 'userid'
CHANNEL_ID = 'channelid'
MESSAGE_ID = 'messageid'


def get_table(table):
    return common.get_table(GENERAL_DATABASE, table)
