from core.bot import PythonBot
from config.constants import IMAGE_COMMANDS_EMBED_COLOR as EMBED_COLOR

from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context


class ImageCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
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


def setup(bot):
    bot.add_cog(ImageCommands(bot))
