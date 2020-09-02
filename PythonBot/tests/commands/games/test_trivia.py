import unittest
from commands.games.trivia.commands import Trivia
import commands.games.trivia.game_instance as tr
from unittest import mock


class Commands(unittest.TestCase):
    def test_get_cats(self):
        cats = Trivia.get_cats()
        self.assertEqual(len(cats), cats[len(cats) - 1]["nbr"])

    def test_is_natural_nbr(self):
        self.assertTrue(tr.is_natural_nbr("4"))
        self.assertFalse(tr.is_natural_nbr("four"))
        self.assertFalse(tr.is_natural_nbr("4525ed4"))
        self.assertFalse(tr.is_natural_nbr("-2"))

    def test_is_boolean_answer(self):
        m = mock.Mock()
        m.content = "TRUe"
        self.assertTrue(tr.is_boolean_answer(m))
        m.content = "troo"
        self.assertFalse(tr.is_boolean_answer(m))

    def test_is_acceptable_answer(self):
        m = mock.Mock()
        m.content = "1"
        self.assertTrue(tr.is_acceptable_answer(m))
        m.content = "5"
        self.assertFalse(tr.is_acceptable_answer(m))
        m.content = "sdqsdsq"
        self.assertFalse(tr.is_acceptable_answer(m))
