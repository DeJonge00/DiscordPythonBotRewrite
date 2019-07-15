from config import constants
from config.constants import TEXT, EMBED
from core.bot import PythonBot
from database.pats import increment_pats

from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord import Embed, TextChannel, Attachment, User
import random

EMBED_COLOR = 0x008909


# Mod commands
class BasicCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        print('Basic commands started')

    @commands.command(name='botstats', help="Biri's botstats!", aliases=['botinfo'])
    async def botstats(self, ctx: Context):
        if not await self.bot.pre_command(ctx=ctx, command='botstats'):
            return
        embed = Embed(colour=0x000000)
        embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        embed.add_field(name='Profile', value=str(self.bot.user.mention))
        embed.add_field(name='Name', value=str(self.bot.user))
        embed.add_field(name='Id', value=str(self.bot.user.id))
        embed.add_field(name="Birthdate", value=self.bot.user.created_at.strftime("%D, %H:%M:%S"))
        embed.add_field(name='Total Servers', value=str(len(self.bot.guilds)))
        embed.add_field(name='Emoji', value=str(len([_ for _ in self.bot.emojis])))
        embed.add_field(name='Big Servers (100+)',
                        value=str(sum([1 for x in self.bot.guilds if x.member_count > 100])))
        embed.add_field(name='Fake friends', value=str(len(set(x.id for x in self.bot.get_all_members()))))
        embed.add_field(name='Huge Servers (1000+)',
                        value=str(sum([1 for x in self.bot.guilds if x.member_count > 1000])))
        embed.add_field(name='Commands', value=str(len(self.bot.commands)))
        embed.add_field(name='Owner', value='Nya#2698')
        embed.add_field(name='Landlord', value='Kappa#2915')
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await self.bot.send_message(destination=ctx, embed=embed)

    @staticmethod
    def command_cast(args, author_name):
        """
        Casts a random spell to a target
        :param args: The text of the message, excluding the command and split by spaces
        :param author_name: The username of the sender of the command
        :return: The response string
        """
        # Exceptions
        if len(args) <= 0:
            return {TEXT: "{}, you cannot cast without a target...".format(author_name)}

        # Casting spell
        target = ' '.join(args)
        chosen_spell = random.choice(constants.spell)
        chosen_result = random.choice(constants.spellresult)

        return {TEXT: "**{}** casted **{}** on {}.\n{}".format(author_name, chosen_spell, target, chosen_result)}

    @commands.command(name='cast', help="Cast a spell!")
    async def cast(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='cast'):
            return

        answer = BasicCommands.command_cast(args, author_name=ctx.message.author.display_name)
        await self.bot.send_message(ctx, content=answer.get(TEXT))

    @commands.command(name='compliment', help="Give someone a compliment")
    async def compliment(self, ctx, *args):
        if not await self.bot.pre_command(ctx=ctx, command='compliment'):
            return
        try:
            target = await self.bot.get_member_from_message(ctx=ctx, args=args, in_text=True)
        except ValueError:
            return
        await self.bot.send_message(ctx, random.choice(constants.compliments).format(u=[target.mention]))

    @staticmethod
    def command_cookie(display_name: str):
        n = increment_pats('cookie', 'all')
        s = '' if n == 1 else 's'
        m = "has now been clicked {} time{} in total".format(n, s)
        if n % 100 == 0:
            embed = Embed(colour=0x000000)
            m = 'The cookie {}!!!'.format(m)
            embed.add_field(name="Cookie clicker: " + display_name + " has clicked the cookie",
                            value=m)
            url = 'https://res.cloudinary.com/lmn/image/upload/e_sharpen:100/f_auto,fl_lossy,q_auto/v1/gameskinny/' \
                  'deea3dc3c4bebf48c8d61d0490b24768.png'
            embed.set_thumbnail(url=url)
            return {TEXT: m, EMBED: embed}
        return {TEXT: "{} has clicked the cookie. It {}".format(display_name, m)}

    @commands.command(name='cookie', help="Collectively click the cookie!")
    async def cookie(self, ctx):
        if not await self.bot.pre_command(ctx=ctx, command='cookie'):
            return

        answer = BasicCommands.command_cookie(ctx.message.author.display_name)
        await self.bot.send_message(ctx, content=answer.get(TEXT), embed=answer.get(EMBED))

    @staticmethod
    def command_echo(args: [str], attachments: [Attachment], author: User):
        """
        Returns what to send after an echo command was issued
        :param args: The text of the message, excluding the command itself and split by spaces
        :param attachments: The files the message has attached
        :param author: The author of the message
        :return: The text or embed that needs to be send back to the discord-client
        """
        # Exceptions
        if len(args) <= 0 and len(attachments) <= 0:
            return {TEXT: author.mention + " b-b-baka!"}

        # Echo message
        answer = {}

        # Echo an image
        # TODO Testing images
        if len(attachments) > 0:
            embed = Embed(colour=0x000000)
            embed.set_author(name=author.display_name, icon_url=author.avatar_url)
            embed.set_image(url=attachments[0].url)
            answer[EMBED] = embed

        # Echo text
        if len(args) > 0:
            answer[TEXT] = " ".join(args)

        # Return answer
        return answer

    @commands.command(name='echo', help="I'll be a parrot!", aliases=['parrot'])
    async def echo(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='echo'):
            return
        answer = BasicCommands.command_echo(args, ctx.message.attachments, ctx.message.author)
        await self.bot.send_message(destination=ctx, content=answer.get(TEXT), embed=answer.get(EMBED))


def setup(bot):
    bot.add_cog(BasicCommands(bot))
