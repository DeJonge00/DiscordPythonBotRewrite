from database.general.general import get_table, SERVER_ID, CHANNEL_ID, SERVER_TABLE, CHANNEL_TABLE

from discord import Guild, TextChannel, DMChannel


def server_as_dict(s: Guild):
    try:
        member_count = s.member_count
    except AttributeError:
        member_count = 0
    return {
        'name': s.name,
        SERVER_ID: s.id,
        'members': member_count,
        'bots': len([x for x in s.members if x.bot]),
        'icon': str(s.icon_url),
        'channels': {
            'text': [str(c.id) for c in s.channels if isinstance(c, TextChannel)],
            'voice': [str(c.id) for c in s.channels if isinstance(c, DMChannel)]
        }
    }


def channel_as_dict(c: TextChannel):
    channel_type = 'text' if isinstance(c, TextChannel) else 'voice'
    return {
        'name': c.name,
        CHANNEL_ID: str(c.id),
        'type': channel_type
    }


def update_server_list(servers: [Guild]):
    server_table = get_table(SERVER_TABLE)
    channel_table = get_table(CHANNEL_TABLE)
    for s in servers:
        server_table.replace_one({SERVER_ID: str(s.id)}, server_as_dict(s), upsert=True)
        for c in s.channels:
            channel_table.replace_one({CHANNEL_ID: str(c.id)}, channel_as_dict(c), upsert=True)
