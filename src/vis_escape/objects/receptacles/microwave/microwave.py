from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.receptacle import Receptacle


class Microwave(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"closed", "open"},
            initial_state="closed",
            interactable_states=interactable_states,
        )

        self.add_transition("closed", "open", "open", AlwaysAllowRule())
        self.add_transition("open", "close", "closed", AlwaysAllowRule())
