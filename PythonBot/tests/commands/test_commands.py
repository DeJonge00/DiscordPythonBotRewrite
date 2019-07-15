import unittest
from commands.commands import BasicCommands as bc
from config.constants import TEXT, EMBED
from tests.objects import get_test_attachment, get_test_user

from discord import Attachment, User, Embed
import re


class Commands(unittest.TestCase):

    def test_command_cast(self):
        # TODO Think of testing random functions
        pass

    def test_command_compliment(self):
        # TODO Think of testing random functions
        pass

    @staticmethod
    def get_cookie_number(answer: {TEXT: str}):
        r = re.match('.*?(\d+).*?', answer.get(TEXT))
        return int(r.groups()[0])

    def test_command_cookie(self):
        # Make sure the name does not contain numbers for this test
        display_name = 'name'
        self.assertEqual(
            Commands.get_cookie_number(answer=bc.command_cookie(display_name)) + 1,
            Commands.get_cookie_number(answer=bc.command_cookie(display_name))
        )

    def test_command_echo(self):
        author = get_test_user('author_name')

        message = 'test test2 test3'
        self.assertEqual(message, bc.command_echo(message.split(), [], author).get(TEXT))

        file_url = 'file-url'
        attachment = get_test_attachment(url=file_url)

        embed: Embed = bc.command_echo('', [attachment], author).get(EMBED)
        self.assertEqual(file_url, embed.image.url)

    def test_command_embed(self):
        author_name = 'author_name'
        author_url = 'author_url'
        text = 'Hello World'
        attachment_url = 'attachment_url'
        attachment = get_test_attachment(url='attachment_url')

        embed = bc.command_embed(text.split(), author_name, author_url, [attachment]).get(EMBED)

        self.assertEqual(author_name, embed.author.name)
        self.assertEqual(author_url, embed.author.icon_url)
        self.assertEqual(text, embed.fields[0].value)
        # TODO Fix test when the todo in the function is resolved
        # self.assertEqual(attachment_url, embed.image.url)
