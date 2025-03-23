from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.receptacle import Receptacle


class NoneLockDoor(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]] = None):
        if interactable_states is None:
            interactable_states = {}

        super().__init__(
            id=id,
            possible_states={"closed", "open"},
            initial_state="closed",
            interactable_states=interactable_states,
        )

        self.add_transition("closed", "open", "open", AlwaysAllowRule())
        self.add_transition("open", "close", "closed", AlwaysAllowRule())


def main():
    from vis_escape.game.core.context import GameContext

    context = GameContext()

    print("=== Test 1: Basic Door Operations ===")
    door = NoneLockDoor(id="front_door")
    print(f"Initial state: {door.get_full_state()}")
    print(f"Available actions: {door.get_actions()}")

    door.handle_action("open", context)
    print(f"After opening: {door.get_full_state()}")

    door.handle_action("close", context)
    print(f"After closing: {door.get_full_state()}\n")


if __name__ == "__main__":
    main()
