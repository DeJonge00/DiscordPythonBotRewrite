from database.rpg.rpg_main import get_table, RPG_CHANNEL_TABLE, SERVER_ID, CHANNEL_ID


def set_rpg_channel(server_id: int, channel_id: int):
    table = get_table(RPG_CHANNEL_TABLE)
    table.update({SERVER_ID: str(server_id)}, {'$set': {CHANNEL_ID: str(channel_id)}}, upsert=True)


def get_rpg_channel(server_id: int):
    r = get_table(RPG_CHANNEL_TABLE).find_one({SERVER_ID: str(server_id)})
    if not r:
        print("Channel not specified for server")
        return None
    return r.get(CHANNEL_ID)
