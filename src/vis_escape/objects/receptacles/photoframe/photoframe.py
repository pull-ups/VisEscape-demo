from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule, TriggerActiveRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class PhotoFrame(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"hang", "drop"},
            initial_state="hang",
            interactable_states=interactable_states,
        )

        self.add_transition("hang", "drop", "drop", AlwaysAllowRule())
        self.add_transition("drop", "hang", "hang", AlwaysAllowRule())
