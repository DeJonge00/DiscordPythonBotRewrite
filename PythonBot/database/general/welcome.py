from database.general.general import get_table, SERVER_ID, CHANNEL_ID


def set_message(table: str, server_id: int, channel_id: int, message: str):
    get_table(table).update({SERVER_ID: str(server_id)}, {'$set': {CHANNEL_ID: str(channel_id), 'message': message}},
                            upsert=True)


def get_message(table: str, server_id: int):
    r = get_table(table).find_one({SERVER_ID: str(server_id)})
    if not r:
        return None, None
    return r.get('channelid', None), r.get('message', None)
