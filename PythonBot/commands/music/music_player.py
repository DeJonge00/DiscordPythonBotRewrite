import logging
import re
from datetime import datetime

from discord import Message, TextChannel, Reaction

from commands.music.song import Song
from commands.music.voice_state import VoiceState
from core.bot import PythonBot
from secret.secrets import LOG_LEVEL

logging.basicConfig(filename='logs/music_player.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


class MusicPlayer:
    def __init__(self, mybot: PythonBot):
        self.bot = mybot
        # self.states: {int: (VoiceState, TextChannel)}
        self.states = {}
        self.running = True

    async def music_loop(self, time: datetime):
        for s, _ in self.states.values():
            if s.state.is_connected() and not s.state.is_playing() and ((time - s.last_song_start).seconds > (10 * 60)):
                await s.disconnect()

    async def handle_reaction(self, r: Reaction):
        pass

    async def check_connected(self, m: Message):
        """
        Check whether the author of the message is connected to a voicechannel
        :param m: The message issueing a command
        :return: Boolean: True if the author is connected to a VoiceChannel
        """
        if not m.author.voice:
            await self.bot.send_message(m.channel, 'You are not connected to vc, silly')
            return False
        return True

    def get_voice_state(self, channel: TextChannel):
        """
        Get the VoiceState belonging to the guild, create a new one is there is none
        :param channel: The channel where the command was issued
        :return: A VoiceState object belonging to the guild
        """
        s, _ = self.states.get(channel.guild.id, (None, None))
        if s:
            return s
        if not channel.guild.voice_client:
            return
        new_state = VoiceState(channel.guild.voice_client, channel.guild.name)
        self.states[channel.guild.id] = (new_state, channel)
        return new_state

    async def add_song_to_queue(self, message: Message, song_url: str):
        """
        Add a new song to the queue of a guild
        :param message: The message that issued the command
        :param song_url: The url or name of the song to be retrieved from youtube
        """
        if not re.match('([a-zA-Z0-9 ]*)|(^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$)', song_url):
            await self.bot.send_message(message.channel, 'I cannot find anything for that sadly...')
            return
        song = Song(message.author, song_url)
        if not song:
            return

        state = self.get_voice_state(message.channel)
        if not state:
            await self.join_voice_channel(message)
            state = self.get_voice_state(message.channel)

        state.add_song_to_queue(song)
        await self.bot.send_message(message.channel, embed=song.as_embed())

    async def join_voice_channel(self, message: Message, from_state=None,
                                 only_if_old_empty=True):
        """
        Let the bot join the same voicechannel as the author is in.
        :param message: The message that issued the command.
        :param from_state: A state that is already in another channel if the bot needs to switch from there.
        :param only_if_old_empty: Only if from_state contains a state: Only move from another VoiceChannel if the bot
        is not already playing for other people there
        :return:
        """
        if not await self.check_connected(message):
            return
        channel = message.author.voice.channel
        perms = channel.permissions_for(channel.guild.me)
        if not perms.connect:
            await self.bot.send_message(message.channel, 'I need permission to connect to this channel')
            return False
        # TODO Test whether perms.use_voice_activation is necessary
        if not perms.speak:
            await self.bot.send_message(message.channel, 'I need permission to speak in this channel')
            return False

        if from_state:
            if only_if_old_empty and from_state.is_playing() and len(from_state.channel.members) > 1:
                await self.bot.send_message(message.channel, 'There are already people listening to me')
                return False
            state = await from_state.move_to(channel)
        else:
            state = await channel.connect(timeout=10.0)

        if not state:
            await self.bot.send_message(message.channel, 'Trying to connect timed out...')
            return False
        return True

    async def show_queue(self, channel: TextChannel):
        """
        Show the queue for the current guild in an embedded message.
        :param channel: The channel to send the embedded message in.
        """
        state = self.get_voice_state(channel)
        if not state or not len(state.queue):
            await self.bot.send_message(channel, 'The music queue for this guild is empty')
            return
        await self.bot.send_message(channel, embed=state.get_queue_display())

    async def stop_playing(self, channel: TextChannel):
        """
        Stop playing in this server and leave all VoiceChannels
        :param channel: The channel the command was issued in and the answer should be send in.
        """
        state = self.get_voice_state(channel)
        if not state:
            await self.bot.send_message(channel, 'That worked all too well')
            return
        await state.disconnect()
        del self.states[channel.guild.id]
        await self.bot.send_message(channel, "Baibai o/")

    async def quit(self):
        for _, state in self.states:
            state[0].disconnect()
