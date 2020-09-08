from enum import Enum

from game.card import Card, Item
from copy import copy

from game.creature import BoardCreature


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
    SUMMON = 0,
    ATTACK = 1,
    USE = 2


class Action:
    def __init__(self, action_type: ActionType):
        self._type = action_type

    def type(self):
        return self._type


class Summon(Action):
    def __init__(self, card: Card):
        super(Summon, self).__init__(ActionType.SUMMON)
        self._card = card

    def card(self):
        return self._card

    def __str__(self):
        return 'SUMMON ' + str(self._card)

    def command_str(self):
        return 'SUMMON ' + str(self._card.instance_id())


class Use(Action):
    def __init__(self, item: Item, target: BoardCreature):
        super(Use, self).__init__(ActionType.USE)
        self._item = item
        self._target = target

    def item(self):
        return self._item

    def has_target(self):
        return self._target is not None

    def target(self):
        return self._target

    def command_str(self):
        if self.has_target():
            return 'USE ' + str(self._item.instance_id()) + ' ' + str(self.target().instance_id())
        else:
            return 'USE ' + str(self._item.instance_id())

class Attack(Action):
    def __init__(self, attacker: BoardCreature, defender: BoardCreature):
        super(Attack, self).__init__(ActionType.ATTACK)
        self._attacker = attacker
        self._defender = defender

    def attacker(self):
        return self._attacker

    def defender(self):
        return self._defender

    def attacking_player(self):
        return self._defender is None

    def command_str(self):
        if not self.attacking_player():
            return 'ATTACK ' + str(self._attacker.instance_id()) + ' ' + str(self.defender().instance_id())
        else:
            return 'ATTACK ' + str(self._attacker.instance_id())

class IllegalActionException(Exception):
    def __init__(self, msg):
        self._msg = msg
        pass

    def __str__(self):
        return self._msg

    def __repr__(self):
        return self._msg


class InsufficientManaException(Exception):
    def __init__(self, card: Card):
        super(InsufficientManaException, self).__init__("Not enough mana to play " + card.name())
        self._card = card

    def card(self):
        return self._card

class IllegalAttackException(Exception):
    def __init__(self, creature: BoardCreature):
        super(IllegalAttackException, self).__init__("Cannot Perform Attack: " + creature.name())

class IllegalSummonException(Exception):
    def __init__(self, card: Card):
        super(IllegalSummonException, self).__init__("Cannot Perform Summon: " + card.name())