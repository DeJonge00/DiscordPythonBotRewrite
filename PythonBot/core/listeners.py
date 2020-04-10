import logging

from config import constants
from config.constants import STAR_EMOJI
from core import logging as log
from core.handlers import message_handler, channel_handlers
from core.utils import update_member_counter, on_member_message
from database.general import general
from secret.secrets import game_name, LOG_LEVEL
from commands.rpg.rpg_main import RPGGame

from discord.ext.commands import Cog
from discord import Member, Status, Game, Spotify, Message, Forbidden, DMChannel, Guild, VoiceChannel, User, Activity, \
    VoiceState

logging.basicConfig(filename='logs/listeners.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


class Listeners(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        self.logger = logging.getLogger(__name__)
        print('Listeners started')

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if isinstance(message.channel, DMChannel):
            if not await message_handler.new_message(self.bot, message):
                log.message(message)
        else:
            if message.content and message.guild.id not in constants.bot_list_servers:
                await message_handler.new_message(self.bot, message)

        # Commands in the message
        # Get handled automatically somewhere else?
        # try:
        #     # TODO Remove double logging on command used in dms
        #     # await self.bot.process_commands(message)
        #     pass
        # except Forbidden:
        #     log.error_on_message(message, error_message='Forbidden Exception')

        # Send message to rpggame for exp
        if self.bot.RPGGAME and (len(message.content) < 2 or (message.content[:2] == '<@') or
                            (message.content[0].isalpha() and message.content[1].isalpha())):
            RPGGame.handle(message)

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
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
                await self.bot.change_presence(activity=activity, status=Status.do_not_disturb)
                return

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        await channel_handlers.auto_channel(member, before, after)

    @Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, VoiceChannel):
            channel_handlers.deleted_channel(channel)

    @Cog.listener()
    async def on_guild_create(self, guild: Guild):
        pass

    @Cog.listener()
    async def on_member_join(self, member: Member):
        await update_member_counter(member.guild)
        if member.bot:
            return
        await on_member_message(member.guild, member, general.WELCOME_TABLE, 'joined')

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        await update_member_counter(member.guild)
        if member.bot:
            return
        await on_member_message(member.guild, member, general.GOODBYE_TABLE, 'left')

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.emoji == "\N{BROKEN HEART}":
            if reaction.message.author.id is self.bot.user.id:
                await self.bot.delete_message(reaction.message)
                return
        if self.bot.MUSIC:
            await self.bot.music_player.handle_reaction(reaction)
        if self.bot.RPGGAME:
            await self.bot.rpggame.handle_reaction(reaction)
        if self.bot.EMBED_LIST:
            await self.bot.embed_list.handle_reaction(reaction)
        if reaction.emoji == STAR_EMOJI:
            await message_handler.handle_star_reaction(self.bot, reaction)

    @Cog.listener()
    async def on_member_ban(self, guild: Guild, user: User):
        log.announcement(guild_name=guild.name, announcement_text='User {} got banned'.format(user))

    @Cog.listener()
    async def on_member_unban(self, guild: Guild, user: User):
        log.announcement(guild_name=guild.name, announcement_text='User {} got unbanned'.format(user))

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        channel = self.bot.get_guild(constants.PRIVATESERVERid).get_channel(constants.SNOWFLAKE_GENERAL)
        m = "I joined a new server named '{}' with {} members, senpai!".format(guild.name, guild.member_count)
        await self.bot.send_message(channel, m)

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        channel = self.bot.get_guild(constants.PRIVATESERVERid).get_channel(constants.SNOWFLAKE_GENERAL)
        m = "A server named '{}' ({} members) just removed me from service :(".format(guild.name, guild.member_count)
        await self.bot.send_message(channel, m)


def setup(bot):
    bot.add_cog(Listeners(bot))