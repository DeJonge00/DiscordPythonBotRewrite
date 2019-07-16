from database.rpg import get_table, RPG_PLAYER_TABLE, USER_ID


def get_player(player_id: str, player_name: str, picture_url: str):
    r = list(get_table(RPG_PLAYER_TABLE).find({USER_ID: player_id}))
    return dict_to_player(r[0]) if r else RPGPlayer(userid=player_id, picture_url=picture_url, username=player_name)


def update_player(player: RPGPlayer):
    get_table(RPG_PLAYER_TABLE).replace_one({USER_ID: player.userid}, player.as_dict(), upsert=True)


def reset_busy(user_id: str):
    set_busy(user_id, 0, '', BUSY_DESC_NONE)


def set_busy(user_id: str, time: int, channel: str, description: str):
    get_table(RPG_PLAYER_TABLE).update(
        {USER_ID: user_id},
        {'$set':
            {'busy':
                {
                    'time': time,
                    'channel': channel,
                    'description': description
                }}})


def add_stats(playerid: str, stat: str, amount: int):
    get_table(RPG_PLAYER_TABLE).update({USER_ID: playerid}, {'$inc': {stat: amount}})


def add_pet_stats(playerid: str, stat: str, amount: int):
    for x in range(len(list(get_table(RPG_PLAYER_TABLE).find({USER_ID: playerid}))[0].get('pets', []))):
        get_table(RPG_PLAYER_TABLE).update({USER_ID: playerid}, {'$inc': {'pets.{}.{}'.format(x, stat): amount}})


def set_stat(player_id: str, stat: str, value):
    get_table(RPG_PLAYER_TABLE).update_one({USER_ID: player_id}, {'$set': {stat: value}})


def set_picture(player_id: str, url: str):
    set_stat(player_id, 'stats.picture_url', url)


def set_name(player_id: str, name: str):
    set_stat(player_id, 'stats.name', name)


def set_kingtimer(player_id: str, time: float):
    set_stat(player_id, 'kingtimer', time)


def set_health(player_id: str, hp: int):
    set_stat(player_id, 'stats.health', hp)
