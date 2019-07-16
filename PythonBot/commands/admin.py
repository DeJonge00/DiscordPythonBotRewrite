from core.setup import get_cogs
from core.bot import PythonBot
from config import constants

from discord import HTTPException
from discord.ext import commands
from discord.ext.commands import Cog, Context

from io import BytesIO
from os import remove
from PIL import Image
import requests


# Mod commands
class AdminCommands(Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        print('Admin commands cog started')

    @commands.command(name='newpp', hidden=True, help="Give me a new look")
    async def newpp(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='newpp', owner_check=True,
                                          delete_message=False):
            return

        if len(ctx.message.attachments) > 0:
            url = ctx.message.attachments[0].url
        elif len(ctx.message.mentions) > 0:
            url = '.'.join(ctx.message.mentions[0].avatar_url.split('.')[:-1]) + '.png'
        else:
            await self.bot.send_message(ctx.channel, 'Pls give me smth...')
            return
        name = 'temp/newpp.png'
        try:
            # TODO: Fix saving pic first
            Image.open(BytesIO(requests.get(url).content)).save(name)
            await self.bot.delete_message(ctx.message)
            with open(name, 'rb') as file:
                await self.bot.user.edit(avatar=file.read())
            await self.bot.send_message(ctx.channel, 'Make-up is done sweety <3')
        except requests.exceptions.MissingSchema as e:
            await self.bot.send_message(ctx.channel, 'Thats not a valid target' + str(e))
        except OSError as e:
            await self.bot.send_message(ctx.channel, 'Thats not a valid target' + str(e))
        except HTTPException:
            await self.bot.send_message(ctx.channel, 'Discord pls')
        finally:
            try:
                remove(name)
            except:
                pass

    @commands.command(name='serverlist', hidden=1, help="List the servers the bot can see", aliases=['guildlist'])
    async def serverlist(self, ctx):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='serverlist',
                                          owner_check=True, is_typing=False):
            return
        m = ""
        for i in sorted([x for x in self.bot.guilds], key=lambda l: len(l.members), reverse=True):
            m += "{}, members={}, owner={}\n".format(i.name, sum([1 for _ in i.members]), i.owner)
        # await self.bot.send_message(ctx.message.channel, m)
        print(m)

    @commands.command(pass_context=1, hidden=True)
    async def reload(self, ctx: Context, *args):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='reload', owner_check=True):
            return

        cog = 'commands.' + ' '.join(args)
        if cog not in get_cogs():
            await self.bot.send_message(ctx, "That cog is either misspelled or non-existent")
            return

        self.bot.unload_extension(cog)
        self.bot.load_extension(cog)

        await self.bot.send_message(ctx, "Loaded {}!".format(cog))

    async def command_quit(self):
        try:
            await self.bot.quit()
        except Exception as e:
            print(e)
        await self.bot.logout()
        await self.bot.close()

    @commands.command(name='quit', hidden=True, help="Lets me go to sleep")
    async def quit(self, ctx: Context):
        if not await self.bot.pre_command(message=ctx.message, channel=ctx.channel, command='quit', owner_check=True):
            return

        await self.bot.send_message(destination=ctx, content="ZZZzzz...")
        await self.command_quit()


def setup(bot):
    bot.add_cog(AdminCommands(bot))
