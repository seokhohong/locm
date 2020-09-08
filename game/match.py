from game.constants import Constants
from game.draft import fix_draft
import random

from game.state import GameState
from copy import copy

class Match:
    def __init__(self, ais, seed=0):
        self._ais = ais
        self._draft_decks = {}
        for ai in self._ais:
            self._draft_decks[ai] = []
        random.seed(seed)

    def play_match(self):
        self._play_draft()
        draftphase = fix_draft(self._draft_decks[self._ais[0]], self._draft_decks[self._ais[1]])
        game = GameState(draftphase)

        for turn in range(100):
            for ai in self._ais:
                game.open_next_turn()
                actions = ai.play(game)
                for action in actions:
                    game.perform_action(action)

                if game.has_winner():
                    print('Winner!', game.winner())

        return game.winner()

    def _play_draft(self):
        card_list = list(Constants.CARDS.values())
        for i in range(Constants.CARDS_IN_DRAFT):
            options = random.sample(card_list, Constants.DRAFT_OPTIONS)
            for ai in self._ais:
                # copy the card so we get a new instance
                self._draft_decks[ai].append(ai.draft(options).reinstantiate())
