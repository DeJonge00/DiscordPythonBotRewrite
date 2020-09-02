from PIL import Image
import random

MINE = 10
FLAG = 11
UNGUESSED = -1

PLAYING = 0
WIN = 1
LOSS = 2


class MinesweeperInstance:
    def __init__(self, height: int, width: int, mines: int):
        self.height = height
        self.width = width
        self.mines = mines
        self.board = MinesweeperInstance.create_board(height, width, mines)
        self.game_state = PLAYING

    @staticmethod
    def create_board(h, w, m):
        board = [[UNGUESSED for _ in range(w)] for _ in range(h)]
        mines = random.sample(range(h * w), k=m)
        for m in mines:
            board[int(m / w)][m % w] = MINE
        return board

    @staticmethod
    def convert(c, game_state=PLAYING):
        if not game_state == PLAYING:
            return (
                "?"
                if c == UNGUESSED
                else "M"
                if c == MINE
                else "F"
                if c == FLAG
                else str(c)
            )
        return "?" if c in [UNGUESSED, MINE] else "F" if c == FLAG else str(c)

    def __str__(self):
        m = (
            "Congrats, you win!"
            if self.game_state == WIN
            else "Sorry, you lost"
            if self.game_state == LOSS
            else ""
        )
        return m + "\n".join(
            [
                "".join([MinesweeperInstance.convert(y, self.game_state) for y in x])
                for x in self.board
            ]
        )

    def as_parameter_str(self):
        return "Game initialized on a {}x{} board with {} mines, glhf".format(
            self.height, self.width, self.mines
        )

    def get_mines_in_area(self, x: int, y: int):
        n = 0
        for h in range(max(0, y - 1), min(y + 2, self.height)):
            for w in range(max(0, x - 1), min(x + 2, self.width)):
                if (h != x) or (w != y):
                    if self.board[h][w] == MINE:
                        n += 1
        return n

    def area_search(self, x: int, y: int):
        for h in range(max(0, y - 1), min(y + 2, self.height)):
            for w in range(max(0, x - 1), min(x + 2, self.width)):
                if (h != x) or (w != y):
                    self.guess(w, h)

    def check_win(self):
        return not sum([y.count(UNGUESSED) for y in self.board])

    def guess(self, x: int, y: int):
        if self.game_state:
            return self.game_state
        if self.board[y][x] == MINE:
            self.game_state = LOSS
            return LOSS
        if self.board[y][x] == UNGUESSED:
            self.board[y][x] = self.get_mines_in_area(x, y)
            if self.board[y][x] == 0:
                self.area_search(x, y)
            if self.check_win():
                self.game_state = WIN
                return WIN
        return PLAYING

    def as_embed(self):
        pass

    def as_image(self):
        pass
