from database.general.general import get_table, PREFIX_TABLE, SERVER_ID


def get_prefix(server_id: int):
    r = get_table(PREFIX_TABLE).find_one({SERVER_ID: str(server_id)})
    return r.get('prefix') if r else None


def set_prefix(server_id: int, prefix: str):
    get_table(PREFIX_TABLE).update_one({SERVER_ID: str(server_id)}, {'$set': {'prefix': prefix}}, upsert=True)


def stringify_prefixes():
    r = get_table(PREFIX_TABLE).find({}, {SERVER_ID: 1, 'prefix': 1})
    for d in r:
        if isinstance(d.get(SERVER_ID), int):
            get_table(PREFIX_TABLE).delete_one({SERVER_ID: d.get(SERVER_ID)})
            set_prefix(d.get(SERVER_ID), d.get('prefix'))

