from database.dnd.dnd import get_table, CLASS_TABLE


def fill_classes():
    classes = [
        {'id': 1, 'name': 'Artificer', 'short_desc': '', 'long_desc': 'Long description', 'source': 3},
        {'id': 2, 'name': 'Barbarian', 'short_desc': '', 'long_desc': '', 'source': 1},
        {'id': 3, 'name': 'Bard', 'short_desc': '', 'long_desc': '', 'source': 1},
        {'id': 4, 'name': 'Cleric', 'short_desc': '', 'long_desc': '', 'source': 2}
    ]
    get_table(CLASS_TABLE).insert_many(classes)


def get_classes(source='all'):
    f = {} if source == 'all' else {'source': {'$in': source}}
    r = list(get_table(CLASS_TABLE).find(f, {'_id': 0}))
    return sorted(r, key=lambda l: l.get('name')) if r else []
