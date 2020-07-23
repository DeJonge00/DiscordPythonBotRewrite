from discord.ext.commands.help import DefaultHelpCommand

from config.running_options import prefix


class CustomHelpCommand(DefaultHelpCommand):
    def __init__(self, my_bot):
        self.bot = my_bot
        super(CustomHelpCommand, self).__init__(dm_help=True)

    async def prepare_help_command(self, ctx, command):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="help"
        ):
            return
        c = "Your cry for help has been heard, I will send you some in your DMs"
        await self.bot.send_message(destination=ctx.channel, content=c)
        await super().prepare_help_command(ctx, command)

    def get_ending_note(self):
        return (
            "Message responses:"
            "\n\t'\\o/' : Praise the sun!"
            "\n\t'ded' (After a period of no messages) : Cry about a ded chat"
            "\n\t'(╯°□°）╯︵ ┻━┻' : '┬─┬ ノ( ゜-゜ノ)'"
            "\n\tMention me or 'biri' or 'biribiri' : I will talk to your lonely self"
            "\n\nVisit 'https://github.com/DeJonge00/PythonBot' for a more detailed version of this help message"
            "\n\n"
            + super().get_ending_note()
            + "\nFor more questions use '{}helpserver' or message user 'Nya#2698'"
            "\nOr use the suggestion, complaint or bugreport commands".format(prefix)
        )

    async def on_help_command_error(self, ctx, error):
        url = "https://github.com/DeJonge00/DiscordPythonBotRewrite/blob/master/PythonBot/README.md"
        c = "It seems I cannot DM you my commands, but you can find them at {}".format(
            url
        )
        await self.bot.send_message(destination=ctx.channel, content=c)
