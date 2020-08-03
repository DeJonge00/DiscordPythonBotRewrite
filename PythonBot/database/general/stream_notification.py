from database.general.general import (
    get_table,
    STREAMER_NOTIFICATIONS_TABLE,
    SERVER_ID,
    CHANNEL_ID,
    USER_ID,
)

USERS = "users"


def get_streamers(guild_id: int):
    r = get_table(STREAMER_NOTIFICATIONS_TABLE).find_one(
        {SERVER_ID: guild_id}, {USERS: 1}
    )
    return r.get(USERS, {}) if r else {}


def toggle_streamer(guild_id: int, channel_id: int, user_id: int) -> bool:
    us = get_streamers(guild_id).keys()
    if str(user_id) in us:
        if len(us) == 1:
            remove_all_streamers(guild_id)
            return False
        get_table(STREAMER_NOTIFICATIONS_TABLE).update_one(
            {SERVER_ID: guild_id}, {"$unset": {USERS + "." + str(user_id): 1}}
        )
        return False
    get_table(STREAMER_NOTIFICATIONS_TABLE).update_one(
        {SERVER_ID: guild_id},
        {"$set": {USERS + "." + str(user_id): channel_id}},
        upsert=True,
    )
    return True


def remove_all_streamers(guild_id: int):
    get_table(STREAMER_NOTIFICATIONS_TABLE).remove({SERVER_ID: guild_id})
