import logging

from discord.ext import commands
from discord.ext.commands import Cog, Context

from config.constants import TEXT, STAR_EMOJI
from config.running_options import LOG_LEVEL
from core.bot import PythonBot
from database.general import prefix, delete_commands, starboard
from database.general.banned_commands import toggle_banned_command

logging.basicConfig(
    filename="logs/config_commands.log",
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

response_names = [
    "\\o/",
    "ayy",
    "response_lenny",
    "response_ded",
    "tableflip",
    "talk",
    "s_to_ringel_s",
    "nickname_auto_change",
    "uumuu_reaction",
]


class ConfigCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot

    @staticmethod
    def command_prefix(guild_id: int, args: [str]):
        if len(args) < 1:
            return {TEXT: "You have to specify a prefix after the command"}

        new_prefix = " ".join(args)
        if not (0 < len(new_prefix) <= 10):
            return {TEXT: "My prefix has to be between 1 and 10 characters"}

        prefix.set_prefix(guild_id, new_prefix)
        return {TEXT: "The prefix for this server is now '{}'"}

    @commands.command(
        name="prefix", help="Change my prefix", aliases=["setprefix", "changeprefix"]
    )
    async def prefix(self, ctx: Context, *args):
        c = ["administrator", "manage_channels"]
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="prefix",
            cannot_be_private=True,
            perm_needed=c,
        ):
            return

        response = ConfigCommands.command_prefix(ctx.guild.id, args)
        content = response.get(TEXT).format(await self.bot.get_prefix(ctx.message))
        await self.bot.send_message(destination=ctx, content=content)

    @commands.command(
        name="toggledeletecommands",
        help="Toggle whether commands will be deleted here",
        aliases=["tdc"],
    )
    async def toggledeletecommands(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="toggledeletecommands",
            cannot_be_private=True,
            perm_needed=["manage_channels", "manage_messages", "administrator"],
        ):
            return

        delete_commands.toggle_delete_commands(ctx.message.guild.id)

        if delete_commands.get_delete_commands(ctx.message.guild.id):
            m = "Commands will now be deleted in this server"
        else:
            m = "Commands will now not be deleted in this server"
        await self.bot.send_message(ctx, content=m)

    def get_command_name(self, command: str):
        if command == "all":
            return "all", "All commands"
        if command in response_names:
            return command, 'Response "{}"'.format(command)

        comm = self.bot.get_command(command)
        if not comm:
            raise ValueError
        return str(comm), 'Command "{}" is'.format(command)

    @commands.command(
        pass_context=1,
        help="Toggle whether a specific commands can be used here",
        aliases=["tc"],
    )
    async def togglecommand(self, ctx, *args):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="togglecommand",
            cannot_be_private=True,
            perm_needed=["manage_channels", "manage_messages", "administrator"],
        ):
            return

        if len(args) <= 0:
            m = "The response commands are (un)banned with either of {}".format(
                ", ".join(response_names)
            )
            await self.bot.send_message(destination=ctx.channel, content=m)
            return

        if len(args) <= 1 or not (args[0].lower() in ["server", "channel"]):
            m = 'Please give me either "server" or "channel" followed by the name of the command'
            await self.bot.send_message(destination=ctx.channel, content=m)
            return

        command = " ".join(args[1:])
        try:
            name, text = self.get_command_name(command)
        except ValueError:
            m = "I do not recognize the command name " + command
            await self.bot.send_message(destination=ctx.channel, content=m)
            return

        # Check whether to ban locally or globally
        id_type = args[0].lower()
        identifier = ctx.guild.id if id_type == "server" else ctx.channel.id

        # Add or remove command
        if name == "togglecommand":
            await self.bot.send_message(
                destination=ctx.channel, content="Wow... just wow"
            )
            return
        result = toggle_banned_command(id_type, identifier, name)
        if not result:
            await self.bot.send_message(
                destination=ctx.channel,
                content="{} now unbanned from this {}".format(text, args[0]),
            )
        else:
            await self.bot.send_message(
                destination=ctx.channel,
                content="{} now banned from this {}".format(text, args[0]),
            )

    @commands.command(
        name="starboard",
        help="List the special messages, which are reacted to with a star emoji",
        aliases=["star"],
    )
    async def starboard(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="starboard",
            cannot_be_private=True,
            perm_needed=["administrator", "manage_server", "manage_channels"],
        ):
            return

        if starboard.get_star_channel(ctx.message.guild.id) == ctx.channel.id:
            starboard.delete_star_channel(ctx.message.guild.id)
            m = "The starboard for this server has been succesfully deleted!"
        else:
            starboard.set_star_channel(ctx.message.guild.id, ctx.message.channel.id)
            m = "React with {} to see your messages get saved in this channel".format(
                STAR_EMOJI
            )

        await self.bot.send_message(ctx, m)


def setup(bot):
    bot.add_cog(ConfigCommands(bot))
