from game.card import Card, Creature
from game.ability import Ability


class BoardCreature:
    def __init__(self, card: Creature, lane):
        self._id = card.id()
        self._base_id = card.instance_id()
        self._attack = card.get_attack()
        self._defense = card.defense()
        self._abilities = card.get_abilities()
        self._can_attack = self._abilities.has_attack()
        self._has_attacked = False
        self._cost = card.cost()
        self._lastTurnDefense = self._defense
        self._my_health_change = card.my_health_change()
        self._opp_health_change = card.opp_health_change()
        self._card_draw = card.card_draw()
        self._base_card = card
        self._lane = lane

    def attack(self):
        return self._attack

    def defense(self):
        return self._defense

    def mark_attack(self):
        self._can_attack = False
        self._has_attacked = True

    def can_attack(self):
        return self._can_attack

    def set_can_attack(self, value):
        self._can_attack = value

    def set_has_attacked(self, value):
        self._has_attacked = value

    def set_abilities(self, ability_set):
        self._abilities = ability_set

    def get_abilities(self):
        return self._abilities

    def take_damage(self, amount):
        self._defense -= amount

    def has_abil(self, abil: Ability):
        return self._abilities.has_abil(abil)

    def set_abil(self, abil: Ability, value):
        self._abilities.set_abil(abil, value)