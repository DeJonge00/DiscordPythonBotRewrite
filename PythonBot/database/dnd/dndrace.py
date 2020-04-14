from database.dnd.dnd import get_table, RACE_TABLE


def fill_races():
    races = [
        {'id': 1, 'name': 'Aarakocra', 'source': 1, 'race': 1},
        {'id': 2, 'name': 'Aasimar', 'source': 2, 'race': 3},
        {'id': 3, 'name': 'Bugbear', 'source': 3, 'race': 1},
        {'id': 4, 'name': 'Changeling', 'source': 3, 'race': 2},
        {'id': 5, 'name': 'Dragonborn', 'short_desc': 'short description', 'long_desc': 'Long description',
         'source': 1, 'race': 2},
    ]
    get_table(RACE_TABLE).insert_many(races)


def get_races(source='all'):
    f = {} if source == 'all' else {'source': {'$in': source}}
    r = list(get_table(RACE_TABLE).find(f, {'_id': 0}))
    return sorted(r, key=lambda l: l.get('name')) if r else []
