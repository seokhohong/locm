from enum import Enum

from game.card import Card
from copy import copy


class ActionResult:
    def __init__(self, attacker_after, defender_after, health_gain, health_taken):
        self._attacker_after = attacker_after
        self._defender_after = defender_after
        self._health_gain = health_gain
        self._health_taken = health_taken

    def defender(self):
        return self._defender_after

    def attacker(self):
        return self._attacker_after

    def defender_died(self):
        return self._defender_after is None

    def attacker_died(self):
        return self._attacker_after is None

    def health_gain(self):
        return self._health_gain

    def health_taken(self):
        return self._health_taken

class ActionType(Enum):
    SUMMON=0,
    ATTACK=1,
    USE=2

class Action:
    def __init__(self, card: Card, type: ActionType, args):
        self._type = type
        self._args = []
        self._card = card

    def type(self):
        return self._type

    def card(self):
        return self._card

    def args(self):
        return copy(self._args)