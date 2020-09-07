class DraftPhase:
    def __init__(self):
        self._chosen_cards = []
        self._decks = []
    def decks(self):
        return self._decks