import unittest
from commands.config import ConfigCommands as cc
from core.constants import TEXT, EMBED

GUILD_ID = 1234567890


class Commands(unittest.TestCase):

    def test_command_prefix(self):
        args = []
        self.assertEqual("You have to specify a prefix after the command", cc.command_prefix(GUILD_ID, args).get(TEXT))

        for args in [['testtesttesttest'], ['aosjdkjfdas;jfkljas'], ['4143487', '6546573']]:
            self.assertEqual('My prefix has to be between 1 and 10 characters',
                             cc.command_prefix(GUILD_ID, args).get(TEXT))

        for args in [['?'], ['!'], ['//']]:
            self.assertEqual('The prefix for this server is now \'{}\'', cc.command_prefix(GUILD_ID, args).get(TEXT))
