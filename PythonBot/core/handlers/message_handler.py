import logging
import random
import string
from datetime import timedelta, datetime

from discord import Message, Member, Reaction, Forbidden, NoMoreItems, Embed, DMChannel, File

from config import constants, command_text
from config.image_links import praise_the_sun
from config.constants import TEXT, EMBED, IMAGE, ACTION, STAR_EMBED_COLOR, STAR_EMOJI
from core import logging as log
from core.bot import PythonBot
from commands.image import embedded_pic
from database.general.starboard import get_star_channel, get_star_message, update_star_message
from secret.secrets import LOG_LEVEL
from secret.secrets import bot_names

logging.basicConfig(filename='logs/message_handlers.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


def cl(x):
    return x.lower() if random.randint(0, 1) <= 0 else x.capitalize()


async def new_message(bot: PythonBot, message: Message):
    """
    Interact with received messages, even if no command was issued.
    :param bot: The bot (needed to log messages and pre_command).
    :param message: The message received.
    :return: Whether a response was send.
    """
    is_private = isinstance(message.channel, DMChannel)

    if is_private:
        guild_id = perms = None
    else:
        perms = message.channel.permissions_for(message.guild.me)
        if not (perms.manage_messages or perms.attach_files):
            return False
        guild_id = message.guild.id
    author_id = message.author.id

    # TODO Maybe prevent prefix from being called even more since it queries the database
    answer = await react_with_text(bot.pre_command, message, is_private, guild_id, author_id) or \
             await react_with_image(bot.pre_command, message, is_private, guild_id) or \
             await react_with_action(bot.pre_command, message, is_private, guild_id, author_id) or \
             await talk(bot.user if is_private else message.guild.me, bot.pre_command, message, is_private, guild_id,
                        await bot.get_prefix(message))

    if not answer:
        return False
    if answer.get(ACTION):
        return True

    content = answer.get(TEXT) if is_private or perms.manage_messages else None
    embed = answer.get(EMBED) if is_private or perms.embed_links else None
    image = answer.get(IMAGE) if is_private or perms.attach_files else None
    if content or embed or image:
        await bot.send_message(message.channel, content=content, embed=embed, file=image)
        return True
    return False


async def react_with_text(pre_command, message: Message, is_private: bool, guild_id: int, author_id: int):
    """
    React to a message with a text response.
    :param pre_command: The command to execute before an action is taken.
    :param message: The message to respond to.
    :param is_private: Whether the channel the message was received in is a private channel.
    :param guild_id: The id of the guild the message was send in (possible None if is_private).
    :param author_id: The id of the author of the message.
    :return: {TEXT: The text to respond with.} or {} if there is nothing to respond to.
    """
    if (is_private or guild_id in constants.s_to_ringels_whitelist) and \
            author_id == constants.DOGEid and "s" in message.content and \
            await pre_command(message=message, channel=message.channel, command='s_to_ringel_s', delete_message=False):
        return {TEXT: "*" + message.content.replace("s", "ß")}

    if (is_private or guild_id not in constants.ayy_lmao_blacklist or author_id == constants.NYAid) and \
            (message.content.lower() == "ayy") and \
            await pre_command(message=message, channel=message.channel, command='ayy', delete_message=False):
        return {TEXT: "Lmao"}

    if author_id in [constants.NYAid, constants.TRISTANid] and message.content.lower() == "qyy" and \
            await pre_command(message=message, channel=message.channel, command='qyy', delete_message=False):
        return {TEXT: 'Kmao'}

    if message.content.lower() == "lmao" and author_id == constants.NYAid and \
            await pre_command(message=message, channel=message.channel, command='lmao', delete_message=False):
        return {TEXT: 'Ayy'}

    if (is_private or guild_id not in constants.lenny_blacklist) and "lenny" in message.content.split(" ") and \
            await pre_command(message=message, channel=message.channel, command='response_lenny', delete_message=False):
        return {TEXT: "( ͡° ͜ʖ ͡°)"}

    if (is_private or guild_id not in constants.ded_blacklist) and "ded" == message.content:
        ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
        try:
            history = message.channel.history(limit=2, after=ten_mins_ago)
            await history.next()
            await history.next()
        except NoMoreItems:
            if await pre_command(message=message, channel=message.channel, command='response_ded',
                                 delete_message=False):
                return {TEXT: random.choice(command_text.ded)}

    if (is_private or guild_id not in constants.table_unflip_blacklist) and message.content == "(╯°□°）╯︵ ┻━┻" and \
            await pre_command(message=message, channel=message.channel, command='tableflip', delete_message=False):
        return {TEXT: "┬─┬﻿ ノ( ゜-゜ノ)"}
    return {}


async def react_with_image(pre_command, message: Message, is_private: bool, guild_id: int):
    """
        React to a message with a file response.
        :param pre_command: The command to execute before an action is taken.
        :param message: The message to respond to.
        :param is_private: Whether the channel the message was received in is a private channel.
        :param guild_id: The id of the guild the message was send in (possible None if is_private).
        :param author_id: The id of the author of the message.
        :return: {IMAGE: The file to respond with.} or {} if there is nothing to respond to.
        """
    # TODO add or replace images
    if (is_private or guild_id not in constants.praise_the_sun_blacklist) and message.content == "\\o/" and \
            await pre_command(message=message, channel=message.channel, command='\\o/', delete_message=True):
        return {EMBED: embedded_pic('Praise the sun!', message.author.avatar_url, praise_the_sun).get(EMBED)}
    return {}


async def change_nickname_with(pre_command, message, new_name):
    if not await pre_command(message=message, channel=message.channel, command='nickname_auto_change',
                             delete_message=False, is_typing=False):
        return
    await message.author.edit(reason="A dad joke", nick=new_name)
    print("Changed nickname of " + message.author.display_name)


async def react_with_action(pre_command, message: Message, is_private: bool, guild_id: int, author_id: int):
    """
    React to a message with a text response.
    :param pre_command: The command to execute before an action is taken.
    :param message: The message to respond to.
    :param is_private: Whether the channel the message was received in is a private channel.
    :param guild_id: The id of the guild the message was send in (possible None if is_private).
    :param author_id: The id of the author of the message.
    :return: {ACTION: True} if an action was taken or {} if there is nothing to respond to.
    """
    # Change nickname
    if (is_private or guild_id in constants.auto_name_change_whitelist) and \
            author_id in [constants.NYAid, constants.LOLIid, constants.WIZZid] and \
            message.author.permissions_in(message.channel).change_nickname:
        if guild_id in constants.auto_name_change_whitelist:
            try:
                if len(message.content.split(" ")) > 2:
                    if (message.content.split(" ")[0] == "i", message.content.split(" ")[1]) == ("i", "am"):
                        new_name = message.content.partition(' ')[2].partition(' ')[2]
                        await change_nickname_with(pre_command, message, new_name)
                        return {ACTION: True}
                if len(message.content.split(" ")) > 1:
                    if message.content.split(" ")[0] in ["i'm", "im"]:
                        new_name = message.content.partition(' ')[2]
                        await change_nickname_with(pre_command, message, new_name)
                        return {ACTION: True}
            except Forbidden:
                pass

    # Add reacion
    if message.author.id in [constants.KAPPAid, constants.RAZid, constants.POLYid] \
            and message.content.lower() in ['owo', 'uwu', 'umu']:
        await message.add_reaction(":uumuu:715594968328175687")
        return {ACTION: True}
    return {}


async def talk(me: Member, pre_command, message: Message, is_private: bool, guild_id: int, prefix):
    """
    React to a message that talks to me using a name from the secrets file.
    :param pre_command: The command to execute before an action is taken.
    :param message: The message to respond to.
    :param is_private: Whether the channel the message was received in is a private channel.
    :param guild_id: The id of the guild the message was send in (possible None if is_private).
    :param author_id: The id of the author of the message.
    :return: {TEXT: The test to respond with.} or {} if there is nothing to respond to.
    """
    if not (len(message.content) < 2 or (message.content[:2] == '<@') or (
            message.content[0].isalpha() and message.content[1].isalpha())) or \
            (not is_private and guild_id in constants.bot_talk_blacklist):
        return {}

    if (me in message.mentions or (len(set(message.content.lower().translate(str.maketrans('', '', string.punctuation))
                                                   .split(" ")).intersection(set(bot_names))) > 0)) and \
            await pre_command(message=message, channel=message.channel, command='talk', delete_message=False):
        if 'prefix' in message.content.lower():
            return {TEXT: 'My prefix is \'{}\', darling'.format(prefix)}

        if (message.author.id in [constants.NYAid, constants.LOLIid, constants.WIZZid]) and \
                any(word in message.content.lower() for word in ['heart', 'pls', 'love']):
            return {TEXT: ":heart:"}

        if message.content[len(message.content) - 1] == "?":
            return {TEXT: random.choice(command_text.qa)}
        return {TEXT: random.choice(command_text.response)}
    return {}


def construct_starboard_embed(message: Message, stars: int):
    m = 'A message received {} stars in {}'.format(stars, message.channel.mention)
    e = Embed(colour=STAR_EMBED_COLOR)
    e.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    if message.content:
        e.add_field(name='Message contents', value=message.content)
    if message.attachments:
        e.set_image(url=message.attachments[0].get('url'))
    e.set_footer(text='Message send at ' + message.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    return m, e


async def handle_star_reaction(bot: PythonBot, reaction: Reaction):
    channel_id = get_star_channel(reaction.message.guild.id)
    if not channel_id:
        return
    channel = await bot.fetch_channel(channel_id)

    stars = sum([x.count for x in reaction.message.reactions if x.emoji == STAR_EMOJI])
    embed_id = get_star_message(reaction.message.id)
    m, e = construct_starboard_embed(reaction.message, stars)

    if embed_id:
        message = await channel.fetch_message(embed_id)
        await message.edit(content=m, embed=e)
        log.message(message, "Updated starboard embed")
        return

    i = (await bot.send_message(channel, content=m, embed=e)).id
    update_star_message(reaction.message.id, i)
