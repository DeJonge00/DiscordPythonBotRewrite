from database.dnd.dnd import get_table, SUBCLASS_TABLE
from database.dnd.dndclass import get_classes


def fill_subclasses():
    subclasses = [
        {'id': 1, 'name': 'Alchemist', 'short_desc': 'Short description', 'source': 1, 'class': 1,
         'long_desc': 'Long description of the subclass, including where it comes from or who practices it most'},
        {'id': 2, 'name': 'Boomboom', 'short_desc': 'Short description', 'source': 2, 'class': 2,
         'long_desc': 'Long description of the subclass, including where it comes from or who practices it most'}
    ]
    get_table(SUBCLASS_TABLE).insert_many(subclasses)


def get_subclasses(source='all'):
    f = {} if source == 'all' else {'source': {'$in': source}}
    table = get_table(SUBCLASS_TABLE)
    subclasses = {}
    for c, i in [(c.get('name'), c.get('id')) for c in get_classes(source) if c.get('source') in source]:
        f['class'] = i
        r = list(table.find(f, {'_id': 0}))
        subclasses[c] = sorted(r, key=lambda l: l.get('name')) if r else []
    return subclasses
