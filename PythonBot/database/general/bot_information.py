from discord import Guild, TextChannel, VoiceChannel

from database.general.general import get_table, SERVER_ID, CHANNEL_ID, SERVER_TABLE, CHANNEL_TABLE

NAME = 'name'
MEMBERS = 'members'
BOTS = 'bots'
ICON = 'icon'
CHANNELS = 'channels'
TEXT_CHANNEL = 'text'
VOICE_CHANNEL = 'voice'
CHANNEL_TYPE = 'type'


def server_as_dict(s: Guild):
    try:
        member_count = s.member_count
    except AttributeError:
        member_count = 0
    return {
        NAME: s.name,
        SERVER_ID: str(s.id),
        MEMBERS: member_count,
        BOTS: len([x for x in s.members if x.bot]),
        ICON: str(s.icon_url),
        CHANNELS: {
            TEXT_CHANNEL: [str(c.id) for c in s.channels if isinstance(c, TextChannel)],
            VOICE_CHANNEL: [str(c.id) for c in s.channels if isinstance(c, VoiceChannel)]
        }
    }


def channel_as_dict(c: TextChannel):
    channel_type = TEXT_CHANNEL if isinstance(c, TextChannel) else VOICE_CHANNEL
    return {
        NAME: c.name,
        CHANNEL_ID: str(c.id),
        CHANNEL_TYPE: channel_type
    }


def update_channel(channel: TextChannel, channel_table=None):
    if not channel_table:
        channel_table = get_table(CHANNEL_TABLE)
    channel_table.replace_one({CHANNEL_ID: str(channel.id)}, channel_as_dict(channel), upsert=True)


def update_server(server: Guild, server_table=None, channel_table=None):
    if not server_table:
        server_table = get_table(SERVER_TABLE)
    if not channel_table:
        channel_table = get_table(CHANNEL_TABLE)
    server_table.replace_one({SERVER_ID: str(server.id)}, server_as_dict(server), upsert=True)
    for c in server.channels:
        update_channel(c, channel_table=channel_table)


def remove_server(server: Guild):
    server_table = get_table(SERVER_TABLE)
    server_table.remove({SERVER_ID: str(server.id)})


def update_server_member_count(server: Guild, server_table=None):
    if not server_table:
        server_table = get_table(SERVER_TABLE)
    server_table.update_one({SERVER_ID: str(server.id)}, {'$set': {MEMBERS: server.member_count}})


def update_server_list(servers: [Guild]):
    server_table, channel_table = get_table(SERVER_TABLE), get_table(CHANNEL_TABLE)
    for s in servers:
        update_server(s, server_table=server_table, channel_table=channel_table)


def clear_server_list():
    get_table(SERVER_TABLE).remove({})
    get_table(CHANNEL_TABLE).remove({})
