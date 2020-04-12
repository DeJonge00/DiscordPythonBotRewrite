from database.general.general import get_table, MEMBER_COUTER_VOICECHANNEL_TABLE, SERVER_ID, CHANNEL_ID


def get_member_counter_channel(guild_id: int):
    result = get_table(MEMBER_COUTER_VOICECHANNEL_TABLE).find_one({SERVER_ID: str(guild_id)})
    return int(result.get(CHANNEL_ID)) if result else None


def set_member_counter_channel(guild_id: int, channel_id: int):
    get_table(MEMBER_COUTER_VOICECHANNEL_TABLE)\
        .update_one({SERVER_ID: str(guild_id)}, {'$set': {CHANNEL_ID: str(channel_id)}}, upsert=True)


def delete_member_counter_channel(guild_id: int):
    get_table(MEMBER_COUTER_VOICECHANNEL_TABLE).delete_one({SERVER_ID: str(guild_id)})
