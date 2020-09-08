from ai.ai import BasicAI
from game.match import Match


def run():
    ais = BasicAI()
    match = Match([ais, ais])
    match.play_match()

if __name__ == '__main__':
    run()

