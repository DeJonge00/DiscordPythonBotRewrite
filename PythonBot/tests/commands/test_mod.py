import unittest
from commands.mod import ModCommands as mc
from config.constants import TEXT, KICK_REASON
from tests.objects import get_test_user

GUILD_ID = 1234567890


class Commands(unittest.TestCase):
    def test_command_banish(self):
        mod = get_test_user("mod1")
        mention1 = get_test_user("rude1")
        mention2 = get_test_user("rude2")
        mention3 = get_test_user("rude3")

        answer = mc.command_banish(mod, [], ">banish {}".format(mention1.mention))
        self.assertEqual(
            "Mention one or more users to banish them from the server", answer.get(TEXT)
        )
        answer = mc.command_banish(
            mod, [mention1], ">banish {}".format(mention1.mention)
        )
        self.assertEqual(
            "The basnish command was used by {} to kick you".format(mod),
            answer.get(KICK_REASON),
        )
        answer = mc.command_banish(
            mod,
            [mention1, mention2],
            ">banish {} {}".format(mention1.mention, mention2.mention),
        )
        self.assertEqual(
            "The basnish command was used by {} to kick you".format(mod),
            answer.get(KICK_REASON),
        )

        reason = "reason reason"
        mentions = [mention1, mention2]
        answer = mc.command_banish(
            mod,
            mentions,
            ">banish {} {} {}".format(mention1.mention, mention2.mention, reason),
        )
        self.assertEqual(
            "{} banned you with the reason: '{}'".format(mod, reason),
            answer.get(KICK_REASON),
        )

        reason = "reason {} reason".format(mention3)
        mentions = [mention1, mention2, mention3]
        answer = mc.command_banish(
            mod,
            mentions,
            ">banish {} {} {}".format(mention1.mention, mention2.mention, reason),
        )
        self.assertEqual(
            "{} banned you with the reason: '{}'".format(mod, reason),
            answer.get(KICK_REASON),
        )
