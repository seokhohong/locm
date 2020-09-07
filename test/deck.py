import unittest
from game.constants import Constants

class TestDeckMethods(unittest.TestCase):

    def test_card(self):
        slimer = Constants.CARDS[1]
        self.assertEquals(slimer.get_attack(), 2)
        self.assertEquals(slimer.my_health_change(), 1)
        slithering_nightmare = Constants.CARDS[82]
        self.assertEquals(slithering_nightmare.name(), "Slithering Nightmare")

if __name__ == '__main__':
    unittest.main()

