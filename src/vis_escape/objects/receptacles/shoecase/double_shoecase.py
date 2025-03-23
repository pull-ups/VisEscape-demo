from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.receptacle import Receptacle


class DoubleShoecase(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={
                "first_closed_second_closed",
                "first_open_second_closed",
                "first_closed_second_open",
                "first_open_second_open",
            },
            initial_state="first_closed_second_closed",
            interactable_states=interactable_states,
        )

        self.add_transition(
            "first_closed_second_closed",
            "open_first",
            "first_open_second_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed",
            "close_first",
            "first_closed_second_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open",
            "open_first",
            "first_open_second_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open",
            "close_first",
            "first_closed_second_open",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_closed_second_closed",
            "open_second",
            "first_closed_second_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open",
            "close_second",
            "first_closed_second_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed",
            "open_second",
            "first_open_second_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open",
            "close_second",
            "first_open_second_closed",
            AlwaysAllowRule(),
        )
