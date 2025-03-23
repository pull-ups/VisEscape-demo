from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule, TriggerActiveRule
from vis_escape.objects.item import Item
from vis_escape.objects.receptacle import Receptacle


class NonLockBox(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
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
    from vis_escape.objects.item import Item

    context = GameContext()

    apple = Item(item_type="apple", item_name="red_apple")
    book = Item(item_type="book", item_name="diary")

    print("=== Test 1: Basic Box ===")
    simple_box = NonLockBox(id="simple_box", interactable_states={"apple": {"open"}})
    simple_box.add_item(apple)
    print(f"Initial state: {simple_box.get_full_state()}")
    print(f"Try to pick apple while closed: {simple_box.pick_item('apple', context)}")
    simple_box.handle_action("open", context)
    print(f"After opening: {simple_box.get_full_state()}")
    picked_apple = simple_box.pick_item("apple", context)
    print(f"Picked apple: {picked_apple.item_name if picked_apple else None}")
    print(f"Final state: {simple_box.get_full_state()}\n")

    print("=== Test 2: Multi-item Box ===")
    storage_box = NonLockBox(
        id="storage_box", interactable_states={"apple": {"open"}, "book": {"open"}}
    )

    print("Adding multiple items...")
    storage_box.add_item(apple)
    storage_box.add_item(book)
    print(f"Current state: {storage_box.get_full_state()}")
    print(f"Available actions: {storage_box.get_actions()}\n")


if __name__ == "__main__":
    main()
