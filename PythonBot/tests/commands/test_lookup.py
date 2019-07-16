import unittest
from commands.lookup import LookupCommands as lc
from config.constants import TEXT


class Commands(unittest.TestCase):

    def test_command_osu(self):
        results = [
            ([], 'Please provide a username to look for'),
            (['123135456456434234654'], 'Ehhm, there is no user with that name...')
        ]

        for args, result in results:
            answer = lc.command_osu(args, 'author_name', 'url')
            self.assertEqual(result, answer.get(TEXT))
