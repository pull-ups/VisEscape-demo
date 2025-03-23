from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class Table(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"food_original", "food_cut"},
            initial_state="food_original",
            interactable_states=interactable_states,
        )
