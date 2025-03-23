from typing import Dict, List, Optional, Set

from vis_escape.game.core.context import GameContext
from vis_escape.game.core.rules import TransitionRule
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

from .item import Item


class Receptacle:
    def __init__(
        self,
        id: str,
        possible_states: Set[str],
        initial_state: str,
        interactable_states: Dict[str, Set[str]],
    ):
        self._id = id
        self._possible_states = possible_states
        self._current_state = initial_state
        self._interactable_states = interactable_states
        self._contained_items = set(interactable_states.keys())
        self._transitions: Dict[str, Dict[str, tuple[str, TransitionRule]]] = {}

    def add_transition(
        self, from_state: str, action: str, to_state: str, rule: TransitionRule
    ):
        if from_state not in self._transitions:
            self._transitions[from_state] = {}
        self._transitions[from_state][action] = (to_state, rule)

    def add_item(self, item: Item) -> bool:
        self._contained_items.add(item)
        return True

    def remove_item(self, item: Item) -> bool:
        self._contained_items.discard(item)
        return True

    @property
    def id(self) -> str:
        return self._id

    @property
    def current_state(self) -> str:
        return self._current_state

    def get_total_states(self) -> Set[str]:
        return self._possible_states

    def get_total_transitions(self) -> Dict[str, Dict[str, tuple[str, TransitionRule]]]:
        transitions = []
        for from_state, actions in self._transitions.items():
            for action, (to_state, rule) in actions.items():
                transitions.append(
                    {
                        "from_state": from_state,
                        "action": action,
                        "to_state": to_state,
                        "rule": str(rule),
                    }
                )
        return transitions

    def get_interactable_items_in_current_state(self):
        interactable_items_in_currnet_state = set()
        for item, interactable_state in self._interactable_states.items():
            if self._current_state in interactable_state:
                interactable_items_in_currnet_state.add(item)

        return list(interactable_items_in_currnet_state)

    def get_actions(self) -> Set[str]:
        base_actions = set(self._transitions.get(self._current_state, {}).keys())
        for item in self._contained_items:
            if (
                item in self._interactable_states
                and self._current_state in self._interactable_states[item]
            ):
                base_actions.update(item.get_actions())
        return base_actions

    @property
    def current_state(self) -> str:
        return self._current_state

    def set_current_state(self, state: str):
        self._current_state = state
        return self.get_full_state()

    def get_full_state(self) -> dict:
        return {
            "receptacle_state": self._current_state,
            "interactable_items": sorted(
                item.item_name
                for item in self.get_interactable_items_in_current_state()
            ),
            "contained_items": sorted(
                [item._item_name for item in self._contained_items]
            ),
        }

    def pick_item(self, item_name: str, context: GameContext) -> Optional[Item]:
        interactable_items_str = [
            item.item_name for item in self.get_interactable_items_in_current_state()
        ]
        if item_name not in interactable_items_str:
            return None

        for item in self.get_interactable_items_in_current_state():
            if item.item_name == item_name:
                self._contained_items.remove(item)
                self._interactable_states.pop(item)

                # trigger handling
                trigger_name = f"picked_{item.item_name}"
                context.triggers[trigger_name] = True

                # inventory update
                context.add_to_player_inventory(item_name, item)
                return item
        return None

    def use_item(self, item_name: str, context: GameContext) -> Optional[Item]:
        if item_name not in context.get_player_inventory_str():
            return None

        for k, v in context.player_inventory.items():
            if item_name == k:
                if (
                    self.id == v.appliable_receptacle
                    and self.current_state == v.appliable_state
                ):
                    trigger_name = f"used_{item_name}"
                    context.triggers[trigger_name] = True
        item = context.remove_from_player_inventory(item_name)
        return item

    def handle_action(self, action: str, context: GameContext) -> str:
        interactable_items = self.get_interactable_items_in_current_state()
        for item in interactable_items:
            if isinstance(item, NonKeyLock):
                if item.answer.lower() == action.lower():
                    next_state, rule = self._transitions[self._current_state]["unlock"]
                    self._current_state = next_state
                    return self.get_full_state()

        if " " in action:
            action_type = action.split(" ")[0]
            target_item_name = action.split(" ")[1]
            if action_type == "pick":
                interactable_items_str = [
                    item.item_name
                    for item in self.get_interactable_items_in_current_state()
                ]
                if target_item_name in interactable_items_str:
                    item = self.pick_item(target_item_name, context)
                    print(f"Picked {item.item_name}")
                else:
                    raise ValueError(
                        f"Error: {target_item_name} is not in the current state"
                    )
                return self.get_full_state()
            elif action_type == "use":  ###keyLock
                if (self._current_state in self._transitions) and (
                    action in self._transitions[self._current_state]
                ):
                    next_state, rule = self._transitions[self._current_state][action]
                    if rule.evaluate(context):
                        item = self.use_item(target_item_name, context)
                        self._current_state = next_state
                return self.get_full_state()
            else:
                if (self._current_state in self._transitions) and (
                    action in self._transitions[self._current_state]
                ):
                    next_state, rule = self._transitions[self._current_state][action]
                    if rule.evaluate(context):
                        self._current_state = next_state
                context.triggers[action] = True
                return self.get_full_state()
        else:
            if (
                self._current_state in self._transitions
                and action in self._transitions[self._current_state]
            ):
                next_state, rule = self._transitions[self._current_state][action]
                if rule.evaluate(context):
                    self._current_state = next_state

            return self.get_full_state()


class SequenceReceptacle(Receptacle):
    def __init__(
        self,
        id: str,
        possible_states: Set[str],
        initial_state: str,
        interactable_states: Dict[str, Set[str]],
        correct_sequence: List[str],
    ):
        super().__init__(id, possible_states, initial_state, interactable_states)
        self._correct_sequence = correct_sequence
        self._current_sequence: List[str] = []

    def handle_action(self, action: str, context: GameContext) -> str:
        self._current_sequence.append(action)

        if self._is_correct_sequence():
            if (
                self._current_state in self._transitions
                and "sequence_complete" in self._transitions[self._current_state]
            ):
                next_state, rule = self._transitions[self._current_state][
                    "sequence_complete"
                ]
                if rule.evaluate(context):
                    self._current_state = next_state
                    self.reset_sequence()

        return super().handle_action(action, context)

    def _is_correct_sequence(self) -> bool:
        if len(self._current_sequence) < len(self._correct_sequence):
            return False

        sequence_to_check = self._current_sequence[-len(self._correct_sequence) :]
        return sequence_to_check == self._correct_sequence

    def reset_sequence(self):
        self._current_sequence = []
