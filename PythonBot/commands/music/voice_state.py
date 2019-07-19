from commands.music.song import Song
from core import logging as log

from discord import VoiceClient, Embed, TextChannel

from os import remove, path


class VoiceState:
    def __init__(self, state: VoiceClient, guild_name: str):
        self.queue: [Song] = []
        self.current: Song = None
        self.repeat = False
        self.state: VoiceClient = state
        self.skip_votes = []
        self.guild_name = guild_name
        self.running = True

    def get_queue_display(self):
        """
        Creates an embed with information about songs in the queue
        :return: The Embed object
        """
        e = Embed()
        q = self.get_queue()
        if not len(q):
            return 'The queue is empty'
        v = '\n'.join([str(s) for s in self.queue])
        e.add_field(name='Queue', value=v)
        return e

    def get_queue(self):
        """
        Returns existing queue or creates a new one
        :return: [Song]
        """
        try:
            return self.queue
        except AttributeError:
            self.queue = []
            return self.queue

    def add_song_to_queue(self, song: Song):
        """
        Adds a single Song object to the queue and initiates play if not already playing
        :param song: The next song to play
        """
        q = self.get_queue()
        q.append(song)
        if not self.state.is_playing():
            self.play_next()

    def remove_song_from_queue(self, nr=0):
        """
        Remove a song from the queue
        :param nr: The number of the song in the queue
        :return: The song that was removed
        """
        q = self.get_queue()
        self.queue = q[:nr] + q[nr + 1:]
        return q[nr]

    def delete_current(self):
        """
        Deletes the song that is playing or recently finished (the song in self.current)
        This deletes resets the state of the player and deletes the song file
        """
        if self.current and path.exists(self.current.file_name):
            try:
                remove(self.current.file_name)
                print('Deleted', self.current.file_name)
            except PermissionError:
                print('Deletion failed: PermissionError')

    def finalize_song(self, error):
        """
        The callback function of VoiceClient.play(), resets current song and initiates a next song
        :param error: A potential error that was thrown while playing a song
        """
        if error:
            log.announcement(self.guild_name, 'Error: ' + str(error))
        self.play_next(song=self.current) if self.repeat else self.play_next()

    def play_next(self, song: Song = None):
        """
        (Force) play the next song in the queue
        :param song: The song to be played instead of the next song in the queue (ie: when repeating a song)
        :return: The next song that will be playing
        """
        if not self.running:
            return False
        if not song:
            if self.state.is_playing():
                self.state.stop()
            self.delete_current()
            q = self.get_queue()
            if not q:
                return False
            song = self.current = q[0]
        if self.state.is_playing():
            self.state.stop()
        self.skip_votes = []
        try:
            self.state.play(song.stream_object, after=self.finalize_song)
        except FileNotFoundError:
            return self.play_next()
        self.remove_song_from_queue()
        return song

    async def disconnect(self):
        """
        Stop playing music and disconnect from the voicechannel
        """
        self.running = False
        if self.state:
            if self.state.is_playing():
                self.state.stop()
            await self.state.disconnect()
