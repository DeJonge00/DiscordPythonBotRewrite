import unittest
import sys
from unittest.mock import Mock, patch

sys.modules["secret.secrets"] = Mock()
sys.modules["database.common"] = Mock()

from commands.lookup import LookupCommands as lc
from config.constants import TEXT


class Commands(unittest.TestCase):
    def test_command_osu_empty_user(self):
        with patch(
            "commands.lookup.LookupCommands.command_osu",
            return_value={"text_message": "Please provide a username to look for"},
        ):
            answer = lc.command_osu([], "author_name", "url")
            self.assertEqual("Please provide a username to look for", answer.get(TEXT))

    def test_command_osu_random_user(self):
        with patch(
            "commands.lookup.LookupCommands.command_osu",
            return_value={"text_message": "Ehhm, there is no user with that name..."},
        ):
            answer = lc.command_osu(["123135456456434234654"], "author_name", "url")
            self.assertEqual(
                "Ehhm, there is no user with that name...", answer.get(TEXT)
            )
