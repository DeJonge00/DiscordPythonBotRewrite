from api.rpg.objects.rpgplayer import RPGPlayer, dict_to_player
from database.rpg.rpg_main import get_table, RPG_PLAYER_TABLE, USER_ID, BUSY_DESC_NONE


def get_player(player_id: int, player_name: str, picture_url: str):
    r = list(get_table(RPG_PLAYER_TABLE).find({USER_ID: str(player_id)}))
    return (
        dict_to_player(r[0])
        if r
        else RPGPlayer(userid=player_id, picture_url=picture_url, username=player_name)
    )


def update_player(player: RPGPlayer):
    get_table(RPG_PLAYER_TABLE).replace_one(
        {USER_ID: str(player.userid)}, player.as_dict(), upsert=True
    )


def reset_busy(user_id: int):
    set_busy(user_id, 0, "", BUSY_DESC_NONE)


def set_busy(user_id: int, time: int, channel_id: int, description: str):
    get_table(RPG_PLAYER_TABLE).update(
        {USER_ID: str(user_id)},
        {
            "$set": {
                "busy": {
                    "time": time,
                    "channel": str(channel_id),
                    "description": description,
                }
            }
        },
    )


def add_stats(player_id: int, stat: str, amount: int):
    get_table(RPG_PLAYER_TABLE).update(
        {USER_ID: str(player_id)}, {"$inc": {stat: amount}}
    )


def add_pet_stats(player_id: int, stat: str, amount: int):
    for x in range(
        len(
            list(get_table(RPG_PLAYER_TABLE).find({USER_ID: str(player_id)}))[0].get(
                "pets", []
            )
        )
    ):
        get_table(RPG_PLAYER_TABLE).update(
            {USER_ID: str(player_id)}, {"$inc": {"pets.{}.{}".format(x, stat): amount}}
        )


def set_stat(player_id: int, stat: str, value):
    get_table(RPG_PLAYER_TABLE).update_one(
        {USER_ID: str(player_id)}, {"$set": {stat: value}}
    )


def set_picture(player_id: int, url: str):
    set_stat(player_id, "stats.picture_url", url)


def set_name(player_id: int, name: str):
    set_stat(player_id, "stats.name", name)


def set_kingtimer(player_id: int, time: float):
    set_stat(player_id, "kingtimer", time)


def set_health(player_id: int, hp: int):
    set_stat(player_id, "stats.health", hp)
