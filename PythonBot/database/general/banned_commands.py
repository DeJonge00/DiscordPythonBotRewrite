from database.general.general import get_table, BANNED_COMMANDS_TABLE


def get_banned_command(id_type: str, iden: int, command: str):
    r = get_table(BANNED_COMMANDS_TABLE).find_one({id_type: command})
    return r.get(str(iden), False) if r else False


def toggle_banned_command(id_type: str, iden: int, command: str):
    v = not get_banned_command(id_type, iden, command)
    get_table(BANNED_COMMANDS_TABLE).update_one(
        {id_type: command}, {"$set": {str(iden): v}}, upsert=True
    )
    return v
