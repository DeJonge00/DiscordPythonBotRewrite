from database.general.general import get_table, PREFIX_TABLE, SERVER_ID


def get_prefix(server_id: int):
    r = get_table(PREFIX_TABLE).find_one({SERVER_ID: server_id})
    return r.get('prefix') if r else None


def set_prefix(server_id: int, prefix: str):
    get_table(PREFIX_TABLE).update_one({SERVER_ID: server_id}, {'$set': {'prefix': prefix}}, upsert=True)
