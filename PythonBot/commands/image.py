from core.bot import PythonBot
from config import image_links
from config.constants import IMAGE_COMMANDS_EMBED_COLOR as EMBED_COLOR, image_spam_protection_removal, EMBED

from discord import Embed, Message, TextChannel
from discord.ext import commands
from discord.ext.commands import Cog, Context

import asyncio
from datetime import datetime
from random import randint, choice


class ImageCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        self.image_timers = {}
        print('Image commands cog started')

    @commands.command(pass_context=1, aliases=['avatar', 'picture'], help="Show a profile pic, in max 200x200")
    async def pp(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='pp'):
            return
        try:
            user = await self.bot.get_member_from_message(ctx=ctx, args=args, in_text=True)
        except ValueError:
            return

        if not user:
            user = ctx.message.author

        embed = Embed(colour=EMBED_COLOR)
        embed.set_author(name=str(user.name))
        embed.set_image(url=user.avatar_url)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @staticmethod
    def embedded_pic(name: str, picture: str, image_list: [str]):
        embed = Embed(colour=EMBED_COLOR)
        embed.set_author(name=name, icon_url=picture)
        # TODO Add possible number to embed to improve debugging
        embed.set_image(url=choice(image_list))
        return {EMBED: embed}

    async def send_picture_template_command(self, message: Message, channel: TextChannel, command: str,
                                            pic_links: list):
        if not await self.bot.pre_command(message=message, channel=channel, command=command, is_typing=False):
            return

        if channel.guild.id not in image_spam_protection_removal:
            if not self.image_timers.get(command):
                self.image_timers[command] = {}

            prev_time = self.image_timers.get(command).get(channel.id, datetime.utcfromtimestamp(0))
            if (datetime.utcnow() - prev_time).seconds < 15:
                message = await self.bot.send_message(channel, 'Not so fast!')
                await asyncio.sleep(2)
                await self.bot.delete_message(message)
                return
            await channel.trigger_typing()
            self.image_timers[command][channel.id] = datetime.utcnow()
        answer = ImageCommands.embedded_pic(command, self.bot.user.avatar_url, pic_links)
        await self.bot.send_message(channel, embed=answer.get(EMBED))

    @commands.command(name='cat', help="Take a look at my beautiful cats!")
    async def cat(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'cat', pic_links=image_links.cat)

    @commands.command(name='cute', help="For if you need cute anime girls!")
    async def cute(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'cute', pic_links=image_links.cute_gifs)

    @commands.command(name='cuddle', help="Cuddles everywhere!")
    async def cuddle(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'cuddle', pic_links=image_links.hug_gifs)

    @commands.command(name='happy', help="Awwww yeaaahhh!")
    async def happy(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'happy', pic_links=image_links.happy_gifs)

    @commands.command(name='lewd', help="LLEEEEEEEEWWDD!!!")
    async def lewd(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'lewd', pic_links=image_links.lewd_gifs)

    @commands.command(name='love', help="Everyone needs love in their life!")
    async def love(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'love', pic_links=image_links.love_gifs)

    @commands.command(name='nyan', help="Nyanyanyanyanyanyanyanyanya!")
    async def nyan(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'nyan', pic_links=image_links.nyan_gifs)

    @commands.command(name='otter', help="OTTERSSSSS!")
    async def otter(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'otter', pic_links=image_links.otters)

    @commands.command(name='plsno', help="Nonononononono!", aliases=['nopls'])
    async def plsno(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'plsno', pic_links=image_links.plsno_gifs)

    @commands.command(name='sadness', help="Cri!")
    async def sadness(self, ctx: Context):
        await self.send_picture_template_command(ctx.message, ctx.channel, 'sadness', pic_links=image_links.sad_gifs)


def setup(bot):
    bot.add_cog(ImageCommands(bot))
