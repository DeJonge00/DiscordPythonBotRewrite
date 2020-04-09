from core.bot import PythonBot
from config.constants import MUSIC_EMBED_COLOR as EMBED_COLOR, NYAid
from commands.music.music_player import MusicPlayer
from commands.music.song import Song
from secret.secrets import prefix

from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord.opus import is_loaded

from math import ceil


class MusicCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        self.bot.music_player = MusicPlayer(my_bot)
        print('Music commands cog started')
        print('Opus loaded:', is_loaded())

    @commands.group(name='music', aliases=["m"], help="'{}help music' for full options".format(prefix))
    async def music(self, ctx: Context):
        if not ctx.invoked_subcommand:
            guild_prefix = await self.bot.get_prefix(ctx.message)
            if ctx.message.content in ['{}music'.format(guild_prefix),
                                       '{}m'.format(guild_prefix),
                                       '{}music help'.format(guild_prefix),
                                       '{}m help'.format(guild_prefix)]:
                if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music help'):
                    return
                embed = Embed(colour=EMBED_COLOR)
                embed.set_author(name="Help", icon_url=ctx.message.author.avatar_url)
                embed.add_field(name="current", value="Show information about the song currently playing", inline=False)
                embed.add_field(name="join", value="Let me join a voice channel", inline=False)
                embed.add_field(name="leave", value="Send me away from the voice channel", inline=False)
                embed.add_field(name="play",
                                value="'{0}m p' to pause or resume singing, '{0}m p <songname | url>' to add a song to the queue".format(
                                    guild_prefix), inline=False)
                embed.add_field(name="queue",
                                value="'{0}m q' to show the queue, '{0}m q <songname | url>' to add a song to the queue".format(
                                    guild_prefix), inline=False)
                embed.add_field(name="repeat", value="Repeat the current song", inline=False)
                embed.add_field(name="reset", value="Reset the player for this channel", inline=False)
                embed.add_field(name="skip", value="Vote to skip the current song", inline=False)
                embed.add_field(name="stop",
                                value="Empty the queue and skip the current song, then leave the voice channel",
                                inline=False)
                embed.add_field(name="volume", value="Change the volume of the songs", inline=False)

                await self.bot.send_message(destination=ctx.channel, embed=embed)

    @music.command(name='join', aliases=["j"], help="Let me join a voice channel")
    async def join(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music join',
                                          is_typing=False):
            return

        if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
            await self.bot.send_message(ctx.channel, "Im already singing somewhere else...")
            return

        if ctx.guild.voice_client:
            await self.music_player.join_voice_channel(ctx.message, from_state=ctx.guild.voice_client)
            return
        await self.music_player.join_voice_channel(ctx.message)

    @music.command(name='leave', aliases=["l"], help="Send me away from the voice channel")
    async def leave(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music leave',
                                          is_typing=False):
            return

        if not ctx.guild.voice_client:
            await self.bot.send_message(ctx.channel, "I am not in vc dummy")
            return

        if ctx.guild.voice_client.is_playing():
            await self.bot.send_message(ctx.channel,
                                        "I am still singing, use '{}music stop' to send me away".format(prefix))
            return
        await ctx.guild.voice_client.disconnect()

    @music.command(name='play', aliases=["p", 'pause'],
                   help="'{0}m p' to pause or resume singing, '{0}m p <songname | url>' to add a song to the queue".format(
                       prefix))
    async def play(self, ctx: Context, *song):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music play'):
            return
        state = self.music_player.get_voice_state(ctx.channel)
        if song:
            await self.music_player.add_song_to_queue(ctx.message, " ".join(song))
            return

        if state.state.is_playing():
            state.state.pause()
            await self.bot.send_message(ctx.channel, ctx.message.author.display_name + " paused my singing...")
            return
        state.state.resume()
        await self.bot.send_message(ctx.channel, "Singing resumed")

    @music.command(name='current', aliases=["c"], help="Show information about the song currently playing")
    async def current(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music current'):
            return
        state = self.music_player.get_voice_state(ctx.channel)
        if not state or not state.current or not state.is_playing():
            await self.bot.send_message(ctx.channel, "I am not performing at the moment")
            return
        await self.bot.send_message(ctx.channel, embed=state.current.as_embed())

    @music.command(name='queue', aliases=["q"],
                   help="'{0}m q' to show the queue, '{0}m q <songname | url>' to add a song to the queue".format(
                       prefix))
    async def queue(self, ctx: Context, *song):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music queue'):
            return
        state = self.music_player.get_voice_state(ctx.channel)
        if not state:
            if not await self.music_player.join_voice_channel(ctx.message):
                return
            state = self.music_player.get_voice_state(ctx.channel)
        if len(song) <= 0:
            await self.music_player.show_queue(ctx.channel)
            return
        await self.music_player.add_song_to_queue(ctx.message, " ".join(song))

    @music.command(name='stop', aliases=["quit"],
                   help="Empty the queue and skip the current song, then leave the voice channel")
    async def stop(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music stop'):
            return
        state = self.music_player.get_voice_state(ctx.channel)
        if not state or not state.state.is_playing():
            await self.bot.send_message(ctx.channel, "I am not singing at the moment")
            return
        await state.stop_playing(ctx)
        await self.music_player.stop_playing(ctx.guild)

    @music.command(name='repeat', aliases=["r"], help="Repeat the current song")
    async def repeat(self, ctx):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music repeat'):
            return
        state = self.music_player.get_voice_state(ctx.channel)
        if not state or not state.state.isplaying():
            await self.bot.send_message(ctx.message, "I am not singing at the moment")
            return
        if not ctx.author.voice or ctx.author.voice.channel is not state.voice.channel:
            await self.bot.send_message(ctx.message, "You are not here with me...")
            return
        if state.repeat:
            state.repeat = False
            await self.bot.send_message(ctx.message, "Repeat is now off")
            return
        state.repeat = True
        await self.bot.send_message(ctx.message, "Repeat is now on")

    @music.command(name='skip', aliases=["s"], help="Vote to skip a song, or just skip it if you are the requester")
    async def skip(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='music skip'):
            return
        state = self.music_player.get_voice_state(ctx.channel)
        if not state or not state.state.is_playing():
            await self.bot.send_message(ctx.channel, "I am not playing songs right now...")
            return
        if not ctx.author.voice or ctx.author.voice.channel is not state.state.channel:
            await self.bot.send_message(ctx.channel, "You are not in the right voice channel for this command")
            return

        # dequeue later song
        if len(args) > 0:
            try:
                n = int(args[0]) - 1
            except ValueError:
                await self.bot.send_message(ctx.channel, "I'm not sure that's a number...")
                return
            songs = state.get_queue()
            if n >= len(songs):
                await self.bot.send_message(ctx.channel, "The song queue is not that long...")
            if (ctx.message.author.id == songs[n].requester.id) or (ctx.message.author.id == NYAid):
                s = state.remove_song_from_queue(n)
                await self.bot.send_message(ctx.channel, "Removed a song from the queue: {}".format(s))
                return
            else:
                await self.bot.send_message(ctx.channel, "Only the requester, {}, can skip that song".format(
                    songs[n].requester.name))
                return

        # dequeue current song
        state.skip_votes.append(ctx.message.author.id)
        votes_needed = ceil(len([p for p in ctx.author.voice.channel.members if not p.bot]) / 3)
        votes = len(state.skip_votes)
        if votes >= votes_needed:
            state.play_next()
            await self.bot.send_message(ctx.channel, "{} people voted to skip the song\nSkipping now!".format(votes))
            return
        if state.current.requester.id == ctx.message.author.id:
            state.play_next()
            await self.bot.send_message(ctx.channel, "Master has decided to skip this song!")
            return
        await self.bot.send_message(ctx.channel, "Votes to skip: {}/{}".format(votes, votes_needed))


def setup(bot):
    bot.add_cog(MusicCommands(bot))
