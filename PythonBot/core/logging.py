import datetime
from discord.abc import GuildChannel
from discord import Message, TextChannel, Guild, User
from config.constants import bot_list_servers


def str_cmd(s: str):
    return s.encode("ascii", "replace").decode("ascii")


async def error(event, filename="errors", serverid=None):
    if serverid in bot_list_servers:
        return
    text = datetime.datetime.utcnow().strftime("%H:%M:%S") + " | " + str_cmd(event)
    file = open("logs/" + str_cmd(filename.replace('/', '')) + ".txt", "a+")
    file.write(text + '\n')
    file.close()
    print(text)


async def log(note: str, author: str, string: str, filename: str):
    file = open("logs/" + str_cmd(filename.replace('/', '')) + ".txt", "a+")
    text = "{} | {} | {} : {}".format(datetime.datetime.utcnow().strftime("%H:%M:%S"), str_cmd(note), str_cmd(author),
                                      str_cmd(string))
    file.write(text + "\n")
    print(text)


async def message(mess: Message, action: str):
    await message_content(mess.content, mess.channel, mess.guild, mess.author, mess.created_at, mess.raw_mentions,
                          action)


async def message_content(content: str, channel: GuildChannel, server: Guild, author: User,
                          timestamp: Message.created_at, raw_mentions: list, action: str):
    # True if not a direct message
    public = isinstance(channel, TextChannel)
    if public and server.id in bot_list_servers:
        return
    if not public:
        servername = 'direct message'
        channelname = '-'
    else:
        servername = server.name
        channelname = str(channel)
    file = open("logs/" + str_cmd(servername.replace('/', '')) + ".txt", "a+")
    if action == "pic":
        text = "{} | {} | {} | {} posted a pic".format(timestamp.strftime("%H:%M:%S"), str_cmd(servername),
                                                           str_cmd(channelname), str_cmd(str(author)))
    else:
        cont = content
        if public:
            members = list(map(server.get_member, raw_mentions))
            for user in members:
                try:
                    cont = cont.replace(user.mention, "@" + user.name)
                except AttributeError:
                    pass
        text = "{} | {} | {} | {} | {} : {}".format(timestamp.strftime("%H:%M:%S"), str_cmd(servername),
                                                    str_cmd(channelname), str_cmd(str(author)), action, str_cmd(cont))
    file.write(text + "\n")
    print(text)
    file.close()
