import unittest
from commands.commands import BasicCommands as bc
from config.constants import TEXT, EMBED
from tests.objects import get_test_attachment, get_test_user

from discord import Attachment, User, Embed


class Commands(unittest.TestCase):

    def test_command_cast(self):
        # TODO Think of testing random functions
        pass

    def test_command_compliment(self):
        # TODO Think of testing random functions
        pass

    def test_command_echo(self):
        author = get_test_user('author_name')

        message = 'test test2 test3'
        self.assertEqual(message, bc.command_echo(message.split(), [], author).get(TEXT))

        file_url = 'file-url'
        attachment = get_test_attachment(url=file_url)

        embed: Embed = bc.command_echo('', [attachment], author).get(EMBED)
        self.assertEqual(file_url, embed.image.url)
