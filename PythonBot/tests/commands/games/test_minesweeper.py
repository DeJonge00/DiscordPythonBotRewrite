import unittest
from commands.games.minesweeper.commands import Minesweeper
from commands.games.minesweeper.game_instance import (
    MinesweeperInstance,
    FLAG,
    MINE,
    UNGUESSED,
    LOSS,
    WIN,
    PLAYING,
)


class Commands(unittest.TestCase):
    def test_read_parameters(self):
        self.assertEqual(Minesweeper.read_parameters("10", "20", "50"), (10, 20, 50))
        self.assertEqual(Minesweeper.read_parameters("a", "b", "c"), (10, 15, 20))
        self.assertEqual(Minesweeper.read_parameters("", "", ""), (10, 15, 20))
        self.assertEqual(Minesweeper.read_parameters("-10", "-2", "0"), (1, 1, 1))
        self.assertEqual(
            Minesweeper.read_parameters(
                "10000", "1000000000000000", "100000000000000000"
            ),
            (50, 50, 2500),
        )
        self.assertEqual(Minesweeper.read_parameters("30", "10", "10"), (10, 30, 10))

    def test_convert(self):
        self.assertEqual(MinesweeperInstance.convert(FLAG), "F")
        self.assertEqual(MinesweeperInstance.convert(MINE), "?")
        self.assertEqual(MinesweeperInstance.convert(UNGUESSED), "?")
        for i in range(1, 9):
            self.assertEqual(MinesweeperInstance.convert(i), str(i))

    @staticmethod
    def reset_board(game: MinesweeperInstance):
        game.board = [
            [UNGUESSED, UNGUESSED, UNGUESSED, MINE],
            [UNGUESSED, UNGUESSED, UNGUESSED, UNGUESSED],
            [UNGUESSED, UNGUESSED, UNGUESSED, UNGUESSED],
        ]
        game.height, game.width = 3, 4
        game.game_state = PLAYING

    def test_minesweeper(self):
        game = MinesweeperInstance(1, 1, 1)
        self.assertEqual(str(game), "?")

        self.reset_board(game)
        self.assertEqual(game.guess(3, 0), LOSS)
        self.reset_board(game)
        self.assertEqual(game.guess(0, 0), WIN)
