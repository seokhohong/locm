from game.action import InsufficientManaException, IllegalSummonException
from game.card import Card
from game.constants import Constants
from game.creature import BoardCreature

from copy import copy


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
        self.handLimit = Constants.MAX_CARDS_IN_HAND + (0 if card_id == 0 else Constants.SECOND_PLAYER_MAX_CARD_BONUS)
        self.draw_cards(Constants.INITIAL_HAND_SIZE + (0 if card_id == 0 else Constants.SECOND_PLAYER_CARD_BONUS), 0)

    def suicide_runes(self):
        if len(self._runes) > 0:
            last_rune = self._runes[-1]
            self._health = last_rune
            self._runes = self._runes[:-1]
        else:
            self._health = 0

    def initialize_turn(self, player_turn):
        self.reset_mana()

        for creature in self.board():
            creature.reset_attack()
            creature._lastTurnDefense = creature.defense()

        self.draw_cards(self.next_turn_draw(), player_turn)
        self._nextTurnDraw = 1

    def draw_cards(self, num_draw, player_turn):
        for i in range(num_draw):
            # don't draw
            if self.num_hand_cards() == Constants.MAX_CARDS_IN_HAND:
                break
            if len(self._deck) == 0 or player_turn >= Constants.PLAYER_TURNLIMIT:
                self.suicide_runes()
                continue
            if len(self._hand) == self.handLimit:
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
                self._runes.remove(self._runes[i])

    def health(self):
        return self._health

    def modify_mana(self, mod):
        self._currentMana += mod

    def num_board_creatures(self):
        return len(self.board())

    def from_hand(self, card: Card):
        for c in self._hand:
            if c.card_id() == card.card_id():
                return c
        assert False

    def num_hand_cards(self):
        return len(self._hand)

    def get_creature_by_index(self, index):
        return self._board[index]

    def get_creature_and_index(self, target: BoardCreature):
        for i, creature in enumerate(self._board):
            if creature.instance_id() == target.instance_id():
                return creature, i
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

    # includes cost, and hp modifiers
    def use_card(self, card: Card):
        for c in self._hand:
            # matching card type
            if c.card_id() == card.card_id():
                self._hand.remove(c)
        self.modify_mana(-card.cost())
        if self._currentMana < 0:
            raise InsufficientManaException(card)
        self.modify_health(card.my_health_change())
        self._nextTurnDraw += card.card_draw()

    def enemy_use_card(self, card: Card):
        self.modify_health(card.opp_health_change())

    def remove_from_board(self, creature: BoardCreature):
        # the instance on the board that matches the perceived creature (param and board may be diff copies)
        board_creature = self.get_creature_and_index(creature)[0]
        self._board.remove(board_creature)
        self._graveyard.append(board_creature)

    def update_board(self, index, creature: BoardCreature):
        assert creature is not None
        self._board[index] = creature

    def summon(self, card: Card):
        if self.num_board_creatures() == Constants.MAX_CREATURES_IN_LINE:
            raise IllegalSummonException(card)
        self.use_card(card)
        creature = BoardCreature(card, 0)
        self._board.append(creature)

    def get_hand(self):
        return copy(self._hand)

    def deck_size(self):
        return len(self._deck)