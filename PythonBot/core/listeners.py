import logging

from discord import Member, Status, Game, Spotify, Message, DMChannel, Guild, VoiceChannel, User, Activity, \
    VoiceState, Streaming, Embed, CustomActivity
from discord.ext.commands import Cog

from commands.games.games import ROW_NUMS
from commands.rpg.rpg_main import RPGGame
from config import constants
from config.constants import STAR_EMOJI, STREAMER_EMBED_COLOR
from config.running_options import game_name, LOG_LEVEL
from core import logging as log
from core.handlers import message_handler, channel_handlers
from core.utils import update_member_counter, on_member_message
from database.general import bot_information
from database.general import general
from database.general.stream_notification import get_streamers

logging.basicConfig(filename='logs/listeners.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


class Listeners(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        self.logger = logging.getLogger(__name__)

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
        if isinstance(after.activity, Streaming) and not isinstance(before.activity, Streaming):
            ss = get_streamers(after.guild.id)
            if str(after.id) in ss:
                embed = Embed(colour=STREAMER_EMBED_COLOR)
                embed.set_author(name=after.activity.name, icon_url=after.avatar_url)
                embed.add_field(
                    name='**{}** just started streaming {}!'.format(after.display_name, after.activity.game),
                    value='Watch here: {}'.format(after.activity.url))
                embed.set_footer(text='Look for {} on {}!'.format(after.activity.twitch_name, after.activity.platform))

                channel = self.bot.get_channel(ss.get(str(after.id)))
                await self.bot.send_message(destination=channel, embed=embed)
                # if after.activity.twitch_name:
                #     m = 'https://player.twitch.tv/?channel={}&player=facebook&autoplay=true&parent=meta.tag'.format(
                #         after.activity.twitch_name)
                #     await self.bot.send_message(destination=channel, content=m)

        if before.id == constants.NYAid and before.activity != after.activity:
            if isinstance(after.activity, Spotify):
                activity = Game(name='🎵 {}: {} 🎵'.format(after.activity.artist, after.activity.title))
            elif isinstance(after.activity, CustomActivity):
                activity = Game(name=game_name)
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
        bot_information.update_channel(channel)

    @Cog.listener()
    async def on_guild_create(self, guild: Guild):
        pass

    @Cog.listener()
    async def on_member_join(self, member: Member):
        bot_information.update_server_member_count(member.guild)
        if not member.bot:
            await on_member_message(member.guild, member, general.WELCOME_TABLE, 'joined', do_log=False)
        await update_member_counter(member.guild)

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        bot_information.update_server_member_count(member.guild)
        if not member.bot:
            await on_member_message(member.guild, member, general.GOODBYE_TABLE, 'left', do_log=False)
        await update_member_counter(member.guild)

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.emoji == "\N{BROKEN HEART}":
            if reaction.message.author.id is self.bot.user.id:
                await self.bot.delete_message(reaction.message)
                return
        if reaction.emoji in ROW_NUMS:
            await self.bot.games_cog.handle_reaction(reaction, user)
        if self.bot.MUSIC:
            await self.bot.music_player.handle_reaction(reaction)
        if self.bot.RPGGAME:
            await self.bot.rpg_game.handle_reaction(reaction)
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
        bot_information.update_server(server=guild)
        channel = self.bot.get_guild(constants.PRIVATESERVERid).get_channel(constants.SNOWFLAKE_GENERAL)
        m = "I joined a new server named '{}' with {} members, senpai!".format(guild.name, guild.member_count)
        await self.bot.send_message(channel, m)

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        bot_information.remove_server(server=guild)
        channel = self.bot.get_guild(constants.PRIVATESERVERid).get_channel(constants.SNOWFLAKE_GENERAL)
        m = "A server named '{}' ({} members) just removed me from service :(".format(guild.name, guild.member_count)
        await self.bot.send_message(channel, m)

    @Cog.listener()
    async def on_guild_update(self, before: Guild, after: Guild):
        bot_information.update_server(server=after)


def setup(bot):
    bot.add_cog(Listeners(bot))
