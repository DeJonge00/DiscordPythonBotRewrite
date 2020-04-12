from database.common import get_table

PAT_DATABASE = 'pats'
PAT_TABLE = 'pats'


# Returns current pat amount
def increment_pats(patter_id: int, pattee_id: int):
    table = get_table(PAT_DATABASE, PAT_TABLE)
    table.update_one({'patter': str(patter_id), 'pattee': str(pattee_id)}, {'$inc': {'pats': 1}}, upsert=True)
    return table.find({'patter': str(patter_id), 'pattee': str(pattee_id)})[0].get('pats')
