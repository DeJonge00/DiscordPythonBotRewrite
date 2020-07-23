import unittest
from commands.games.hangman.game_instance import (
    HangmanInstance,
    WRONG,
    RIGHT,
    GAME_OVER,
    MAX_FAULTS,
    WIN,
)


class Commands(unittest.TestCase):
    def test_hangman(self):
        word = "abc"
        game = HangmanInstance(word)
        self.assertEqual(word, game.word)
        self.assertEqual(game.guess("a"), RIGHT)
        self.assertEqual(game.guess("k"), WRONG)
        self.assertEqual(game.guess(word), WIN)

        game = HangmanInstance("ab")
        self.assertEqual(game.guess("a"), RIGHT)
        self.assertEqual(game.guess("c"), WRONG)
        self.assertEqual(game.guess("b"), WIN)
