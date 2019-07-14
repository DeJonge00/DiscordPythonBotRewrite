from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord import Embed, TextChannel


# Mod commands
class BasicCommands(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        print('Basic started')

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
