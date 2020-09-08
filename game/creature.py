from game.card import Card, Creature, Item
from game.ability import Ability


class BoardCreature:
    def __init__(self, card: Creature, lane):
        self._instance_id = card.instance_id()
        self._attack = card.get_attack()
        self._defense = card.defense()
        self._abilities = card.get_abilities()
        self._can_attack = self.has_abil(Ability.CHARGE)
        self._has_attacked = False
        self._cost = card.cost()
        self._lastTurnDefense = self._defense
        self._my_health_change = card.my_health_change()
        self._opp_health_change = card.opp_health_change()
        self._card_draw = card.card_draw()
        self._base_card = card
        self._lane = lane

    def instance_id(self):
        return self._instance_id

    def name(self):
        return self._base_card.name()

    def attack(self):
        return self._attack

    def defense(self):
        return self._defense

    def reset_attack(self):
        self._can_attack = True
        self._has_attacked = False

    def apply_item(self, item: Item):
        if item.is_green_item():
            for abil in Ability:
                if item.affects_abil(abil):
                    self.set_abil(abil, True)
            # TODO: deal with charging abil
        else:
            # if the item deals damage, remove ward
            if self.has_abil(Ability.WARD) and item.defense_mod() < 0:
                self.set_abil(Ability.WARD, False)
            else:
                self._defense += item.defense_mod()

        self._attack = max(0, self.attack() + item.attack_mod())

    def mark_attack(self):
        self._can_attack = False
        self._has_attacked = True

    def can_attack(self):
        if self._has_attacked:
            self._can_attack = False
        return self._can_attack

    def set_can_attack(self, value):
        self._can_attack = value

    def set_has_attacked(self, value):
        self._has_attacked = value

    def has_attacked(self):
        return self._has_attacked

    def get_abilities(self):
        return self._abilities

    def take_damage(self, amount):
        self._defense -= amount

    def has_abil(self, abil: Ability):
        return self._abilities.has_abil(abil)

    def set_abil(self, abil: Ability, add: bool):
        self._abilities.set_abil(abil, add)
        if abil == Ability.CHARGE and add:
            self._can_attack = True

    def __str__(self):
        return self.name() + ' (' + str(self._cost) + ') ' + str(self.attack()) + ' / ' + str(self.defense()) + ' | ' + str(self._abilities)

