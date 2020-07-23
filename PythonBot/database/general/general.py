import database.common as common

GENERAL_DATABASE = "general"
WELCOME_TABLE = "welcome"
GOODBYE_TABLE = "goodbye"
DO_NOT_DELETE_TABLE = "delete_comm"
BANNED_COMMANDS_TABLE = "banned_comm"
PREFIX_TABLE = "prefix"
SELF_ASSIGNABLE_ROLES_TABLE = "selfassignable"
COMMAND_COUNTER_TABLE = "count_comm"
STARBOARD_CHANNEL_TABLE = "starchannels"
STARBARD_MESSAGES_TABLE = "starmessages"
SERVER_TABLE = "servers"
CHANNEL_TABLE = "channels"
MEMBER_COUTER_VOICECHANNEL_TABLE = "membercountervc"
AUTO_VOICE_CHANNEL_TABLE = "auto_voice_channel"
STREAMER_NOTIFICATIONS_TABLE = "streamer_notifications"

SERVER_ID = "serverid"
USER_ID = "userid"
CHANNEL_ID = "channelid"
MESSAGE_ID = "messageid"

ASC = 1
DESC = -1


def get_table(table):
    return common.get_table(GENERAL_DATABASE, table)


def get_server(server_id: int):
    return get_table(SERVER_TABLE).find_one({SERVER_ID: str(server_id)}, {"_id": 0})


def get_server_list():
    return list(
        get_table(SERVER_TABLE).find({}, {"_id": 0}).sort("members", DESC).limit(1000)
    )
