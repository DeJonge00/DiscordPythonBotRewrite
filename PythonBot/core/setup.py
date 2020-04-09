from config import constants
from config.constants import STAR_EMOJI
from core import logging as log
from core.handlers import message_handler, channel_handlers
from core.bot import PythonBot
from core.utils import get_cogs, update_member_counter, on_member_message
from database.general import bot_information, general
from secret.secrets import game_name
from commands.rpg.rpg_main import RPGGame

from datetime import datetime
from discord import Member, Status, Game, Spotify, Message, Forbidden, DMChannel, Guild, VoiceChannel, User, Activity, \
    VoiceState


def create_bot():
    bot = PythonBot()
    for cog in get_cogs():
        bot.load_extension(cog)

    @bot.event
    async def on_ready():
        print('\nStarted bot')
        print("Disc: " + bot.user.discriminator)
        print("ID: " + str(bot.user.id))
        print("Started at: " + datetime.utcnow().strftime("%H:%M:%S") + "\n")
        if not hasattr(bot, 'uptime'):
            bot.uptime = datetime.utcnow()
        await bot.change_presence(activity=Game(name=game_name), status=Status.do_not_disturb)

        bot_information.update_server_list(bot.guilds)

    @bot.event
    async def on_message(message: Message):
        if message.author.bot:
            return
        if isinstance(message.channel, DMChannel):
            if not await message_handler.new_message(bot, message):
                log.message(message)
        else:
            if message.content and message.guild.id not in constants.bot_list_servers:
                await message_handler.new_message(bot, message)

        # Commands in the message
        try:
            # TODO Remove double logging on command used in dms
            await bot.process_commands(message)
        except Forbidden:
            log.error_on_message(message, error_message='Forbidden Exception')

        # Send message to rpggame for exp
        if bot.RPGGAME and (len(message.content) < 2 or (message.content[:2] == '<@') or
                            (message.content[0].isalpha() and message.content[1].isalpha())):
            RPGGame.handle(message)

    @bot.event
    async def on_member_update(before: Member, after: Member):
        if before.id == constants.NYAid:
            if before.activity != after.activity:
                if isinstance(after.activity, Spotify):
                    activity = Game(name='🎵 {}: {} 🎵'.format(after.activity.artist, after.activity.title))
                elif isinstance(after.activity, Activity):
                    name = after.activity.name
                    if after.activity.details:
                        name += ' | ' + after.activity.details
                    activity = Game(name=name)
                else:
                    activity = after.activity if after.activity else Game(name=game_name)
                await bot.change_presence(activity=activity, status=Status.do_not_disturb)
                return

    @bot.event
    async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
        await channel_handlers.auto_channel(member, before, after)

    @bot.event
    async def on_guild_channel_delete(channel):
        if isinstance(channel, VoiceChannel):
            channel_handlers.deleted_channel(channel)

    @bot.event
    async def on_member_join(member: Member):
        await update_member_counter(member.guild)
        if member.bot:
            return
        await on_member_message(member.guild, member, general.WELCOME_TABLE, 'joined')

    @bot.event
    async def on_member_remove(member: Member):
        await update_member_counter(member.guild)
        if member.bot:
            return
        await on_member_message(member.guild, member, general.GOODBYE_TABLE, 'left')

    @bot.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return
        if reaction.emoji == "\N{BROKEN HEART}":
            if reaction.message.author.id is bot.user.id:
                await bot.delete_message(reaction.message)
                return
        if bot.MUSIC:
            await bot.musicplayer.handle_reaction(reaction)
        if bot.RPGGAME:
            await bot.rpggame.handle_reaction(reaction)
        if bot.EMBED_LIST:
            await bot.embed_list.handle_reaction(reaction)
        if reaction.emoji == STAR_EMOJI:
            await message_handler.handle_star_reaction(bot, reaction)

    @bot.event
    async def on_member_ban(guild: Guild, user: User):
        log.announcement(guild_name=guild.name, announcement_text='User {} got banned'.format(user))

    @bot.event
    async def on_member_unban(guild: Guild, user: User):
        log.announcement(guild_name=guild.name, announcement_text='User {} got unbanned'.format(user))

    @bot.event
    async def on_guild_join(guild: Guild):
        channel = bot.get_guild(constants.PRIVATESERVERid).get_channel(constants.SNOWFLAKE_GENERAL)
        m = "I joined a new server named '{}' with {} members, senpai!".format(guild.name, guild.member_count)
        await bot.send_message(channel, m)

    @bot.event
    async def on_guild_remove(guild: Guild):
        channel = bot.get_guild(constants.PRIVATESERVERid).get_channel(constants.SNOWFLAKE_GENERAL)
        m = "A server named '{}' ({} members) just removed me from service :(".format(guild.name, guild.member_count)
        await bot.send_message(channel, m)

    return bot
