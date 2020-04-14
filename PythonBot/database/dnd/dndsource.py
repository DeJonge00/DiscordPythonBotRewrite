from database.dnd.dnd import get_table, SOURCE_TABLE


def fill_sources():
    sources = [
        {'id': 1, 'name': 'Player Handbook', 'shortname': 'PHB', 'enabled': True},
        {'id': 2, 'name': 'Dungeon Master\'s Guide', 'shortname': 'DMG', 'enabled': True},
        {'id': 3, 'name': 'Xanathar\'s Guide To Everything', 'shortname': 'XGtE', 'enabled': False}
    ]
    get_table(SOURCE_TABLE).insert_many(sources)


def get_sources():
    s = list(get_table(SOURCE_TABLE).find({}, {'_id': 0}))
    return sorted(s, key=lambda l: l.get('name')) if s else []
