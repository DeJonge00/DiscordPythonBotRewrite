import unittest
from commands.basic import BasicCommands as bc
from config.constants import TEXT, EMBED
from tests.objects import get_test_attachment, get_test_user, get_test_emoji

from discord import Embed
from datetime import datetime, timedelta
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

    def test_command_emoji(self):
        for text in ['', 'abcdef']:
            answer = bc.command_emoji(text.split(), '', '', [])
            self.assertTrue(answer.get(TEXT))
            self.assertTrue(answer.get(EMBED) is None)

        emoji_name = 'emoji1'
        emoji_id = 123451234512345
        emoji1 = get_test_emoji(emoji_name, emoji_id)
        for text in [str(emoji_id), emoji_name]:
            answer = bc.command_emoji(text.split(), '', '', [emoji1]).get(EMBED)
            # .get(EMBED) returns False even if the attribute is there, so checking the returned value instead.
            self.assertFalse(answer is None)
            self.assertEqual("https://cdn.discordapp.com/emojis/{}.png".format(emoji_id), answer.image.url)

    def test_command_emojify(self):
        answers = {
            'lol': ':regional_indicator_l: :regional_indicator_o: :regional_indicator_l:',
            '?!': ':question: :exclamation:',
            '012345': ':zero: :one: :two: :three: :four: :five:'
        }
        for original, formatted in answers.items():
            self.assertEqual(formatted, bc.command_emojify(original.split()).get(TEXT))

    def test_command_hype(self):
        answer = bc.command_hype([get_test_emoji('emoji1', 1)])
        self.assertEqual('<:emoji1:1>', answer.get(TEXT))

    def test_command_kill(self):
        author = get_test_user('author')
        target = get_test_user('target')
        answer = bc.command_kill(author, author)
        self.assertEqual("Suicide is not the answer, 42 is", answer.get(TEXT))
        answer = bc.command_kill(author, target)
        self.assertNotEqual("Suicide is not the answer, 42 is", answer.get(TEXT))

    def test_command_kiss(self):
        author = get_test_user('author')
        target = get_test_user('target')
        failure_answer = "{0} Trying to kiss yourself? Let me do that for you...\n*kisses {0}*".format(author.mention)
        answer = bc.command_kiss(author, author)
        self.assertEqual(failure_answer, answer.get(TEXT))
        answer = bc.command_kiss(author, target)
        self.assertNotEqual(failure_answer, answer.get(TEXT))

    def test_command_pat(self):
        author = get_test_user('author')
        target = get_test_user('target')
        time = datetime.utcnow()
        last_pat = time - timedelta(days=1)

        answer = bc.command_pat(time, author, last_pat, author)
        self.assertEqual(author.mention + " One does not simply pat ones own head", answer.get(TEXT))
        answer = bc.command_pat(time, author, time, target)
        self.assertEqual(author.mention + " Not so fast, b-b-baka!", answer.get(TEXT))

        def get_pat_nr(text: str):
            answer_regex = "<.+> has pat <.+> (.+) times? now.*"
            try:
                return int(re.match(answer_regex, text).groups()[0])
            except:
                return -1

        prev = get_pat_nr(bc.command_pat(time, author, last_pat, target).get(TEXT))
        for i in range(3):
            answer = get_pat_nr(bc.command_pat(time, author, last_pat, target).get(TEXT))
            self.assertEqual(prev + 1, answer)
            prev = answer
