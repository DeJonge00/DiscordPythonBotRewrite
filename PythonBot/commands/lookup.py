from core.bot import PythonBot
from config.constants import TEXT, EMBED, LOOKUP_COMMANDS_EMBED_COLOR as EMBED_COLOR
from secret.secrets import osu_api_key

from discord import TextChannel, Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context

import re
import requests


class LookupCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        print('Lookup commands cog started')

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

    @commands.command(pass_context=1, help="Look up someones osu stats!")
    async def osu(self, ctx, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='osu'):
            return

        answer = LookupCommands.command_osu(args, ctx.message.author.display_name, ctx.message.author.avatar_url)

        await self.bot.send_message(ctx.channel, content=answer.get(TEXT), embed=answer.get(EMBED))


def setup(bot):
    bot.add_cog(LookupCommands(bot))
