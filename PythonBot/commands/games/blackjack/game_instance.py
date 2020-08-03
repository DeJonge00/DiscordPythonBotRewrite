from random import randrange

from discord import Member, Embed

colors = ["hearts", "diamonds", "spades", "clubs"]
value_conversions = {"ace": 1, "king": 10, "queen": 10, "jack": 10}

GAME_OVER = 1
PLAYING = 2


class Card:
    def __init__(self, value, color):
        self.value = value
        self.color = color

    def __str__(self):
        return "{} of {}".format(self.value, self.color)

    def __int__(self):
        if self.value in value_conversions.keys():
            return value_conversions.get(self.value)
        return int(self.value)


class Deck:
    def __init__(self, sets=1):
        self.cards = [
            Card(value, color)
            for value in [*range(2, 10), *value_conversions.keys()] * sets
            for color in colors
        ]

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return (
            "a pile of {} cards".format(len(self))
            if self.score() > 21
            else "\n".join([str(c) for c in self.cards])
        )

    def score(self):
        aces = len([c for c in self.cards if int(c) == 1])
        s = sum(int(x) for x in self.cards)
        while aces > 0 and s <= 11:
            aces -= 1
            s += 10
        return s

    def draw(self):
        return self.cards.pop(randrange(0, len(self.cards)))

    def add(self, card: Card):
        self.cards.append(card)
        return card

    def last(self):
        return self.cards[-1]


def fold_embed(cards: Deck, dealer: Deck):
    embed = Embed()
    embed.add_field(name="You: {}".format(cards.score()), value=str(cards))
    embed.add_field(name="Dealer: {}".format(dealer.score()), value=str(dealer))
    if dealer.score() > 21:
        embed.set_footer(
            text="You win! With {} points less".format(dealer.score() - cards.score())
        )
    else:
        embed.set_footer(
            text="You lost! With {} points more".format(dealer.score() - cards.score())
        )
    return embed


class BlackjackGame:
    def __init__(self, player: Member):
        self.player = player
        self.draw_pile = Deck(sets=1)
        self.cards_in_play = Deck(sets=0)
        self.discard_pile = Deck(sets=0)
        self.game_over = False

    def draw(self):
        self.cards_in_play.add(self.draw_pile.draw())
        if self.cards_in_play.score() > 21:
            self.game_over = True
            return GAME_OVER
        return PLAYING

    def fold(self):
        dealer = Deck(sets=0)
        player_score = self.cards_in_play.score()
        while dealer.score() < player_score:
            dealer.add(self.draw_pile.draw())
        return fold_embed(self.cards_in_play, dealer)

    def as_embed(self):
        embed = Embed()
        embed.set_author(
            name="Blackjack {} ({})".format(
                self.player.display_name, "lost" if self.game_over else "playing"
            ),
            url=self.player.avatar_url,
        )
        if self.game_over:
            embed.add_field(
                name="Last card drawn", value=str(self.cards_in_play.last())
            )
            embed.set_footer(
                text="{} points in your hand. You failed to stay under 21".format(
                    self.cards_in_play.score()
                )
            )
        else:
            embed.add_field(name="Cards on the table", value=str(self.cards_in_play))
            embed.set_footer(
                text="{} points in your hand. Draw or fold please".format(
                    self.cards_in_play.score()
                )
            )
        return embed

    def __str__(self):
        return "Blackjack with {}\nThese cards are on the table: {}".format(
            self.player.display_name, self.cards_in_play
        )
