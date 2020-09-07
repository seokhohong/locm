from game.constants import Constants


class Gamer:
    def __init__(self, card_id, deck):
        self._id = card_id
        self._hand = []
        self._deck = deck
        self._board = []
        self._graveyard = []
        self._health = Constants.INITIAL_HEALTH
        self._maxMana = 1 if card_id == 1 and Constants.SECOND_PLAYER_MANA_BONUS_TURNS > 0 else 0
        self._currentMana = self._maxMana
        self._nextTurnDraw = 1
        self._runes = [5, 10, 15, 20, 25]

        self.bonusManaTurns = Constants.SECOND_PLAYER_MANA_BONUS_TURNS if card_id == 1 else 0
        self.handLimit = Constants.MAX_CARDS_IN_HAND + 0 if card_id == 0 else Constants.SECOND_PLAYER_MAX_CARD_BONUS
        self.draw_cards(Constants.INITIAL_HAND_SIZE + 0 if card_id == 0 else Constants.SECOND_PLAYER_CARD_BONUS, 0)

    def suicide_runes(self):
        if len(self._runes) > 0:
            last_rune = self._runes[-1]
            self._health = last_rune
            self._runes = self._runes[:-1]
        else:
            self._health = 0

    def draw_cards(self, n, player_turn):
        for i in range(n):
            if len(self._deck) == 0 or player_turn >= Constants.PLAYER_TURNLIMIT:
                self.suicide_runes()
                continue
            if len(self._hand) == self._hand.handLimit:
                break
            draw_card = self._deck.pop()
            self._hand.append(draw_card)

    def modify_health(self, mod):
        self._health += mod
        if mod >= 0:
            return
        for i in range(len(self._runes) - 1, -1, -1):
            if self._health <= self._runes[i]:
                self._nextTurnDraw += 1
                self._runes.remove(i)

    def modify_mana(self, mod):
        self._currentMana += mod

    def num_board_creatures(self):
        return len(self.board())

    def spend_card(self, card):
        self._hand.remove(card)

    def get_creature_and_index(self, target_id):
        for i, creature in enumerate(self._board):
            if creature.id == target_id:
                return i, creature
        assert False

    def next_rune(self):
        if len(self._runes) == 0:
            return 0
        return self._runes[-1]

    def reset_mana(self):
        if self._maxMana < Constants.MAX_MANA + (1 if self.bonusManaTurns > 0 else 0):
            self._maxMana += 1
        if self.bonusManaTurns > 0 and self.current_mana() == 0:
            self.bonusManaTurns -= 1
            if self.bonusManaTurns == 0:
                self._maxMana -= 1
        self._currentMana = self._maxMana

    def board(self):
        return self._board

    def current_mana(self):
        return self._currentMana

    def next_turn_draw(self):
        return self._nextTurnDraw

    def set_next_turn_draw(self, value):
        self._nextTurnDraw = value

    def remove_from_board(self, creature_index):
        self._graveyard.add(board.remove(creature_index))
