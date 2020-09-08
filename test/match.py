import unittest

from ai.ai import BasicAI
from game.match import Match

class TestStateMethods(unittest.TestCase):
    def test_matches(self):
        ais = BasicAI()
        for i in range(1):
            match = Match([ais, ais])
            match.play_match()

if __name__ == '__main__':
    unittest.main()
