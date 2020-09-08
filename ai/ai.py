from game.action import Summon, Use, Attack
from game.constants import Constants
from game.state import GameState
from copy import deepcopy

class BasicAI:
    def __init__(self):
        pass

    def draft(self, options):
        return options[0]

    def play(self, state: GameState):
        # copy to make decisions
        state = deepcopy(state)
        my_player = state.current_player()
        opp_player = state.non_current_player()
        actions = []

        for card in my_player.get_hand():
            if my_player.current_mana() >= card.cost():
                if card.is_creature() and my_player.num_board_creatures() < Constants.MAX_CREATURES_IN_LINE:
                    actions.append(Summon(card))
                    state.perform_action(actions[-1])
                elif card.is_item():
                    if card.is_green_item():
                        for target in my_player.board():
                            actions.append(Use(card, target))
                            state.perform_action(actions[-1])
                            break
                    elif card.is_blue_item():
                        actions.append(Use(card, None))
                        state.perform_action(actions[-1])
                    elif card.is_red_item():
                        for target in opp_player.board():
                            actions.append(Use(card, target))
                            state.perform_action(actions[-1])
                            break
        for creature in my_player.board():
            if creature.can_attack():
                targets = opp_player.board()
                if len(targets) > 0:
                    actions.append(Attack(creature, targets[0]))
                else:
                    actions.append(Attack(creature, None))
                state.perform_action(actions[-1])

        return actions