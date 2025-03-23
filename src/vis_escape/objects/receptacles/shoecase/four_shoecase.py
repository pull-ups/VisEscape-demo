from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.receptacle import Receptacle


class FourShoecase(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        possible_states = {
            f"{first}_{second}_{third}_{fourth}"
            for first in ["first_closed", "first_open"]
            for second in ["second_closed", "second_open"]
            for third in ["third_closed", "third_open"]
            for fourth in ["fourth_closed", "fourth_open"]
        }

        super().__init__(
            id=id,
            possible_states=possible_states,
            initial_state="first_closed_second_closed_third_closed_fourth_closed",
            interactable_states=interactable_states,
        )

        for state in possible_states:
            if "first_closed" in state:
                new_state = state.replace("first_closed", "first_open")
                self.add_transition(state, "open_first", new_state, AlwaysAllowRule())
            elif "first_open" in state:
                new_state = state.replace("first_open", "first_closed")
                self.add_transition(state, "close_first", new_state, AlwaysAllowRule())

            if "second_closed" in state:
                new_state = state.replace("second_closed", "second_open")
                self.add_transition(state, "open_second", new_state, AlwaysAllowRule())
            elif "second_open" in state:
                new_state = state.replace("second_open", "second_closed")
                self.add_transition(state, "close_second", new_state, AlwaysAllowRule())

            if "third_closed" in state:
                new_state = state.replace("third_closed", "third_open")
                self.add_transition(state, "open_third", new_state, AlwaysAllowRule())
            elif "third_open" in state:
                new_state = state.replace("third_open", "third_closed")
                self.add_transition(state, "close_third", new_state, AlwaysAllowRule())

            if "fourth_closed" in state:
                new_state = state.replace("fourth_closed", "fourth_open")
                self.add_transition(state, "open_fourth", new_state, AlwaysAllowRule())
            elif "fourth_open" in state:
                new_state = state.replace("fourth_open", "fourth_closed")
                self.add_transition(state, "close_fourth", new_state, AlwaysAllowRule())
