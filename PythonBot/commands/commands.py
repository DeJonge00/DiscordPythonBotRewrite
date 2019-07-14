from core.constants import TEXT, EMBED

from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord import Embed, TextChannel, Attachment, User


# Mod commands
class BasicCommands(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        print('Basic commands started')

    @commands.command(name='botstats', help="Biri's botstats!", aliases=['botinfo'])
    async def botstats(self, ctx):
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
    def command_echo(args: [str], attachments: [Attachment], author: User):
        if len(args) > 0:
            return {TEXT: " ".join(args)}

        if len(attachments) > 0:
            embed = Embed(colour=0x000000)
            embed.set_author(name=author.display_name, icon_url=author.avatar_url)
            embed.set_image(url=attachments[0].url)
            return {EMBED: embed} # TODO Testing images
        return {TEXT: author.mention + " b-b-baka!"}

    @commands.command()
    async def echo(self, ctx: Context, *args):
        if not await self.bot.pre_command(ctx=ctx, command='echo'):
            return
        answer = BasicCommands.command_echo(args, ctx.message.attachments, ctx.message.author)
        await self.bot.send_message(destination=ctx, content=answer.get(TEXT, None), embed=answer.get(EMBED, None))


def setup(bot):
    bot.add_cog(BasicCommands(bot))
