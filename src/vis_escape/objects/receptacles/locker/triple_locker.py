from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.receptacle import Receptacle


class TripleLocker(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        possible_states = {
            f"{first}_{second}_{third}"
            for first in ["first_closed", "first_open"]
            for second in ["second_closed", "second_open"]
            for third in ["third_closed", "third_open"]
        }

        super().__init__(
            id=id,
            possible_states=possible_states,
            initial_state="first_closed_second_closed_third_closed",
            interactable_states=interactable_states,
        )

        self.add_transition(
            "first_closed_second_closed_third_closed",
            "open_first_locker",
            "first_open_second_closed_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed_third_closed",
            "close_first_locker",
            "first_closed_second_closed_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open_third_closed",
            "open_first_locker",
            "first_open_second_open_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open_third_closed",
            "close_first_locker",
            "first_closed_second_open_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_closed_third_open",
            "open_first_locker",
            "first_open_second_closed_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed_third_open",
            "close_first_locker",
            "first_closed_second_closed_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open_third_open",
            "open_first_locker",
            "first_open_second_open_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open_third_open",
            "close_first_locker",
            "first_closed_second_open_third_open",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_closed_second_closed_third_closed",
            "open_second_locker",
            "first_closed_second_open_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open_third_closed",
            "close_second_locker",
            "first_closed_second_closed_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed_third_closed",
            "open_second_locker",
            "first_open_second_open_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open_third_closed",
            "close_second_locker",
            "first_open_second_closed_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_closed_third_open",
            "open_second_locker",
            "first_closed_second_open_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open_third_open",
            "close_second_locker",
            "first_closed_second_closed_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed_third_open",
            "open_second_locker",
            "first_open_second_open_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open_third_open",
            "close_second_locker",
            "first_open_second_closed_third_open",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_closed_second_closed_third_closed",
            "open_third_locker",
            "first_closed_second_closed_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_closed_third_open",
            "close_third_locker",
            "first_closed_second_closed_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open_third_closed",
            "open_third_locker",
            "first_closed_second_open_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open_third_open",
            "close_third_locker",
            "first_closed_second_open_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed_third_closed",
            "open_third_locker",
            "first_open_second_closed_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed_third_open",
            "close_third_locker",
            "first_open_second_closed_third_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open_third_closed",
            "open_third_locker",
            "first_open_second_open_third_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open_third_open",
            "close_third_locker",
            "first_open_second_open_third_closed",
            AlwaysAllowRule(),
        )
