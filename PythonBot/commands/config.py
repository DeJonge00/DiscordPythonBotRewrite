from config.constants import TEXT, STAR_EMOJI
from database import general as dbcon

from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord import Permissions


class ConfigCommands(Cog):
    def __init__(self, my_bot):
        self.bot = my_bot
        print('Config commands cog started')

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
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='prefix',
                                          cannot_be_private=True, checks=c):
            return

        response = ConfigCommands.command_prefix(ctx.guild.id, args)
        content = response.get(TEXT).format(await self.bot.get_prefix(ctx.message))
        await self.bot.send_message(destination=ctx, content=content)

    @commands.command(name='toggledeletecommands', help="Toggle whether commands will be deleted here",
                      aliases=['tdc'])
    async def toggledeletecommands(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='toggledeletecommands',
                                          cannot_be_private=True,
                                          perm_needed=['manage_channels', 'manage_messages', 'administrator']):
            return

        dbcon.toggle_delete_commands(ctx.message.guild.id)

        if dbcon.get_delete_commands(ctx.message.guild.id):
            m = 'Commands will now be deleted in this server'
        else:
            m = 'Commands will now not be deleted in this server'
        await self.bot.send_message(ctx, content=m)

    # TODO >togglecommand

    @commands.command(name='starboard', help="Change my prefix", aliases=['star'])
    async def starboard(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='starboard',
                                          cannot_be_private=True,
                                          perm_needed=['administrator', 'manage_server', 'manage_channels']):
            return

        if dbcon.get_star_channel(ctx.message.guild.id) == ctx.channel.id:
            dbcon.delete_star_channel(ctx.message.guild.id)
            m = "The starboard for this server has been succesfully deleted!"
        else:
            dbcon.set_star_channel(ctx.message.guild.id, ctx.message.channel.id)
            m = 'React with {} to see your messages get saved in this channel'.format(STAR_EMOJI)

        await self.bot.send_message(ctx, m)


def setup(bot):
    bot.add_cog(ConfigCommands(bot))