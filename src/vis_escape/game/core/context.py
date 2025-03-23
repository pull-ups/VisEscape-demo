from collections import OrderedDict
from typing import Dict, Set

from vis_escape.objects.item import Item


class GameContext:
    def __init__(self):
        self.player_inventory: Dict[str, Item] = {}
        self.triggers: OrderedDict[str, bool] = {}

    def get_triggers(self) -> Dict[str, bool]:
        return self.triggers

    def get_active_triggers(self) -> list[str]:
        """Returns a list of trigger names that are currently True"""
        return [name for name, state in self.triggers.items() if state]

    def get_player_inventory_str(self) -> Set[str]:
        return set(self.player_inventory.keys())

    def peek_last_trigger(self) -> tuple[str, bool]:
        """Returns the last trigger and its state as a tuple (name, state) without removing it
        Returns ("", False) if triggers is empty"""
        try:
            return next(reversed(self.triggers.items()))
        except StopIteration:
            return ("", False)

    def add_to_player_inventory(self, item_name: str, item: Item):
        self.player_inventory[item_name] = item

    def remove_from_player_inventory(self, item_name: str) -> Item:
        if item_name not in self.player_inventory:
            raise ValueError(f"Item '{item_name}' not found in inventory")
        return self.player_inventory.pop(item_name)
