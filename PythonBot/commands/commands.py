from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord import Embed, TextChannel


# Mod commands
class BasicCommands(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        print('Basic started')

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
        await ctx.send(embed=embed)

    @commands.command()
    async def echo(self, ctx: Context, *args):
        # if not await self.bot.pre_command(message=ctx.message, command='echo'):
        #     return

        if len(args) > 0:
            await ctx.send(content=" ".join(args))
            return

        if len(ctx.message.attachments) > 0:
            embed = Embed(colour=0x000000)
            embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
            embed.set_image(url=ctx.message.attachments[0].get('url'))
            await ctx.send(embed=embed)
            return
        await ctx.send(content=ctx.message.author.mention + " b-b-baka!")


def setup(bot):
    bot.add_cog(BasicCommands(bot))
