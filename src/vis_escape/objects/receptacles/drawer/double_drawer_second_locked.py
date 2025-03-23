from typing import Dict, Set

from vis_escape.game.core.rules import AlwaysAllowRule
from vis_escape.objects.receptacle import Receptacle


class DoubleDrawerSecondLocked(Receptacle):
    def __init__(self, id: str, interactable_states: Dict[str, Set[str]]):
        super().__init__(
            id=id,
            possible_states={
                "first_closed_second_locked",
                "first_closed_second_closed",
                "first_closed_second_open",
                "first_open_second_locked",
                "first_open_second_closed",
                "first_open_second_open",
            },
            initial_state="first_closed_second_locked",
            interactable_states=interactable_states,
        )

        self.add_transition(
            "first_closed_second_locked",
            "open_first_drawer",
            "first_open_second_locked",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_closed_second_closed",
            "open_first_drawer",
            "first_open_second_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_closed",
            "open_second_drawer",
            "first_closed_second_open",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_closed_second_open",
            "open_first_drawer",
            "first_open_second_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_closed_second_open",
            "close_second_drawer",
            "first_closed_second_closed",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_open_second_locked",
            "close_first_drawer",
            "first_closed_second_locked",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_open_second_closed",
            "close_first_drawer",
            "first_closed_second_closed",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_closed",
            "open_second_drawer",
            "first_open_second_open",
            AlwaysAllowRule(),
        )

        self.add_transition(
            "first_open_second_open",
            "close_first_drawer",
            "first_closed_second_open",
            AlwaysAllowRule(),
        )
        self.add_transition(
            "first_open_second_open",
            "close_second_drawer",
            "first_open_second_closed",
            AlwaysAllowRule(),
        )


def main():
    from vis_escape.game.core.context import GameContext
    from vis_escape.objects.items.apple.apple import Apple
    from vis_escape.objects.items.book.book import Book
    from vis_escape.objects.items.key.key import Key
    from vis_escape.objects.receptacles.drawer.double_drawer import DoubleDrawer

    context = GameContext()
    door_key = Key(item_type="key", item_name="door_key")
    book = Book(item_type="book", item_name="book")
    apple = Apple(item_type="apple", item_name="apple")

    print("\n=== Test: Drawer State Transitions and Key Pickup ===")
    drawer = DoubleDrawer(
        id="drawer",
        interactable_states={
            door_key.item_name: {"first_closed_second_open", "first_open_second_open"},
            apple.item_name: {"first_closed_second_open", "first_open_second_open"},
            # book.item_name: {"first_open_second_closed", "first_open_second_open"}}
            book.item_name: {"first_open_second_closed"},
        },  # Can't find when first closed
    )

    # Add item to drawer
    drawer.add_item(door_key)
    drawer.add_item(book)
    drawer.add_item(apple)

    print("\nInitial state:", drawer.get_full_state())

    # Drawer state trasition test
    print("\n=== Drawer state trasition test ===")
    drawer.handle_action("open_first_drawer", context)
    print("Opening first drawer:", drawer.get_full_state())

    drawer.handle_action("open_second_drawer", context)
    print("Opening second drawer:", drawer.get_full_state())

    drawer.handle_action("close_first_drawer", context)
    print("Closing first drawer:", drawer.get_full_state())

    # Item pickable state test
    print("\n=== Item pickable state test ===")
    print(
        "Pickable items now:",
        drawer.get_interactable_items_in_current_state(),
    )

    drawer.handle_action("open_first_drawer", context)
    print(
        "Pickable items after opening first drawer:",
        drawer.get_interactable_items_in_current_state(),
    )

    # Item Pickup Test
    print("\n=== Item Pickup Test ===")

    picked_book = drawer.pick_item("book", context)
    print("Getting a book success:", picked_book.item_name)
    print("Remained items:", [item.item_name for item in drawer._contained_items])

    picked_apple = drawer.pick_item("apple", context)
    print("Getting an apple success:", picked_apple.item_name)
    print("Remained items:", [item.item_name for item in drawer._contained_items])

    picked_door_key = drawer.pick_item("door_key", context)
    print("Getting a door key success:", picked_door_key.item_name)
    print("Remained items:", [item.item_name for item in drawer._contained_items])

    # Missed state transition test
    print("\n=== Missed state transition test ===")
    try:
        drawer.handle_action("invalid_action", context)
    except Exception as e:
        print("Missed action test:", str(e))

    # Adding item test
    print("\n=== Adding item test ===")
    new_apple = Apple(item_type="apple", item_name="new_apple")
    drawer.add_item(new_apple)
    print(
        "Items after adding a new apple:",
        [item.item_name for item in drawer._contained_items],
    )


if __name__ == "__main__":
    main()
