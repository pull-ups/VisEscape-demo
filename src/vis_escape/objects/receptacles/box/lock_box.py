from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule, TriggerActiveRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class LockBox(Receptacle):
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
    from vis_escape.objects.item import Item

    context = GameContext()

    key = Item(item_type="key", item_name="treasure_key")
    apple = Item(item_type="apple", item_name="red_apple")
    book = Item(item_type="book", item_name="diary")

    print("=== Test 1: Basic Box with Key ===")
    key_box = LockBox(id="treasure_box", interactable_states={"key": {"open"}})

    key_box.add_item(key)
    print(f"Initial state: {key_box.get_full_state()}")
    print(f"Try to pick key while closed: {key_box.pick_item('key', context)}")
    key_box.handle_action("open", context)
    print(f"After opening: {key_box.get_full_state()}")
    picked_key = key_box.pick_item("key", context)
    print(f"Picked key: {picked_key.item_name if picked_key else None}")
    print(f"Final state: {key_box.get_full_state()}\n")

    print("=== Test 2: Multi-item Box ===")
    storage_box = LockBox(
        id="storage_box",
        interactable_states={"key": {"open"}, "apple": {"open"}, "book": {"open"}},
    )

    print("Adding multiple items...")
    storage_box.add_item(key)
    storage_box.add_item(apple)
    storage_box.add_item(book)
    print(f"Current state: {storage_box.get_full_state()}")
    print(f"Available actions: {storage_box.get_actions()}\n")

    print("=== Test 3: Lock/Unlock Mechanism ===")
    locked_box = LockBox(id="locked_box", interactable_states={"apple": {"open"}})
    locked_box.add_item(apple)
    locked_box._current_state = "locked"
    print(f"Initial locked state: {locked_box.get_full_state()}")
    print(f"Available actions: {locked_box.get_actions()}")

    print("\nTrying to unlock without key...")
    locked_box.handle_action("unlock", context)
    print(f"State after unlock attempt: {locked_box.get_full_state()}")

    print("\nTrying to unlock with key...")
    context.triggers["has_key"] = True
    locked_box.handle_action("unlock", context)
    print(f"State after unlock with key: {locked_box.get_full_state()}")
    print(f"Available actions: {locked_box.get_actions()}\n")


if __name__ == "__main__":
    main()
