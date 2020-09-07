from game.constants import Constants
from game.draft import DraftPhase
from game.ability import Ability
from game.action import ActionResult, ActionType
from game.card import Item
from game.creature import BoardCreature
from game.gamer import Gamer

from copy import copy

class GameState:
    def __init__(self, draft: DraftPhase):
        self._turn = -1
        self._winner = -1
        self._currentPlayer = 1
        self._players = [Gamer(0, draft.decks()[0]), Gamer(1, draft.decks()[1])]

        self._card_id_map = {}
        for i in range(2):
            for card in draft.decks()[i]:
                self._card_id_map[card.id()] = card

    def check_win(self):
        if self._players[1 - self._currentPlayer].health() <= 0:
            self._winner = self._currentPlayer
        if self._players[self._currentPlayer].health() <= 0:
            self._winner = 1 - self._currentPlayer

    def resolve_attack_player(self, attacker: BoardCreature):
        assert(attacker.can_attack())

        attacker_after = copy(attacker)
        attacker_after.mark_attack()

        healthGain = attacker.attack() if attacker.has_abil(Ability.DRAIN) else 0
        healthTaken = -attacker.attack()

        result = ActionResult(attacker_after, None, healthGain, healthTaken)
        #result.defenderDefenseChange = healthTaken
        return result

    def resolve_attack(self, attacker: BoardCreature, defender: BoardCreature):
        assert(attacker.can_attack())

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
        if damage_given >= defender.defense:
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

        return ActionResult(attacker_after, defender_after, health_gain, health_taken)

    def resolve_use(self, item: Item, target: BoardCreature):
        target_after = copy(target)
        ability_set_after = copy(target_after.get_abilities())
        for abil in Ability:
            ability_set_after.set_abil(abil, ability_set_after.get_abil(abil) or item.get_abilities().get_abil(abil))

        if item.is_green_item():
            if item.has_abil(Ability.CHARGE):
                target_after._can_attack = not target_after.has_attacked()

        target_after._attack = max(0, target.attack() + item.attack_mod())

        target_after.set_abilities(ability_set_after)
        if target_after.has_abil(Ability.WARD) and item.defense_mod() < 0:
            target_after.set_abil(Ability.WARD, False)
        else:
            target_after._defense += item.defense_mod()

        if target_after.defense() <= 0:
            target_after = None

        return ActionResult(target_after)

    def advance_state(self):
        self.check_win()
        current_player_obj = self._players[self._currentPlayer]

        for creature in current_player_obj.board:
            creature.set_can_attack(False)
            creature.set_has_attacked(False)

        self._currentPlayer = 1 - self._currentPlayer
        current_player_obj = self._players[self._currentPlayer]
        #current_player_obj._performed_actions = []
        current_player_obj.reset_mana()

        for creature in current_player_obj.board:
            creature.set_can_attack(True)
            creature._lastTurnDefense = creature.defense()

        current_player_obj.draw_cards(current_player_obj.next_turn_draw, self._turn / 2)
        current_player_obj.set_next_turn_draw(1)
        self.check_win()

    def non_current_player(self):
        return self._players[1 - self._currentPlayer]

    def advance_state_action(self, action: Action):
        current_player_obj = self._players[self._currentPlayer]
        if action.type == ActionType.SUMMON:
            card = self._card_id_map.get(action.args[0])
            current_player_obj.get_hand().remove(card)
            current_player_obj.modify_mana(-card.cost())
            creature = BoardCreature(card, 0) if Constants.LANES == 1 else BoardCreature(card, action.args[1])
            current_player_obj.board.append(creature)
            current_player_obj.modify_health(card.my_health_change())
            self._players[1 - self._currentPlayer].modify_health(card.opp_healthchange())
            current_player_obj.nextTurnDraw += card.cardDraw()

            action.result = ActionResult(creature, None, card.my_health_change(), card.opp_health_change())
        elif action.type == ActionType.ATTACK:
            att, indexatt = current_player_obj.get_creature_and_index(action.args()[0])

            # attacking player
            if action.args()[1] == -1:
                result = self.resolve_attack(att, None)
            else:
                defender, indexdef = current_player_obj.get_creature_and_index(action.args()[1])

                result = self.resolve_attack(att, defender)

                if result.defender_died():
                    self.non_current_player().removeFromBoard(indexdef)
                else:
                    self.non_current_player().board()[indexdef] = result.defender()

            if result.attacker_died():
                current_player_obj.removeFromBoard(indexatt)
            else:
                current_player_obj.board.set(indexatt, result.attacker())

        elif action.type == ActionType.USE:
            item = self._card_id_map[action.args()[0]]
            current_player_obj.spend_card(item)
            current_player_obj.modify_mana(item.cost())
            if item.is_green_item():
                target_creature, target_index = current_player_obj.get_creature_and_index(item.args()[0])
                result = self.resolve_use(item, target_creature)
                current_player_obj.board[target_index] = result.defender()
            else: # red or blue cards
                if action.args()[1] == -1:
                    result = self.resolve_use(item, None)
                else:
                    # using on creature
                    target_creature, target_index = self.non_current_player().get_creature_and_index(item.args[1])
                    result = self.resolve_use(item, target_creature)
                    if result.defender_died():
                        self.non_current_player().remove_from_board(target_index)
                    else:
                        self.non_current_player().board()[target_index] = result.defender()

            current_player_obj.modify_health(result.attacker_health_change())
            self.non_current_player().modify_health(result.defender_health_change())
            current_player_obj.set_next_turn_draw(current_player_obj.next_turn_draw() + item.card_draw())
            action.result = result

            self.check_win()