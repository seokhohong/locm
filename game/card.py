from game.ability import Ability, ability_set_from_str
from copy import copy

def card_from_strarray(data):
    abilities = data[6]
    card_id = int(data[0])
    cost = int(data[3])
    attack = int(data[4])
    defense = int(data[5])
    mhc = int(data[7])
    ohc = int(data[8])
    card_draw = int(data[9])
    if data[2] == 'creature':
        return Creature(card_id, data[1], data[2], cost, attack, defense, abilities, mhc, ohc, card_draw, data[10])
    else:
        return Item(card_id, data[1], data[2], cost, attack, defense, abilities, mhc, ohc, card_draw, data[10])



class Card:
    _instance_tracker = -1

    @classmethod
    def _create_instance(cls):
        Card._instance_tracker += 1
        return Card._instance_tracker

    def __init__(self, card_id, name, card_type, cost, abilities,
                 my_health_change, opp_health_change, card_draw, desc):
        self._card_id = card_id
        self._instance_id = Card._create_instance()
        self._name = name
        self._card_type = card_type
        self._cost = cost
        self._my_health_change = my_health_change
        self._opp_health_change = opp_health_change
        self._abilities = ability_set_from_str(abilities)
        self._card_draw = card_draw
        self._desc = desc

    def reinstantiate(self):
        a_copy = copy(self)
        a_copy._instance_id = Card._create_instance()
        return a_copy

    def name(self):
        return self._name

    def cost(self):
        return self._cost

    def card_id(self):
        return self._card_id

    def instance_id(self):
        return self._instance_id

    def is_item(self):
        return 'item' in self._card_type

    def is_creature(self):
        return self._card_type == 'creature'

    def my_health_change(self):
        return self._my_health_change

    def opp_health_change(self):
        return self._opp_health_change

    def card_draw(self):
        return self._card_draw

    def get_abilities(self):
        return copy(self._abilities)

    def __repr__(self):
        return self.name()

class Item(Card):
    def __init__(self, card_id, name, card_type, cost, attack_mod, def_mod, abilities, mhc, ohc, card_draw, desc):
        super(Item, self).__init__(card_id, name, card_type, cost, abilities, mhc, ohc, card_draw, desc)
        assert ('item' in card_type)
        self._attack_mod = attack_mod
        self._def_mod = def_mod

    def attack_mod(self):
        return self._attack_mod

    def defense_mod(self):
        return self._def_mod

    def is_green_item(self):
        return self._card_type == 'itemGreen'

    def is_red_item(self):
        return self._card_type == 'itemRed'

    def is_blue_item(self):
        return self._card_type == 'itemBlue'

    def affects_abil(self, abil: Ability):
        return self._abilities.has_abil(abil)


class Creature(Card):
    def __init__(self, card_id, name, card_type,
                 cost, attack, defense, abilities, mhc, ohc, card_draw, desc):
        super(Creature, self).__init__(card_id, name, card_type, cost, abilities, mhc, ohc, card_draw, desc)
        assert (card_type == 'creature')
        self._attack = attack
        self._defense = defense

        self._can_attack = self.has_abil(Ability.BREAKTHROUGH)
        self._has_attacked = False

    def defense(self):
        return self._defense

    def get_attack(self):
        return self._attack

    def attack(self, other):
        other._defense -= self.get_attack()
        self._has_attacked = True

    def apply_item(self, item, is_friendly):
        friendly_multiplier = 1 if is_friendly else -1
        self._attack += item.attack_mod() * friendly_multiplier
        self._defense += item.defense_mod() * friendly_multiplier

    def is_dead(self):
        return self._defense <= 0

    def can_attack(self):
        return not self._has_attacked

    def has_abil(self, abil: Ability):
        return self._abilities.has_abil(abil)

