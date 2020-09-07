from game.card import card_from_strarray

class Constants:
    LANES = 1
    CARDS = {}

    CARDS_IN_DECK = 30
    CARDS_IN_DRAFT = 60

    INITIAL_HAND_SIZE = 4
    MAX_CARDS_IN_HAND = 8
    SECOND_PLAYER_CARD_BONUS = 1
    SECOND_PLAYER_MAX_CARD_BONUS = 0
    SECOND_PLAYER_MANA_BONUS_TURNS = 1

    MAX_MANA = 12
    INITIAL_HEALTH = 30

    MAX_CREATURES_IN_LINE = 6
    PLAYER_TURNLIMIT = 50

def load_cards():
    with open('../resources/cardlist.txt') as f:
        for line in f:
            components = line.replace('\n', ' ').split(' ; ')
            Constants.CARDS[int(components[0])] = card_from_strarray(components)
load_cards()