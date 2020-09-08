from game.constants import Constants
from game.draft import DraftPhase
from game.ability import Ability
from game.action import ActionResult, ActionType, Action, Summon, Attack, Use, IllegalAttackException
from game.card import Item
from game.creature import BoardCreature
from game.gamer import Gamer

from copy import copy

class GameState:
    def __init__(self, draft: DraftPhase):
        self._turn = -1
        self._winner = -1
        # starts second ai, but first turn shifts back to first
        self._currentPlayer = 1
        self._players = [Gamer(0, draft.decks()[0]), Gamer(1, draft.decks()[1])]

        self._card_id_map = {}
        for i in range(2):
            for card in draft.decks()[i]:
                self._card_id_map[card.instance_id()] = card

    def check_win(self):
        if self._players[1 - self._currentPlayer].health() <= 0:
            self._winner = self._currentPlayer
        if self._players[self._currentPlayer].health() <= 0:
            self._winner = 1 - self._currentPlayer

    def has_winner(self):
        return self._winner != -1

    def winner(self):
        return self._winner

    def get_first_player(self):
        return self._players[0]

    def get_second_player(self):
        return self._players[1]

    def resolve_attack_player(self, attacker: BoardCreature):
        if not attacker.can_attack():
            raise IllegalAttackException(attacker)

        attacker_after = copy(attacker)
        attacker_after.mark_attack()

        healthGain = attacker.attack() if attacker.has_abil(Ability.DRAIN) else 0
        healthTaken = -attacker.attack()

        self.current_player().modify_health(healthGain)
        self.non_current_player().modify_health(healthTaken)
        result = ActionResult(attacker_after, None, healthGain, healthTaken)
        #result.defenderDefenseChange = healthTaken
        return result

    def resolve_attack(self, attacker: BoardCreature, defender: BoardCreature):
        if not attacker.can_attack():
            raise IllegalAttackException(attacker)

        # check legality based on guard
        for creature in self.non_current_player().board():
            if creature.has_abil(Ability.GUARD) and not defender.has_abil(Ability.GUARD):
                raise IllegalAttackException(attacker)

        attacker_after = copy(attacker)
        defender_after = copy(defender)

        attacker_after.mark_attack()

        if defender.get_abilities().has_ward():
            defender_after.get_abilities().set_ward(attacker.attack() == 0)
        if attacker.get_abilities().has_ward():
            attacker_after.get_abilities().set_ward(defender.defense() == 0)

        damage_given = 0 if defender.get_abilities().has_ward() else attacker.attack()
        damage_taken = 0 if attacker.get_abilities().has_ward() else defender.attack()
        health_gain = 0
        health_taken = 0

        # attacking
        if damage_given >= defender.defense():
            defender_after = None

        if attacker.get_abilities().has_breakthrough() and defender_after is None:
            health_taken = defender.defense() - damage_given
        if attacker.get_abilities().has_lethal() and damage_given > 0:
            defender_after = None
        if attacker.get_abilities().has_drain() and damage_given > 0:
            health_gain = attacker.attack()
        if defender_after is not None:
            defender_after.take_damage(damage_given)

        # defending
        if damage_taken >= attacker.defense():
            attacker_after = None
        if defender.get_abilities().has_lethal() and damage_taken > 0:
            attacker_after = None
        if attacker_after is not None:
            attacker_after.take_damage(damage_taken)

        self.current_player().modify_health(health_gain)
        self.non_current_player().modify_health(health_taken)

        return ActionResult(attacker_after, defender_after, health_gain, health_taken)

    def resolve_use(self, item: Item, target: BoardCreature):
        target_after = copy(target)
        target_after.apply_item(item)

        if target_after.defense() <= 0:
            target_after = None

        return ActionResult(target_after, None, 0, 0)

    def resolve_use_player(self, item: Item):
        return ActionResult(None, None, item.my_health_change(), item.opp_health_change())

    def open_next_turn(self):
        self.check_win()

        # next ai
        self._currentPlayer = 1 - self._currentPlayer
        current_player_obj = self._players[self._currentPlayer]
        #current_player_obj._performed_actions = []
        self.current_player().initialize_turn(self._turn // 2)

        # drawing can kill
        self.check_win()

    def non_current_player(self):
        return self._players[1 - self._currentPlayer]

    def current_player(self):
        return self._players[self._currentPlayer]

    def _advance_state_summon(self, action: Summon):
        card = action.card()
        current_player_obj = self.current_player()

        assert (Constants.LANES == 1)

        current_player_obj.summon(card)
        self.non_current_player().enemy_use_card(card)

        return ActionResult(None, None, card.my_health_change(), card.opp_health_change())

    def _advance_state_attack(self, action: Attack):
        current_player_obj = self.current_player()
        attacker, indexatt = current_player_obj.get_creature_and_index(action.attacker())

        # attacking ai
        if action.attacking_player():
            result = self.resolve_attack_player(attacker)
        else:
            defender, indexdef = self.non_current_player().get_creature_and_index(action.defender())

            result = self.resolve_attack(attacker, defender)

            if result.defender_died():
                self.non_current_player().remove_from_board(defender)
            else:
                self.non_current_player().update_board(indexdef, result.defender())

            if result.attacker_died():
                current_player_obj.remove_from_board(attacker)
            else:
                current_player_obj.update_board(indexatt, result.attacker())
        return result

    def _advance_state_use(self, action: Use):
        item = action.item()
        current_player_obj = self.current_player()
        current_player_obj.use_card(item)
        self.non_current_player().enemy_use_card(item)
        if item.is_green_item():
            target_creature, target_index = current_player_obj.get_creature_and_index(action.target())
            result = self.resolve_use(item, target_creature)
            # interface for result is weird
            current_player_obj.update_board(target_index, result.attacker())

        else:  # red or blue cards
            if action.item().is_blue_item():
                result = self.resolve_use_player(item)
            else:
                # using on creature
                target_creature, target_index = self.non_current_player().get_creature_and_index(action.target())
                result = self.resolve_use(item, target_creature)
                if result.defender_died():
                    self.non_current_player().remove_from_board(target_creature)
                else:
                    self.non_current_player().update_board(target_index, result.defender())
        return result

    def perform_action(self, action: Action):
        if action.type() == ActionType.SUMMON:
            result = self._advance_state_summon(action)
        elif action.type() == ActionType.ATTACK:
            result = self._advance_state_attack(action)
        else:  # item
            result = self._advance_state_use(action)

        action.result = result

        self.check_win()
