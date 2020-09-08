import unittest
from copy import deepcopy

from game.ability import Ability
from game.constants import Constants
from game.draft import DraftPhase, fix_draft
from game.state import GameState
from game.action import Action, ActionType, Summon, InsufficientManaException, Attack, Use, IllegalAttackException


class TestStateMethods(unittest.TestCase):

    def test_summon(self):
        slimer = Constants.CARDS[1]
        scuttler = Constants.CARDS[2]
        decks = [[slimer], [scuttler]]
        draft = fix_draft(*decks)

        state = GameState(draft)
        state.open_next_turn()
        first_player = state.get_first_player()
        second_player = state.get_second_player()
        self.assertEqual(first_player.deck_size(), 0)
        self.assertEqual(second_player.deck_size(), 0)

        summon = Summon(first_player.from_hand(slimer))
        state.perform_action(summon)
        self.assertEqual(len(first_player.board()), 1)
        self.assertEqual(first_player.board()[0].name(), slimer.name())
        # rune effect of trying to draw 4, +1 from slimer
        self.assertEqual(first_player.health(), 11)

    def test_attack(self):
        slimer = Constants.CARDS[1]
        scuttler = Constants.CARDS[2]
        decks = [[slimer] * 6, [scuttler] * 6]
        draft = fix_draft(*decks)

        state = GameState(draft)
        state.open_next_turn()
        first_player = state.get_first_player()
        second_player = state.get_second_player()

        state.perform_action(Summon(first_player.from_hand(slimer)))
        with self.assertRaises(IllegalAttackException):
            state.perform_action(Attack(first_player.get_creature_by_index(0), None))

        with self.assertRaises(InsufficientManaException):
            # not enough mana for this
            state.perform_action(Summon(first_player.from_hand(slimer)))

        self.assertEqual(first_player.health(), Constants.INITIAL_HEALTH + 1)

        # second ai turn
        state.open_next_turn()
        for i in range(2):
            state.perform_action(Summon(second_player.from_hand(scuttler)))

        # does damage to opp
        self.assertEqual(first_player.health(), Constants.INITIAL_HEALTH - 1)

        with self.assertRaises(InsufficientManaException):
            # not enough mana for this
            state.perform_action(Summon(second_player.from_hand(scuttler)))

        state.open_next_turn()
        a_slimer = first_player.get_creature_by_index(0)
        a_target = second_player.get_creature_by_index(0)
        state.perform_action(Attack(a_slimer, a_target))

        # they should kill each other
        self.assertEqual(first_player.num_board_creatures(), 0)
        self.assertEqual(second_player.num_board_creatures(), 1)

    def test_charge(self):
        slimer = Constants.CARDS[1]
        wings = Constants.CARDS[140]
        scuttler = Constants.CARDS[2]
        decks = [[wings] + [slimer] * 6, [scuttler] * 7]
        draft = fix_draft(*decks)

        state = GameState(draft)
        first_player = state.get_first_player()
        second_player = state.get_second_player()
        for i in range(5):
            state.open_next_turn()

        self.assertEqual(first_player.current_mana(), 3)
        state.perform_action(Summon(first_player.from_hand(slimer)))
        slimer_creature = first_player.get_creature_by_index(0)
        self.assertEqual(first_player.get_creature_by_index(0), slimer_creature)
        state.perform_action(Use(first_player.from_hand(wings), slimer_creature))

        # update as a result of item change
        slimer_creature = first_player.get_creature_by_index(0)
        self.assertTrue(slimer_creature.can_attack())
        self.assertEqual(first_player.num_board_creatures(), 1)

        self.assertTrue(slimer_creature.has_abil(Ability.CHARGE))
        self.assertEqual(first_player.get_creature_by_index(0).name(), slimer_creature.name())
        state.perform_action(Attack(slimer_creature, None))

        self.assertEqual(first_player.health(), Constants.INITIAL_HEALTH + 1)
        self.assertEqual(second_player.health(), Constants.INITIAL_HEALTH - 2)

    def test_breakthrough(self):
        slimer = Constants.CARDS[1]
        protein = Constants.CARDS[117]
        scuttler = Constants.CARDS[2]
        decks = [[slimer] * 8 + [protein], [scuttler] * 9]
        draft = fix_draft(*decks)

        state = GameState(draft)
        first_player = state.get_first_player()
        second_player = state.get_second_player()
        for i in range(5):
            state.open_next_turn()

        state.perform_action(Summon(first_player.from_hand(slimer)))
        state.perform_action(Use(first_player.from_hand(protein), first_player.get_creature_by_index(0)))
        self.assertTrue(first_player.get_creature_by_index(0).has_abil(Ability.BREAKTHROUGH))
        state.open_next_turn()
        state.perform_action(Summon(second_player.from_hand(scuttler)))
        state.open_next_turn()
        state.perform_action(Attack(first_player.get_creature_by_index(0), second_player.get_creature_by_index(0)))
        self.assertEqual(second_player.health(), Constants.INITIAL_HEALTH - 1)

    def test_drain(self):
        slimer = Constants.CARDS[1]
        scuttler = Constants.CARDS[2]
        imp = Constants.CARDS[38]
        decks = [[slimer] * 8 + [imp], [scuttler] * 9]
        draft = fix_draft(*decks)

        state = GameState(draft)
        first_player = state.get_first_player()
        second_player = state.get_second_player()
        for i in range(5):
            state.open_next_turn()

        state.perform_action(Summon(first_player.from_hand(imp)))
        state.open_next_turn()
        state.open_next_turn()
        state.perform_action(Attack(first_player.get_creature_by_index(0), None))
        self.assertEqual(first_player.health(), Constants.INITIAL_HEALTH + 1)

    def test_guard(self):
        slimer = Constants.CARDS[1]
        scuttler = Constants.CARDS[2]
        prowler = Constants.CARDS[49]
        decks = [[slimer] * 8 + [prowler], [scuttler] * 9]
        draft = fix_draft(*decks)

        state = GameState(draft)
        first_player = state.get_first_player()
        second_player = state.get_second_player()
        for i in range(5):
            state.open_next_turn()

        state.perform_action(Summon(first_player.from_hand(prowler)))
        state.perform_action(Summon(first_player.from_hand(slimer)))
        state.open_next_turn()
        state.perform_action(Summon(second_player.from_hand(scuttler)))
        state.perform_action(Summon(second_player.from_hand(scuttler)))
        state.open_next_turn()
        state.open_next_turn()
        self.assertEqual(first_player.get_creature_by_index(0).name(), prowler.name())
        # must attack creature with guard first
        with self.assertRaises(IllegalAttackException):
            state.perform_action(Attack(second_player.get_creature_by_index(0), first_player.get_creature_by_index(1)))

        state.perform_action(Attack(second_player.get_creature_by_index(0), first_player.get_creature_by_index(0)))
        # now we can attack the other creature without guard
        state.perform_action(Attack(second_player.get_creature_by_index(0), first_player.get_creature_by_index(0)))

    def test_ward(self):
        slimer = Constants.CARDS[1]
        scuttler = Constants.CARDS[2]
        sapling = Constants.CARDS[7]
        decks = [[slimer] * 8 + [sapling], [scuttler] * 9]
        draft = fix_draft(*decks)

        state = GameState(draft)
        first_player = state.get_first_player()
        second_player = state.get_second_player()
        for i in range(5):
            state.open_next_turn()

        state.perform_action(Summon(first_player.from_hand(sapling)))
        state.open_next_turn()
        state.perform_action(Summon(second_player.from_hand(scuttler)))
        state.open_next_turn()
        state.open_next_turn()
        self.assertEqual(first_player.get_creature_by_index(0).defense(), 2)
        state.perform_action(Attack(second_player.get_creature_by_index(0), first_player.get_creature_by_index(0)))
        # check for annulled ward
        self.assertEqual(first_player.get_creature_by_index(0).defense(), 2)


    def test_draw(self):
        slimer = Constants.CARDS[1]
        scuttler = Constants.CARDS[2]
        toad = Constants.CARDS[28]
        decks = [[slimer] * 8 + [toad], [scuttler] * 9]
        draft = fix_draft(*decks)

        state = GameState(draft)
        first_player = state.get_first_player()
        second_player = state.get_second_player()
        for i in range(3):
            state.open_next_turn()

        self.assertEqual(first_player.num_hand_cards(), 6)
        state.perform_action(Summon(first_player.from_hand(toad)))
        state.open_next_turn()
        state.open_next_turn()
        self.assertEqual(first_player.num_hand_cards(), 7)

        for i in range(5):
            state.open_next_turn()

        self.assertEqual(first_player.num_hand_cards(), Constants.MAX_CARDS_IN_HAND)
        self.assertEqual(second_player.num_hand_cards(), Constants.MAX_CARDS_IN_HAND)

    def test_deepcopy(self):
        slimer = Constants.CARDS[1]
        scuttler = Constants.CARDS[2]
        decks = [[slimer], [scuttler]]
        draft = fix_draft(*decks)

        state = GameState(draft)
        state.open_next_turn()

        copy_state = deepcopy(state)

        self.assertEqual(copy_state.current_player().get_hand()[0].instance_id(), state.current_player().get_hand()[0].instance_id())

if __name__ == '__main__':
    unittest.main()

