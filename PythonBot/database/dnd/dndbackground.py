from database.dnd.dnd import get_table, BACKGROUND_TABLE


def fill_backgrounds():
    backgrounds = [
        {'id': 1, 'name': 'Anthropologist', 'source': 2},
        {'id': 2, 'name': 'Archaeologist', 'source': 1},
        {'id': 3, 'name': 'Azorius Functionary', 'source': 1}
    ]
    get_table(BACKGROUND_TABLE).insert_many(backgrounds)


def get_backgrounds(source='all'):
    f = {} if source == 'all' else {'source': {'$in': source}}
    r = list(get_table(BACKGROUND_TABLE).find(f, {'_id': 0}))
    return sorted(r, key=lambda l: l.get('name')) if r else []


def get_background(filter):
    r = get_table(BACKGROUND_TABLE).find_one(filter, {'_id': 0})
    return dict(r) if r else {}
