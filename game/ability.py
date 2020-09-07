from enum import Enum
class Ability(Enum):
    BREAKTHROUGH = 1
    CHARGE = 2
    DRAIN = 3
    GUARD = 4
    LETHAL = 5
    WARD = 6

def ability_set_from_str(strdata):
    return AbilitySet(strdata[0] == 'B', strdata[1] == 'C', strdata[2] == 'D', strdata[3] == 'G', strdata[4] == 'L', strdata[5] == 'W')

class AbilitySet:
    def __init__(self, b, c, d, g, l, w):
        self._abils = {}
        self._abils[Ability.BREAKTHROUGH] = b
        self._abils[Ability.CHARGE] = c
        self._abils[Ability.DRAIN] = d
        self._abils[Ability.GUARD] = g
        self._abils[Ability.LETHAL] = l
        self._abils[Ability.WARD] = w

    def has_breakthrough(self):
        return self.has_abil(Ability.BREAKTHROUGH)

    def has_charge(self):
        return self.has_abil(Ability.CHARGE)

    def has_drain(self):
        return self.has_abil(Ability.DRAIN)

    def has_guard(self):
        return self.has_abil(Ability.GUARD)

    def has_abil(self, abil):
        return self._abils[abil]

    def set_ward(self, value):
        self._abils[Ability.DRAIN] = value

    def set_abil(self, abil, value):
        self._abils[abil] = value

    def has_ward(self):
        return self.has_abil(Ability.WARD)

    def has_lethal(self):
        return self.has_abil(Ability.LETHAL)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.strdata