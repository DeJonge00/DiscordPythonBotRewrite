import logging
import re

import requests
import wikipedia
from discord import TextChannel, Embed, Member
from discord.ext import commands
from discord.ext.commands import Cog, Context

from config.constants import TEXT, EMBED, LOOKUP_COMMANDS_EMBED_COLOR as EMBED_COLOR, ERROR
from core.bot import PythonBot
from secret.secrets import LOG_LEVEL
from secret.secrets import osu_api_key

logging.basicConfig(filename='logs/lookup_commands.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


class LookupCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot

    @staticmethod
    def lookup(query: str, search_url: str, search_for: str, min_results: int, skip_results: int,
               result_url):
        page = requests.get(search_url, {'q': query})
        if page.status_code != 200:
            return {TEXT: 'Uh oh, I must have made a wrong requests'}
        n = re.findall(search_for + '[0-9]*/', page.text.replace(' ', '').replace('\n', ''))
        if len(n) <= min_results:
            return {TEXT: 'No results found for that...'}
        return {TEXT: result_url + re.findall('[0-9]+', n[skip_results])[0]}

    async def am_lookup(self, destination: TextChannel, query, genre):
        answer = self.lookup(query, 'https://myanimelist.net/search/all', 'myanimelist.net/' + genre + '/', 16, 0,
                             'https://myanimelist.net/' + genre + '/')
        await self.bot.send_message(destination, answer.get(TEXT))

    @commands.command(name='anime', help="Look up an anime!", aliases=['mal', 'myanimelist'])
    async def anime(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='anime'):
            return
        await self.am_lookup(ctx.channel, ' '.join(args), 'anime')

    @commands.command(name='manga', help="Look up a manga!")
    async def manga(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='manga'):
            return
        await self.am_lookup(ctx.channel, ' '.join(args), 'manga')

    @commands.command(name='movie', help="Look up a movie!", aliases=['imdb'])
    async def movie(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='manga'):
            return
        answer = self.lookup(' '.join(args), 'https://www.imdb.com/find', '/title/tt', 2, 2,
                             'https://www.imdb.com/title/tt')
        await self.bot.send_message(ctx.channel, answer.get(TEXT))

    @staticmethod
    def command_osu(args: [str], author_name: str, author_avatar_url: str):
        if len(args) <= 0:
            return {TEXT: 'Please provide a username to look for'}
        user = ' '.join(args)

        url = 'https://osu.ppy.sh/api/get_user'
        params = {'k': osu_api_key,
                  'u': user,
                  'm': 0,
                  'type': 'string'}

        r = requests.get(url, params=params)
        if r.status_code != 200:
            return {TEXT: 'Uh oh, the osu site did not give me any information for my request'}
        r = r.json()
        if len(r) <= 0:
            return {TEXT: 'Ehhm, there is no user with that name...'}
        r = r[0]

        embed = Embed(colour=EMBED_COLOR)
        embed.set_author(name=author_name, icon_url=author_avatar_url)
        embed.set_thumbnail(url='https://a.ppy.sh/{}?.jpg'.format(r.get('user_id')))
        embed.add_field(name="Username", value=r.get('username'))
        embed.add_field(name='Profile link', value='https://osu.ppy.sh/u/{}'.format(r.get('user_id')))
        embed.add_field(name="Playcount", value=r.get('playcount'))
        embed.add_field(name="Total score", value=r.get('total_score'))
        embed.add_field(name="Ranked score", value=r.get('ranked_score'))
        embed.add_field(name="Global rank", value='#' + r.get('pp_rank'))
        embed.add_field(name="Country rank", value='#{} ({})'.format(r.get('pp_country_rank'), r.get('country')))
        embed.add_field(name="Accuracy", value='{}%'.format(round(float(r.get('accuracy')), 3)))
        embed.add_field(name="Hours played", value=str(int(int(r.get('total_seconds_played')) / 3600)))
        embed.add_field(name="Total maps with SS", value=r.get('count_rank_ss'))
        embed.add_field(name="Total maps with S", value=r.get('count_rank_s'))

        return {EMBED: embed}

    @commands.command(name='osu', help="Look up someones osu stats!")
    async def osu(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='osu'):
            return

        answer = LookupCommands.command_osu(args, ctx.message.author.display_name, ctx.message.author.avatar_url)

        await self.bot.send_message(ctx.channel, content=answer.get(TEXT), embed=answer.get(EMBED))

    @staticmethod
    def command_game(title: str, author: Member):
        # Get exact name of the game
        url = 'https://chicken-coop.fr/rest/games'
        querystring = {"title": title}
        r = requests.get(url=url, params=querystring)
        if r.status_code != 200:
            return {TEXT: 'The description could not be retrieved, something is wrong at the source'}
        r = r.json().get('result')
        if not isinstance(r, list):
            return {TEXT: 'The game `{}` does not exist in our library'.format(title)}
        games = [g.get('title', '') for g in r]
        if not games:
            return {TEXT: 'No game with that title could be found'}
        title = games[0]

        # Get the game's information
        url = 'https://chicken-coop.fr/rest/games/{}'.format(title)
        querystring = {"title": title}
        r = requests.get(url=url, params=querystring)
        if r.status_code != 200:
            return {TEXT: 'The description for `{}` could not be found, something is wrong at the source'.format(title)}
        r = r.json().get('result')
        if not isinstance(r, dict):
            return {TEXT: 'The game `{}` exists, but there is no description for it...'.format(title)}

        # Put the results in a nice embed
        embed = Embed()
        embed.set_author(name=r.get('title'), icon_url=author.avatar_url)
        embed.set_thumbnail(url=r.get('image'))
        n = 400
        d = r.get('description')[:n] + '...' if len(r.get('description')) > n else r.get('description')
        embed.add_field(name='Description', value=d, inline=False)
        if r.get('genre'):
            embed.add_field(name='Genres', value=', '.join(r.get('genre')))
        if r.get('score'):
            embed.set_footer(text='This game scores a {}/100'.format(r.get('score')))
        return {EMBED: embed}

    @commands.command(name='game', help="Look up a game!")
    async def game(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='game'):
            return

        if not len(args):
            m = 'Just give me the title of the game to look up for you'
            await self.bot.send_message(destination=ctx.channel, content=m)
            return

        answer = LookupCommands.command_game(' '.join(args), ctx.author)
        await self.bot.send_message(ctx.channel, content=answer.get(TEXT), embed=answer.get(EMBED))

    @staticmethod
    def command_urban(args: [str]):
        q = " ".join(args)
        if not q:
            return {TEXT: '...'}

        embed = Embed(colour=EMBED_COLOR)
        try:
            params = {'term': q}
            r = requests.get('http://api.urbandictionary.com/v0/define', params=params).json().get('list')
            if len(r) <= 0:
                embed.add_field(name="Definition", value="I'm afraid there are no results for '{}'".format(q))
                return {EMBED: embed}

            r = r[0]
            embed.add_field(name="Urban Dictionary Query", value=r.get('word'))
            definition = r.get('definition').replace('[', '').replace(']', '')
            if len(definition) > 500:
                definition = definition[:500] + '...'
            embed.add_field(name="Definition", value=definition, inline=False)
            example = r.get('example').replace('[', '').replace(']', '')
            if len(definition) < 500:
                if len(example) + len(definition) > 500:
                    example = example[:500 - len(definition)]
                if len(example) > 20:
                    embed.add_field(name="Example", value=example)
            embed.add_field(name="👍", value=r.get('thumbs_up'))
            embed.add_field(name="👎", value=r.get('thumbs_down'))
            return {EMBED: embed}
        except KeyError:
            embed.add_field(name="Definition", value="ERROR ERROR ... CANT HANDLE AWESOMENESS LEVEL")
            return {EMBED: embed}

    @commands.command(pass_context=1, help="Search the totally official wiki!", aliases=["ud", "urbandictionary"])
    async def urban(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='urban'):
            return

        answer = LookupCommands.command_urban(args)
        await self.bot.send_message(ctx, content=answer.get(TEXT), embed=answer.get(EMBED))

    @staticmethod
    async def command_wikipedia(ctx: Context, ask_one, args: [str]):
        q = " ".join(args)
        if not q:
            return {TEXT: '...'}

        embed = Embed(colour=0x00FF00)
        s = wikipedia.search(q)
        if len(s) <= 0:
            return {TEXT: 'I cant find anything for that query'}
        try:
            s = await ask_one(ctx, s, 'Which result would you want to see?')
        except ValueError:
            return {ERROR: 'No choice returned when option was given to user'}
        try:
            page = wikipedia.WikipediaPage(s)
        except wikipedia.exceptions.DisambiguationError:
            return {TEXT: "This is too ambiguous..."}

        embed.add_field(name="Title", value=page.title)
        embed.add_field(name='Content', value=wikipedia.summary(s, sentences=2))
        embed.add_field(name='Page url', value=page.url)
        return {EMBED: embed}

    @commands.command(name='wikipedia', help="Search the wiki!", aliases=["wiki"])
    async def wikipedia(self, ctx, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='wikipedia'):
            return

        answer = await LookupCommands.command_wikipedia(ctx, self.bot.ask_one_from_multiple, args)
        if answer.get(TEXT) or answer.get(EMBED):
            await self.bot.send_message(ctx, content=answer.get(TEXT), embed=answer.get(EMBED))


def setup(bot):
    bot.add_cog(LookupCommands(bot))
