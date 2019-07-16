from database.rpg import get_table, RPG_CHANNEL_TABLE, SERVER_ID, CHANNEL_ID


def set_rpg_channel(server_id: str, channel_id: str):
    table = get_table(RPG_CHANNEL_TABLE)
    table.update({SERVER_ID: server_id}, {'$set': {CHANNEL_ID: channel_id}}, upsert=True)


def get_rpg_channel(server_id: str):
    r = get_table(RPG_CHANNEL_TABLE).find_one({SERVER_ID: server_id})
    if not r:
        print("Channel not specified for server")
        return None
    return r.get(CHANNEL_ID)
