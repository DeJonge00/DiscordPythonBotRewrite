from config.constants import ytdl_options

from discord import FFmpegPCMAudio, Embed, Member, AudioSource

from youtube_dl import YoutubeDL
from youtube_dl.utils import sanitize_filename


def get_details_from_url(url: str):
    """
    Downloads a youtube video
    :param url: The url or query for a song to download
    :return: a dict with information about the song and the filename
    """
    with YoutubeDL(ytdl_options) as ydl:
        song_info = ydl.extract_info(url, download=True)
    playlist = song_info.get('entries')
    if not playlist or not playlist[0].get('title'):
        return
    s = playlist[0]
    file_name = sanitize_filename(s.get('title'), restricted=True) + '-' + s.get('display_id') + '.' + s.get('ext')
    print('Downloaded', file_name)
    return s, file_name


class Song:
    def __init__(self, requester: Member, url: str):
        self.requester = requester

        s, self.file_name = get_details_from_url(url)
        self.title = s.get('track') or s.get('alt_title') or s.get('title', 'Unknown title')
        self.url = s.get('url')
        self.artist = s.get('artist') or s.get('creator') or s.get('uploader')
        self.thumbnail = s.get('thumbnail')
        self.duration = s.get('duration')
        self.web_url = s.get('webpage_url')

        # Create the object that can be given to VoiceClient.play()
        self.stream_object = self.create_stream_object()

    def __str__(self):
        if self.artist:
            t = '{}: {}'.format(self.artist, self.title)
        else:
            t = self.title
        if self.duration:
            try:
                d = int(self.duration)
                t += ' ({}m{}s)'.format(int(d / 60), d % 60)
            except Exception as e:
                print(self.title, self.artist)
                print('Error while adding duration:', e, 'Duration:', self.duration)
        return t

    def as_embed(self):
        e = Embed()
        e.set_author(name=self.requester.display_name, url=self.requester.avatar_url)
        e.add_field(name='Song', value=str(self))
        if self.thumbnail:
            e.set_thumbnail(url=self.thumbnail)
        if self.web_url:
            e.set_footer(text=self.web_url)
        return e

    def create_stream_object(self):
        return FFmpegPCMAudio(source=self.file_name)
