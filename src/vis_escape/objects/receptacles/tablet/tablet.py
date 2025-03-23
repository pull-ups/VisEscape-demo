from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule, TriggerActiveRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class Tablet(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"on", "off"},
            initial_state="off",
            interactable_states=interactable_states,
        )

        self.add_transition("on", "turn_off", "off", AlwaysAllowRule())
