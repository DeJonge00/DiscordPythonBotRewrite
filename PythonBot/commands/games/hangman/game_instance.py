from config.constants import HANGMAN_EMBED_COLOR as EMBED_COLOR

from discord import Embed

import string

RIGHT = 0
WRONG = 1
GAME_OVER = 2
WIN = 3
MAX_FAULTS = 6


class HangmanInstance:
    def __init__(self, word: str):
        self.word = word
        self.faults = 0
        self.guesses = []
        self.wrong_guesses = []

    def guess(self, l):
        l = l.lower()
        if self.word.lower() == l:
            return WIN
        # Wrong guess
        if (l not in self.word.lower()) and (l not in self.wrong_guesses):
            self.faults += 1
            if l not in self.wrong_guesses:
                self.wrong_guesses.append(l)
            if self.faults >= MAX_FAULTS:
                return GAME_OVER
            return WRONG
        # Right guess
        if l not in self.guesses:
            self.guesses.append(l)
        for x in self.word.lower().translate(str.maketrans("", "", string.punctuation)):
            if (x.isalpha()) and (x not in self.guesses):
                return RIGHT
        return WIN

    def __str__(self):
        s = ""
        for x in self.word:
            if x.isalpha():
                if x.lower() in self.guesses:
                    s += str(x)
                else:
                    s += "\_"
            else:
                s += str(x)
        return s

    def get_loss_embed(self, author_name: str):
        embed = Embed(colour=EMBED_COLOR)
        if self.faults >= 6:
            embed.add_field(
                name="YOU DIED", value="Better luck next time!", inline=False
            )
            embed.set_thumbnail(url="http://i.imgur.com/1IXbcNb.png")
            embed.add_field(name="The sentence", value=self.word)
            return embed

        embed.add_field(name="Message", value=author_name, inline=False)
        if self.faults == 1:
            embed.set_thumbnail(url="http://i.imgur.com/nwXZ5Ef.png")
        elif self.faults == 2:
            embed.set_thumbnail(url="http://i.imgur.com/izSXiI6.png")
        elif self.faults == 3:
            embed.set_thumbnail(url="http://i.imgur.com/D1BsiYo.png")
        elif self.faults == 4:
            embed.set_thumbnail(url="http://i.imgur.com/sqdAuTl.png")
        elif self.faults == 5:
            embed.set_thumbnail(url="http://i.imgur.com/ZHXq151.png")

        embed.add_field(name="Guessed so far", value=str(self), inline=False)
        if len(self.wrong_guesses) > 0:
            embed.add_field(
                name="Letters guessed wrong", value=" ".join(self.wrong_guesses)
            )
        embed.add_field(name="Faults", value=str(self.faults) + "/6")
        return embed

    def get_win_embed(self, author_name: str):
        embed = Embed(colour=EMBED_COLOR)
        embed.add_field(
            name="Congratulations on winning", value=author_name, inline=False
        )
        embed.set_thumbnail(
            url="http://nobacks.com/wp-content/uploads/2014/11/Golden-Star-3-500x500.png"
        )
        embed.add_field(name="The sentence was indeed", value=self.word)
        return embed
