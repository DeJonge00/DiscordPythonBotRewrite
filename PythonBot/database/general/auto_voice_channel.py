from database.general.general import get_table, SERVER_ID, CHANNEL_ID, AUTO_VOICE_CHANNEL_TABLE

JOINER = 'joiner'
CREATED = 'created'


def set_channel(channel_type: str, guild_id: int, channel_id: int, status: bool):
    table = get_table(AUTO_VOICE_CHANNEL_TABLE)
    if status:
        table.update_one({SERVER_ID: guild_id}, {'$set': {str(channel_id): channel_type}}, upsert=True)
        return
    table.update_one({SERVER_ID: guild_id}, {'$unset': {str(channel_id): None}}, upsert=True)


def get_channel(channel_type: str, guild_id: int):
    r = get_table(AUTO_VOICE_CHANNEL_TABLE).find_one({SERVER_ID: guild_id})
    return [int(k) for k, v in r.items() if v == channel_type] if r else []


def get_joiner_channels(guild_id: int):
    return get_channel(JOINER, guild_id)


def set_joiner_channel(guild_id: int, channel_id: int, status: bool = True):
    set_channel(JOINER, guild_id, channel_id, status)


def get_created_channels(guild_id: int):
    return get_channel(CREATED, guild_id)


def set_created_channel(guild_id: int, channel_id: int, status: bool = True):
    set_channel(CREATED, guild_id, channel_id, status)
