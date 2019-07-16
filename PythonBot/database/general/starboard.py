from database.general.general import get_table, SERVER_ID, CHANNEL_ID, STARBOARD_CHANNEL_TABLE, STARBARD_MESSAGES_TABLE, \
    MESSAGE_ID


def set_star_channel(server_id: int, channel_id: int):
    table = get_table(STARBOARD_CHANNEL_TABLE)
    table.update({SERVER_ID: server_id}, {'$set': {CHANNEL_ID: channel_id}}, upsert=True)


def delete_star_channel(server_id: int):
    table = get_table(STARBOARD_CHANNEL_TABLE)
    table.delete_one({SERVER_ID: server_id})


def get_star_channel(server_id: int):
    r = get_table(STARBOARD_CHANNEL_TABLE).find_one({SERVER_ID: server_id})
    if not r:
        print("Starboard channel not specified for server")
        return None
    return int(r.get(CHANNEL_ID)) if r else None


def get_star_message(message_id: str):
    r = get_table(STARBARD_MESSAGES_TABLE).find_one({MESSAGE_ID: message_id}, {'embed_id': 1})
    return r.get('embed_id') if r else None


def update_star_message(message_id: str, embed_id: str):
    get_table(STARBARD_MESSAGES_TABLE).update_one({MESSAGE_ID: message_id}, {'$set': {'embed_id': embed_id}},
                                                  upsert=True)
