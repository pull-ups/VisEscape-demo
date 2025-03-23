from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule, HasItemRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class LockDoor(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={"closed", "open", "locked"},
            initial_state="locked",
            interactable_states=interactable_states,
        )

        self.add_transition("closed", "open", "open", AlwaysAllowRule())
        self.add_transition("open", "close", "closed", AlwaysAllowRule())


def main():
    from vis_escape.game.core.context import GameContext

    context = GameContext()

    print("=== Test 1: Basic Door Operations ===")
    door = LockDoor(id="front_door")
    print(f"Initial state: {door.get_full_state()}")
    print(f"Available actions: {door.get_actions()}")

    door.handle_action("open", context)
    print(f"After opening: {door.get_full_state()}")

    door.handle_action("close", context)
    print(f"After closing: {door.get_full_state()}\n")

    print("=== Test 2: Lock/Unlock Mechanism ===")
    locked_door = LockDoor(id="locked_door")
    locked_door._current_state = "locked"
    print(f"Initial locked state: {locked_door.get_full_state()}")
    print(f"Available actions: {locked_door.get_actions()}")

    print("\nTrying to unlock without key...")
    locked_door.handle_action("unlock", context)
    print(f"State after unlock attempt: {locked_door.get_full_state()}")

    print("\nTrying to unlock with key...")
    context.triggers["has_key"] = True
    locked_door.handle_action("unlock", context)
    print(f"State after unlock with key: {locked_door.get_full_state()}")
    print(f"Available actions: {locked_door.get_actions()}")


if __name__ == "__main__":
    main()
