from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class Bed(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"bed_with_pillow", "bed_without_pillow"},
            initial_state="bed_with_pillow",
            interactable_states=interactable_states,
        )

        self.add_transition(
            "bed_with_pillow",
            "put_pillow_away",
            "bed_without_pillow",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "bed_without_pillow",
            "get_pillow_back",
            "bed_with_pillow",
            AlwaysAllowRule(),
        )
