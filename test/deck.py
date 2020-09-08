import unittest

from game.ability import Ability
from game.constants import Constants

class TestDeckMethods(unittest.TestCase):

    def test_card(self):
        slimer = Constants.CARDS[1]
        self.assertEqual(slimer.get_attack(), 2)
        self.assertEqual(slimer.my_health_change(), 1)
        self.assertEqual(slimer.card_id(), 1)
        slithering_nightmare = Constants.CARDS[82]
        self.assertEqual(slithering_nightmare.name(), "Slithering Nightmare")
        self.assertEqual(slithering_nightmare.has_abil(Ability.DRAIN), True)
        cursed_sword = Constants.CARDS[146]
        self.assertEqual(cursed_sword.attack_mod(), -2)
        self.assertEqual(cursed_sword.defense_mod(), -2)
        self.assertEqual(cursed_sword.opp_health_change(), -2)
        grow_wings = Constants.CARDS[140]
        self.assertTrue(grow_wings.is_green_item())
        self.assertFalse(grow_wings.is_blue_item())
        self.assertFalse(grow_wings.is_red_item())

    def test_duplicate(self):
        slimer = Constants.CARDS[1]
        slimer_copy = slimer.reinstantiate()
        self.assertNotEqual(slimer.instance_id(), slimer_copy.instance_id())

    def test_basic(self):
        slimer = Constants.CARDS[1]
        self.assertTrue(slimer.is_creature())

if __name__ == '__main__':
    unittest.main()

