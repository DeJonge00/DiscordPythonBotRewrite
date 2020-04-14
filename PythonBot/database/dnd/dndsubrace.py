from database.dnd.dnd import get_table, SUBRACE_TABLE
from database.dnd.dndrace import get_races


def fill_subraces():
    subclasses = [
        {'id': 1, 'name': 'Racism', 'short_desc': 'Short description', 'source': 1, 'race': 2,
         'long_desc': 'Long description of the subclass, including where it comes from or who practices it most'}
    ]
    get_table(SUBRACE_TABLE).insert_many(subclasses)


def get_subraces(source='all'):
    f = {} if source == 'all' else {'source': {'$in': source}}
    table = get_table(SUBRACE_TABLE)
    subclasses = {}
    for c, i in [(c.get('name'), c.get('id')) for c in get_races(source) if c.get('source') in source]:
        f['race'] = i
        r = list(table.find(f, {'_id': 0}))
        subclasses[c] = sorted(r, key=lambda l: l.get('name')) if r else []
    return subclasses
