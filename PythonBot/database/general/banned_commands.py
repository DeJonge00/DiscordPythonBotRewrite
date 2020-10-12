from database.general.general import (
    get_table,
    BANNED_COMMANDS_TABLE,
    WHITELIST_TABLE,
    SERVER_ID,
)


def get_banned_command(id_type: str, iden: int, command: str):
    r = get_table(BANNED_COMMANDS_TABLE).find_one({id_type: command})
    return r.get(str(iden), False) if r else False


def toggle_banned_command(id_type: str, iden: int, command: str):
    v = not get_banned_command(id_type, iden, command)
    get_table(BANNED_COMMANDS_TABLE).update_one(
        {id_type: command}, {"$set": {str(iden): v}}, upsert=True
    )
    return v


COMMAND = "command"
"""
{
    COMMAND: str,
    SERVER_ID: int
}
"""


def is_whitelisted(command: str, server_id: int):
    return bool(
        get_table(WHITELIST_TABLE).find_one({COMMAND: command, SERVER_ID: server_id})
    )


def toggle_whitelist(command: str, server_id: int):
    v = not is_whitelisted(command, server_id)
    if v:
        get_table(WHITELIST_TABLE).insert_one({COMMAND: command, SERVER_ID: server_id})
    else:
        get_table(WHITELIST_TABLE).delete_one({COMMAND: command, SERVER_ID: server_id})
    return v
