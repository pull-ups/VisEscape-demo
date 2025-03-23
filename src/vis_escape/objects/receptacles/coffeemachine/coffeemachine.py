from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule, TriggerActiveRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class CoffeeMachine(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"full", "empty"},
            initial_state="full",
            interactable_states=interactable_states,
        )

        self.add_transition("full", "pour coffee", "empty", AlwaysAllowRule())
