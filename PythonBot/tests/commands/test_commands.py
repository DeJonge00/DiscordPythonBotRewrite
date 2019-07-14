import unittest
from commands.commands import BasicCommands as bc


class Commands(unittest.TestCase):

    def test_command_echo(self):
        message = 'test test2 test3'
        self.assertEqual(message, bc.command_echo(message.split(), None, None, None))
