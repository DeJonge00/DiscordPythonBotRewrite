import re

from database.general.general import get_table, SELF_ASSIGNABLE_ROLES_TABLE, SERVER_ID


def get_roles(server_id: int):
    r = get_table(SELF_ASSIGNABLE_ROLES_TABLE).find_one({SERVER_ID: str(server_id)})
    return (
        [int(i) for i in r.keys() if r[i] and re.match("\d\d\d\d\d\d+", i)] if r else []
    )


def get_role(server_id: int, role_id: int):
    r = get_table(SELF_ASSIGNABLE_ROLES_TABLE).find_one({SERVER_ID: str(server_id)})
    return r.get(str(role_id), False) if r else False


def toggle_role(server_id: int, role_id: int):
    v = not get_role(server_id, role_id)
    get_table(SELF_ASSIGNABLE_ROLES_TABLE).update_one(
        {SERVER_ID: str(server_id)}, {"$set": {str(role_id): v}}, upsert=True
    )
    return v
