from database.general import banned_commands as bc
from database.general import delete_commands as dc
from database.general import welcome
from database.general import self_assignable_roles as sar
from database.general.general import WELCOME_TABLE, GOODBYE_TABLE, SERVER_ID
import unittest

TEST_GUILD_ID = 1234567890
CHANNEL_ID = 1122334455


class Commands(unittest.TestCase):

    def test_welcome_goodbye(self):
        for table in [WELCOME_TABLE, GOODBYE_TABLE]:
            for message in ['Welcome message {} uwu', 'owowo']:
                welcome.set_message(table, TEST_GUILD_ID, CHANNEL_ID, message)
                self.assertEqual((CHANNEL_ID, message), welcome.get_message(table, TEST_GUILD_ID))

    def test_do_not_delete(self):
        for i in range(0, 2):
            self.assertEqual(dc.toggle_delete_commands('serverid'), dc.get_delete_commands('serverid'))

    def test_banned_command(self):
        for command_name in ['command', '', '1234']:
            for i in range(2):
                self.assertEqual(bc.toggle_banned_command(SERVER_ID, TEST_GUILD_ID, command_name), bc.get_banned_command(SERVER_ID, TEST_GUILD_ID, command_name))

    def test_roles(self):
        for role in [123456789]:
            in_it = role in sar.get_roles(TEST_GUILD_ID)
            self.assertEqual(in_it, not sar.toggle_role(TEST_GUILD_ID, role))
