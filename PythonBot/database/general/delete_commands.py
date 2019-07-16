from database.general.general import get_table, SERVER_ID, DO_NOT_DELETE_TABLE


def get_delete_commands(server_id: str):
    r = get_table(DO_NOT_DELETE_TABLE).find_one({SERVER_ID: server_id})
    return r.get('delete_commands', True) if r else True


def set_delete_commands(server_id: str, state: bool):
    get_table(DO_NOT_DELETE_TABLE).update({SERVER_ID: server_id}, {'$set': {'delete_commands': state}}, upsert=True)


def toggle_delete_commands(server_id: [str]):
    v = not get_delete_commands(server_id)
    get_table(DO_NOT_DELETE_TABLE).update({SERVER_ID: server_id}, {'$set': {'delete_commands': v}}, upsert=True)
    return v
