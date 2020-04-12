import pymongo

import api.rpg.constants as rpgc
from api.rpg.objects.rpgplayer import dict_to_player, BUSY_DESC_BOSSRAID, BUSY_DESC_NONE
from database.common import get_table as get_database_and_table

RPG_DATABASE = 'rpg'
CHANNEL_ID = 'channelid'
SERVER_ID = 'serverid'
USER_ID = 'userid'

RPG_CHANNEL_TABLE = 'rpg_channel'
RPG_PLAYER_TABLE = 'rpg_player'
RPG_KING_TABLE = 'rpg_king'


def get_table(table):
    return get_database_and_table(RPG_DATABASE, table)


def get_busy_players():
    return [(x.get('stats').get('name'), int(x.get('userid')), x.get('picture_url'), {
        'time': x.get('busy').get('time'),
        'channel': int(x.get('busy').get('channel')),
        'description': x.get('busy').get('description')
    }, x.get('stats')
             .get('health')) for x in get_table(RPG_PLAYER_TABLE).find({"$or": [{'busy.time': {'$lt': 0}},
                                                                                {'busy.description': {
                                                                                    '$not': {'$eq': 0}}}]})]


def decrement_busy_counters():
    get_table(RPG_PLAYER_TABLE).update_many({'busy.description': {'$not': {'$eq': BUSY_DESC_NONE}}},
                                            {'$inc': {'busy.time': -1}})


def do_health_regen():
    t = get_table(RPG_PLAYER_TABLE)
    r = t.find({})
    if not r:
        return
    for player in r:
        player = dict_to_player(player)
        if player.get_health() < player.get_max_health():
            if player.busydescription == BUSY_DESC_NONE:
                percentage = 0.025 if player.role == rpgc.names.get('role')[4][0] else 0.01
            else:
                percentage = 0.05 if player.role == rpgc.names.get('role')[4][0] else 0.03
            health = min(player.get_max_health(), int(player.get_health() + player.get_max_health() * percentage))
            t.update({USER_ID: str(player.userid)}, {'$set': {'stats.health': health}})


def get_top_players(group: str, start: int, amount: int):
    ps = get_table(RPG_PLAYER_TABLE).find().sort(group, pymongo.DESCENDING).skip(start).limit(amount)
    return [(x.get('stats').get('name'), x.get(group)) for x in ps]


def get_boss_parties():
    r = get_table(RPG_PLAYER_TABLE).find({'busy.description': BUSY_DESC_BOSSRAID})
    res = {}
    for item in [dict_to_player(x) for x in r]:
        res.setdefault(item.busychannel, []).append(item)
    return res


def set_king(user_id: int, server_id: int):
    get_table(RPG_KING_TABLE).update({SERVER_ID: str(server_id)}, {'$set': {USER_ID: str(user_id)}}, upsert=True)


def get_king(server_id: int):
    r = get_table(RPG_KING_TABLE).find_one({SERVER_ID: str(server_id)})
    return r if r else None


def is_king(user_id: int):
    return bool(get_table(RPG_KING_TABLE).find_one({USER_ID: str(user_id)}))
