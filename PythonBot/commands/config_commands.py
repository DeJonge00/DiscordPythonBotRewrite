from config.constants import TEXT, EMBED
from database import general as dbcon

from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord import Embed, TextChannel, Attachment, User, Permissions, Message


# Mod commands
class ConfigCommands(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        print('Config commands started')

    @staticmethod
    def command_prefix(guild_id: int, args: [str]):
        if len(args) < 1:
            return {TEXT: "You have to specify a prefix after the command"}

        new_prefix = ' '.join(args)
        if not (0 < len(new_prefix) <= 10):
            return {TEXT: 'My prefix has to be between 1 and 10 characters'}

        dbcon.set_prefix(guild_id, new_prefix)
        return {TEXT: 'The prefix for this server is now \'{}\''}

    @commands.command(name='prefix', help="Change my prefix", aliases=['setprefix', 'changeprefix'])
    async def prefix(self, ctx, *args):
        c = [Permissions.administrator, Permissions.manage_channels]
        if not await self.bot.pre_command(ctx=ctx, command='prefix', cannot_be_private=True, checks=c):
            return

        response = ConfigCommands.command_prefix(ctx.guild.id, args)
        content = response.get(TEXT).format(await self.bot.get_prefix(ctx.message))
        await self.bot.send_message(destination=ctx,content=content)


def setup(bot):
    bot.add_cog(ConfigCommands(bot))