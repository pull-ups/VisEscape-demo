from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule, TriggerActiveRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class Hourglass(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"before_flip", "after_flip"},
            initial_state="before_flip",
            interactable_states=interactable_states,
        )

        self.add_transition(
            "before_flip", "flip_hourglass", "after_flip", AlwaysAllowRule()
        )
        self.add_transition(
            "after_flip", "flip_hourglass", "before_flip", AlwaysAllowRule()
        )
