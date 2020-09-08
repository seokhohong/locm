def fix_draft(cards1, cards2):
    d = DraftPhase()
    d._decks = [cards1, cards2]
    return d

class DraftPhase:
    def __init__(self):
        self._chosen_cards = []
        self._decks = []

    def decks(self):
        return self._decks