from database.general.general import get_table, COMMAND_COUNTER_TABLE, DESC

from discord import Message, DMChannel


def command_counter(name: str, message: Message):
    if message.guild:
        server = str(message.guild)
    else:
        server = "Direct Message"
    channel_name = (
        str(message.channel)
        if isinstance(message.channel, DMChannel)
        else message.channel.name
    )
    get_table(COMMAND_COUNTER_TABLE).insert_one(
        {
            "command": name,
            "timestamp": message.created_at.timestamp(),
            "server": server,
            "channel": channel_name,
            "author": message.author.name,
        }
    )


def get_command_counters(start_time: float):
    return (
        get_table(COMMAND_COUNTER_TABLE)
        .find({"timestamp": {"$gt": start_time}}, {"_id": 0})
        .sort("timestamp", DESC)
        .limit(1000)
    )
