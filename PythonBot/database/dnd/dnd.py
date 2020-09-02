import database.common as common

RPG_DND_DATABASE = "rpgdnd"

SOURCE_TABLE = "sources"
RACE_TABLE = "playableraces"
CLASS_TABLE = "playableclasses"
SUBRACE_TABLE = "playablesubraces"
SUBCLASS_TABLE = "playablesubclasses"
BACKGROUND_TABLE = "backgrounds"

ASC = 1
DESC = -1


def get_table(table):
    return common.get_table(RPG_DND_DATABASE, table)


def reset_database():
    get_table(SOURCE_TABLE).delete_many({})
    get_table(RACE_TABLE).delete_many({})
    get_table(SUBRACE_TABLE).delete_many({})
    get_table(CLASS_TABLE).delete_many({})
    get_table(SUBCLASS_TABLE).delete_many({})
    get_table(BACKGROUND_TABLE).delete_many({})


def fill_database():
    from database.dnd.dndsource import fill_sources
    from database.dnd.dndrace import fill_races
    from database.dnd.dndsubrace import fill_subraces
    from database.dnd.dndclass import fill_classes
    from database.dnd.dndsubclass import fill_subclasses
    from database.dnd.dndbackground import fill_backgrounds

    fill_sources()
    fill_races()
    fill_subraces()
    fill_classes()
    fill_subclasses()
    fill_backgrounds()


def get_all(table: str, filter):
    r = get_table(table).find_one(filter, {"_id": 0})
    return dict(r) if r else {}


def get_all_by_name(table: str, name: str):
    return get_all(table, {"name": name})


def get_all_by_id(table: str, id: int):
    return get_all(table, {"id": id})


def get_highest_id(table):
    return (
        int(list(table.find({}, {"id": 1}).sort("id", DESC).limit(1))[0].get("id"))
        if id
        else 0
    )


def create_all(table: str, options: dict):
    table = get_table(table)
    try:
        id = options["id"]
    except (TypeError, ValueError, KeyError):
        id = get_highest_id(table) + 1
    table.update_one({"id": id}, {"$set": options}, upsert=True)


if __name__ == "__main__":
    reset_database()
    fill_database()
