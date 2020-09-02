from datetime import datetime

from discord import Message, TextChannel, DMChannel
from discord.abc import Messageable


def str_cmd(s: str):
    return s.encode("ascii", "replace").decode("ascii")


def fill_logging_template(
    guild: str, channel: str, author: str, type: str, content: str
):
    time = datetime.utcnow()
    text = str(time) + " | {guild} | {channel} | {author} | {type} : {content}"
    return text.format(
        guild=str_cmd(guild),
        channel=str_cmd(channel),
        author=str_cmd(author),
        type=str_cmd(type),
        content=str_cmd(content),
    )


def fill_announcement_template(guild: str, announcement_text: str):
    time = datetime.utcnow()
    text = str(time) + " | {guild} | announcement : {announcement_text}"
    return text.format(
        guild=str_cmd(guild), announcement_text=str_cmd(announcement_text)
    )


def log_and_print(filename: str, message: str):
    with open("logs/" + str_cmd(filename.replace("/", "")) + ".txt", "a+") as file:
        file.write(message + "\n")
    print(message)


def get_channel_and_guild_names(channel: Messageable):
    """
    :param channel: The channel in which the logged message will be or was send
    :return: (guild_name, channel_name) to be used in logging
    """
    return (
        ("DM" if isinstance(channel, DMChannel) else str_cmd(channel.guild.name)),
        str_cmd(str(channel)),
    )


def announcement(guild_name: str, announcement_text: str):
    log_and_print(guild_name, fill_announcement_template(guild_name, announcement_text))


def error_on_message(m: Message, error_message: str):
    """
    Log an error caused by a single message the client received (ie: issueing a command without permissions)
    :param m: The message that caused the error
    :param error_message: The error the message caused, formatted to be read by log readers
    """
    guild_name, channel_name = get_channel_and_guild_names(m.channel)
    log_and_print(
        "errors",
        fill_logging_template(
            guild=guild_name,
            channel=channel_name,
            author=str(m.author),
            type="Error: " + error_message,
            content=m.clean_content,
        ),
    )


def error_before_message(
    destination: TextChannel, author: str, content: str, error_message: str
):
    """
    Log an error created before a message was send (ie: missing permissions)
    :param destination: The destination of the message
    :param author: The author of the message (the bot user)
    :param content: The content of the message
    :param error_message: The error, formatter to be read by log readers
    """
    guild_name, channel_name = get_channel_and_guild_names(destination)
    log_and_print(
        "errors",
        fill_logging_template(
            guild=guild_name,
            channel=channel_name,
            author=str(author),
            type="Error: " + error_message,
            content=content,
        ),
    )


def message(m: Message, type="Send message"):
    """
    Log a single message in both the terminal and a file named after the guild it was send in
    :param m: The message to be logged
    :param type: The type of action to be logged (ie: send message/edit message/delete message)
    """
    guild_name, channel_name = get_channel_and_guild_names(m.channel)
    if m.content:
        message_content(m, guild_name, channel_name, type)
    if m.embeds:
        embedded_message(m, guild_name, channel_name, type)
    if m.attachments:
        attachment_message(m, guild_name, channel_name)


def message_content(m: Message, guild_name: str, channel_name: str, type: str):
    log_and_print(
        guild_name,
        fill_logging_template(
            guild=guild_name,
            channel=channel_name,
            author=str(m.author),
            type=type,
            content=m.clean_content,
        ),
    )


def embedded_message(m: Message, guild_name: str, channel_name: str, type: str):
    title = (
        m.embeds[0].author.name
        if m.embeds[0].author.name
        else (m.embeds[0].fields[0].name if m.embeds[0].fields[0] else m.color)
    )
    log_and_print(
        guild_name,
        fill_logging_template(
            guild=guild_name,
            channel=channel_name,
            author=str(m.author),
            type=type,
            content="Embed: {}".format(title),
        ),
    )


def attachment_message(m: Message, guild_name: str, channel_name: str):
    content = "".join(["\n{}".format(a.url) for a in m.attachments])
    log_and_print(
        guild_name,
        fill_logging_template(
            guild=guild_name,
            channel=channel_name,
            author=str(m.author),
            type="A message included the files:",
            content=content,
        ),
    )
