from config import constants
from config.constants import TEXT, EMBED
from core.bot import PythonBot
from database.pats import increment_pats

from asyncio import sleep
from discord import Embed, TextChannel, Attachment, User, Forbidden, Emoji, Member
from discord.ext import commands
from discord.ext.commands import Cog, Context
import random
import re
import requests

EMBED_COLOR = 0x008909

englishyfy_numbers = {
    '0': 'zero',
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine'
}


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

    @commands.command(name='delete', help="Delete your message automatically in a bit!", aliases=["del", "d"])
    async def delete(self, ctx, *args):
        if not await self.bot.pre_command(ctx=ctx, command='delete', is_typing=False, delete_message=False):
            return

        if len(args) > 0:
            s = args[0]
            try:
                s = float(s)
            except ValueError:
                s = 1
        else:
            s = 1
        await sleep(s)
        await self.bot.delete_message(ctx.message)

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

    @staticmethod
    def command_embed(args: [str], author_name: str, author_avatar_url: str, attachments: [Attachment]):
        """
        Embeds the text of the message into an embed
        :param args: The text of the message
        :param author_name: The display name of the author of the message
        :param author_avatar_url: The avatar-url of the author of the message
        :param attachments: The attachments of the message
        :return: {TEXT: the text of the response,
                  EMBED: The embed of the response}
        """
        embed = Embed(colour=EMBED_COLOR)
        embed.set_author(name=author_name, icon_url=author_avatar_url)
        if len(args) > 0:
            embed.add_field(name='Message', value=' '.join(args))
        else:  # TODO Images only work if the image has not been deleted yet
            return {TEXT: 'You will have to specify what to embed (images arent working yet, sorry)'}
        # if len(attachments) > 0:
        #     embed.set_image(url=attachments[0].url)
        return {EMBED: embed}

    @commands.command(name='embed', help="I'll embed that message for you!")
    async def embed(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='embed'):
            return
        answer = BasicCommands.command_embed(args, ctx.message.author.display_name, ctx.message.author.avatar_url,
                                             ctx.message.attachments)
        await self.bot.send_message(destination=ctx, content=answer.get(TEXT), embed=answer.get(EMBED))

    @staticmethod
    def command_emoji(args: [str], display_name: str, avatar_url: str, emoji_list: [Emoji]):
        # TODO Test gif emoji with nitro users
        """
        Given a message, find an emoji and display it in an embedded message.
        :param args: The text of the message, excluding the command and split by space.
        :param display_name: The name of the author of the message.
        :param avatar_url: The avatar-url of the author of the message.
        :param emoji_list: The list of emoji the bot can see.
        :return:
        """
        if len(args) <= 0:
            return {TEXT: "I NEED MORE ARGUMENTS"}

        text = ' '.join(args)
        try:
            # Emoji id was given
            emoji_id = re.match('\D*([0-9]{15,25})\D*', text).groups()[0]
        except AttributeError:
            # Search for emoji name in known emoji
            for e in emoji_list:
                if e.name in args:
                    emoji_id = e.id
                    break
            else:
                # No emoji was found
                return {TEXT: 'Sorry, emoji not found...'}
        ext = 'gif' if requests.get(
            'https://cdn.discordapp.com/emojis/{}.gif'.format(emoji_id)).status_code == 200 else 'png'
        embed = Embed(colour=EMBED_COLOR)
        embed.set_author(name=display_name, icon_url=avatar_url)
        embed.set_image(url="https://cdn.discordapp.com/emojis/{}.{}".format(emoji_id, ext))
        return {EMBED: embed}

    @commands.command(name='emoji', help="Make big emojis")
    async def emoji(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='emoji'):
            return
        answer = BasicCommands.command_emoji(args, ctx.message.author.display_name, ctx.message.author.avatar_url,
                                             self.bot.emojis)
        await self.bot.send_message(ctx, content=answer.get(TEXT), embed=answer.get(EMBED))

    @staticmethod
    def command_emojify(args: [str]):
        """
        The command that emojifies a string
        :param args: The string to be emojified
        :return: The emojfied string
        """
        text = " ".join(args).lower()
        if not text:
            return {TEXT: 'Please give me a string to emojify...'}

        def convert_char(c: str):
            if c.isalpha():
                return ' ' if c is ' ' else ":regional_indicator_" + c + ":"
            if c in englishyfy_numbers.keys():
                return ':{}:'.format(englishyfy_numbers.get(c))
            return ":question:" if c is '?' else ":exclamation:" if c == "!" else c

        return {TEXT: ' '.join([convert_char(c) for c in text])}

    @commands.command(name='emojify', help="Use emojis to instead of ascii to spell!")
    async def emojify(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='emojify'):
            return

        await self.bot.send_message(ctx, BasicCommands.command_emojify(args).get(TEXT))

    @commands.command(name='face', help="Make a random face!")
    async def face(self, ctx: Context):
        if not await self.bot.pre_command(ctx=ctx, command='face'):
            return
        await self.bot.send_message(ctx, random.choice(constants.faces))

    @commands.command(name='hug', help="Give hugs!")
    async def hug(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='hug'):
            return
        try:
            target = await self.bot.get_member_from_message(ctx, args, in_text=True)
        except ValueError:
            return

        if target == ctx.message.author:
            hug = ctx.message.author.mention + " Trying to give yourself a hug? Haha, so lonely..."
            await self.bot.send_message(ctx, hug)
            return

        hug = random.choice(constants.hug).format(u=[ctx.message.author.mention, target.mention])
        await self.bot.send_message(ctx, hug)

    @staticmethod
    def command_hype(emoji: [Emoji]):
        if len(emoji) <= 0:
            return {TEXT: 'Your server doesnt have custom emoji for me to use...'}
        return {TEXT: ' '.join([str(e) for e in random.sample(emoji, k=min(len(emoji), 10))])}

    @commands.command(name='hype', help="Hype everyone with random emoji!")
    async def hype(self, ctx: Context):
        if not await self.bot.pre_command(ctx=ctx, command='hype', cannot_be_private=True):
            return
        answer = BasicCommands.command_hype(ctx.guild.emojis)
        await self.bot.send_message(ctx, content=answer.get(TEXT))

    # TODO Kick command

    @staticmethod
    def command_kill(author: Member, target: Member):
        if author is target:
            return {TEXT: "Suicide is not the answer, 42 is"}
        return {TEXT: random.choice(constants.kill).format(u=[target.mention])}

    @commands.command(name='kill', help="Wish someone a happy death! (is a bit explicit)")
    async def kill(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='kill'):
            return

        try:
            target = await self.bot.get_member_from_message(ctx=ctx, args=args, in_text=True)
        except ValueError:
            return

        answer = BasicCommands.command_kill(ctx.message.author, target)
        await self.bot.send_message(ctx, answer.get(TEXT))

    # TODO Replace >countdown with a >remindme (not spammy, but same functionality)


def setup(bot):
    bot.add_cog(BasicCommands(bot))
