import logging
import re

from discord import Member, TextChannel, PermissionOverwrite, Forbidden
from discord.ext import commands
from discord.ext.commands import Cog, Context

from config.constants import TEXT, KICK_REASON, member_counter_message
from core.bot import PythonBot
from core.utils import prep_str
from database.general import self_assignable_roles
from database.general.auto_voice_channel import set_joiner_channel
from database.general.general import WELCOME_TABLE, GOODBYE_TABLE
from database.general.member_counter import set_member_counter_channel, get_member_counter_channel
from database.general.welcome import set_message
from secret.secrets import LOG_LEVEL

logging.basicConfig(filename='logs/mod_commands.log', level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


class ModCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot

    @staticmethod
    async def command_autovc(channel: TextChannel, name: str):
        bot_perms = channel.permissions_for(channel.guild.me)
        if not bot_perms.manage_channels:
            return {TEXT: 'I do not have the permissions to set this up'}
        if not name:
            name = 'General'
        name = '▶ ' + name

        new_vc = await channel.guild.create_voice_channel(name)
        set_joiner_channel(channel.guild.id, new_vc.id)
        return {TEXT: 'New channel \'{}\' created'.format(name)}

    @commands.command(name='autovc', help="BANHAMMER")
    async def autovc(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='autovc',
                                          perm_needed=['manage_channels', 'administrator']):
            return

        answer = await ModCommands.command_autovc(ctx.channel, ' '.join(args))
        await self.bot.send_message(ctx.channel, answer.get(TEXT))

    @staticmethod
    def command_banish(mod: Member, users: [Member], text: str):
        if len(users) <= 0:
            return {TEXT: 'Mention one or more users to banish them from the server'}

        matched_groups = re.match('^.*?( <@!?\d+>)+ ?(.*)$', text).groups()

        if not matched_groups[-1]:
            return {KICK_REASON: 'The basnish command was used by {} to kick you'.format(mod)}
        return {KICK_REASON: '{} banned you with the reason: \'{}\''.format(mod, matched_groups[-1])}

    @commands.command(name='banish', help="BANHAMMER")
    async def banish(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='banish',
                                          perm_needed=['kick_members', 'administrator']):
            return

        answer = ModCommands.command_banish(ctx.author, ctx.message.mentions, ctx.message.content)
        if answer.get(TEXT):
            await self.bot.send_message(ctx.channel, answer.get(TEXT))
            return

        for user in ctx.message.mentions:
            await user.kick(reason=answer.get(KICK_REASON))

        m = 'Banished users {} successfully'.format(', '.join(ctx.message.mentions))
        await self.bot.send_message(ctx.channel, m)

    @staticmethod
    async def command_membercount(user: Member, channel: TextChannel, args: [str]):
        if not channel.permissions_for(user).manage_channels:
            return {TEXT: 'I need permission to manage channels'}
        name = member_counter_message.format(channel.guild.member_count)
        permissions = {channel.guild.default_role: PermissionOverwrite(connect=False, read_messages=True),
                       user.roles[-1]: PermissionOverwrite(manage_channels=True, connect=True)}

        old_channel_id = get_member_counter_channel(guild_id=channel.guild.id)
        if old_channel_id:
            try:
                await channel.guild.get_channel(old_channel_id).delete()
            except Forbidden:
                pass
        if len(args) >= 1 and args[0].lower() in ['voicechannel', 'voice', 'vc', 'v']:
            channel = await channel.guild.create_voice_channel(name=name, position=0, overwrites=permissions)
        elif len(args) >= 1 and args[0].lower() in ['textchannel', 'text', 't']:
            channel = await channel.guild.create_text_channel(name=name, position=0, overwrites=permissions)
        else:
            channel = await channel.guild.create_category(name=name, overwrites=permissions)
        set_member_counter_channel(channel.guild.id, channel.id)
        return {TEXT: 'Channel \'{}\' created'.format(name)}

    @commands.command(name='membercount', help="Count the people in this server for everyone to see",
                      aliases=['membercounter'])
    async def membercount(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='purge', is_typing=False,
                                          perm_needed=['administrator', 'manage_channels']):
            return
        answer = await ModCommands.command_membercount(ctx.guild.me, ctx.channel, args)
        await self.bot.send_message(ctx.channel, answer.get(TEXT))

    @commands.command(name='purge', help="Remove a weird chat")
    async def purge(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='purge', is_typing=False,
                                          perm_needed=['administrator', 'manage_messages']):
            return
        match = re.match('.*?(\d+)?.*((<@!?\d+>)+)?', ' '.join(args))
        limit = int(match.groups()[0]) if match else 10

        if len(ctx.message.mentions) > 0:
            await ctx.channel.purge(check=lambda m: m.author in ctx.message.mentions, limit=limit)
            return
        await ctx.channel.purge(limit=limit)

    @staticmethod
    def set_welcome(args: [str], table: str, type: str, guild_id: int, channel_id: int):
        if len(" ".join(args)) > 120:
            return {TEXT: "Sorry, this message is too long..."}
        if re.match('.*{.+}.*', " ".join(args)):
            return {TEXT: "Something went terribly wrong..."}
        set_message(table, guild_id, channel_id, " ".join(args))
        if len(args) > 0:
            return {TEXT: "{} message for this server is now: ".format(type) + " ".join(args).format("<username>")}
        return {TEXT: "{} message for this server has been reset".format(type)}

    @commands.command(name='setgoodbye', help="Sets a goodbye message", aliases=['goodbye'])
    async def setgoodbye(self, ctx, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='setgoodbye'):
            return

        answer = ModCommands.set_welcome(args, GOODBYE_TABLE, 'Goodbye', ctx.guild.id, ctx.channel.id)
        await self.bot.send_message(ctx.channel, content=answer.get(TEXT))

    @commands.command(name='setwelcome', help="Sets a welcome message", aliases=['welcome'])
    async def setwelcome(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='setwelcome',
                                          perm_needed=['manage_server', 'administrator']):
            return

        answer = ModCommands.set_welcome(args, WELCOME_TABLE, 'Welcome', ctx.guild.id, ctx.channel.id)
        await self.bot.send_message(ctx.channel, content=answer.get(TEXT))

    @commands.command(name='togglerole', help="Toggles a role to be self-assignable or not",
                      aliases=['toggleassignable', 'sarole'])
    async def togglerole(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='togglerole',
                                          perm_needed=['manage_roles', 'administrator']):
            return

        # Determine role
        role = prep_str(' '.join(args))
        if not role:
            await self.bot.send_message(ctx.channel, 'You have to specify the role you want')
            return
        possible_roles = [r for r in ctx.guild.roles if prep_str(r.name).startswith(role)]
        if not possible_roles:
            await self.bot.send_message(ctx.channel, 'Thats not a valid role')
            return
        if len(possible_roles) == 1:
            role = possible_roles[0]
        else:
            role = await self.bot.ask_one_from_multiple(ctx, possible_roles, 'Which role did you have in mind?')
            if not role:
                return

        r = '' if self_assignable_roles.toggle_role(ctx.guild.id, role.id) else 'not '
        await self.bot.send_message(ctx.channel, 'Role {} is now {}self-assignable'.format(role.name, r))


def setup(bot):
    bot.add_cog(ModCommands(bot))
