from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from vis_escape.game.core.context import GameContext
from vis_escape.objects.item import (
    Item,
    PickableItem,
    QuizItem,
)
from vis_escape.objects.receptacle import Receptacle


@dataclass
class ItemState:
    game_item: Item
    current_state: str

    def __init__(self, game_item: Item):
        if not isinstance(game_item, Item):
            raise ValueError("ItemState can only manage Item objects")
        self.game_item = game_item


        if isinstance(game_item, QuizItem):
            self.current_state = "not_solved"
        else:
            self.current_state = "default"

    def get_current_state(self) -> str:
        return self.current_state


    def get_question_text(self) -> str:
        return self.game_item.question_text

    def solve_question(self, try_answer: str) -> bool:
        if isinstance(self.game_item, QuizItem):
            if self.game_item.check_answer(try_answer):
                self.current_state = "solved"
                return True
        return False


@dataclass
class ReceptacleState:
    game_receptacle: Receptacle
    current_state: dict
    item_states: Dict[str, ItemState]

    def __init__(self, game_receptacle: Receptacle):
        self.game_receptacle = game_receptacle
        self.current_state = game_receptacle.get_full_state()
        self.item_states = {}
        for item in game_receptacle._contained_items:
            if isinstance(item, Item):
                self.item_states[item.item_name] = ItemState(item)

    def get_available_actions(self) -> List[str]:
        return list(self.game_receptacle.get_actions())

    def get_item_state(self, item_name: str) -> Optional[ItemState]:
        return self.item_states.get(item_name)

    def apply_action(self, action: str, context: GameContext) -> bool:
        if action.startswith("inspect "):
            item_name = action.split("inspect ")[1]
            item_state = self.get_item_state(item_name)
            if item_state:
                return True
        else:
            next_state = self.game_receptacle.handle_action(action, context)
            if next_state != self.current_state:
                self.current_state = next_state
                return True
            return False

    def change_state(self, state: str):
        next_state = self.game_receptacle.set_current_state(state)
        self.current_state = next_state
        return True


class WallState:
    def __init__(self, wall_id: str, receptacles: List[ReceptacleState]):
        self.wall_id = wall_id
        self.receptacles = {obj.game_receptacle.id: obj for obj in receptacles}

    def __init__(self, wall_id: str, receptacles: List[Receptacle]):
        self.wall_id = wall_id
        self.receptacles = {obj.id: ReceptacleState(obj) for obj in receptacles}

    def get_receptacle(self, receptacle_id: str) -> Optional[ReceptacleState]:
        return self.receptacles.get(receptacle_id)

    def get_state_snapshot(self) -> dict:
        return {
            "wall_id": self.wall_id,
            "receptacle_states": {
                obj_id: obj.current_state for obj_id, obj in self.receptacles.items()
            },
        }


class GameState:
    def __init__(self, walls: List[WallState], initial_direction: str = "NORTH"):
        self.walls = {wall.wall_id: wall for wall in walls}
        self.current_wall = (
            initial_direction
            if initial_direction in self.walls
            else list(self.walls.keys())[0]
        )
        self.context = GameContext()
        self.current_view = "WALL"
        self.inspected_receptacle = None
        self.current_item = None
        self.clear_condition = None
        self.game_clear = False

    def set_hint_message(self, hint_message: str):
        if isinstance(hint_message, dict):
            self.hint_message = hint_message
        elif isinstance(hint_message, Callable):
            self.hint_message = hint_message
        else:
            raise ValueError("hint_message must be a dictionary or a callable function")

    def get_hint_message(self, last):
        if isinstance(self.hint_message, dict):
            return self.hint_message[self.context.peek_last_trigger()]
        elif isinstance(self.hint_message, Callable):
            return self.hint_message(last)
        return self.hint_message

    def get_item_by_name(self, item_name: str) -> Optional[Item]:
        for wall in self.walls.values():
            for receptacle in wall.receptacles.values():
                for item_state in receptacle.item_states.values():
                    if item_state.game_item.item_name == item_name:
                        return item_state.game_item
        return None

    def get_receptacle_by_id(self, receptacle_id: str) -> Optional[Receptacle]:
        for wall in self.walls.values():
            for receptacle in wall.receptacles.values():
                if receptacle.game_receptacle.id == receptacle_id:
                    return receptacle
        return None

    def export_current_state(self) -> dict:
        state = {"NORTH": {}, "SOUTH": {}, "EAST": {}, "WEST": {}}

        for wall_state in self.walls.values():
            direction = wall_state.wall_id
            wall_objects = {}

            for receptacle_state in wall_state.receptacles.values():
                receptacle_info = {
                    "type": "receptacle",
                    "state": receptacle_state.current_state,
                    "items": [],
                }

                for item_state in receptacle_state.item_states.values():
                    item_info = {
                        "name": item_state.game_item.item_name,
                        "state": item_state.current_state,
                    }
                    receptacle_info["items"].append(item_info)

                wall_objects[receptacle_state.game_receptacle.id] = receptacle_info

            state[direction] = wall_objects

        return state

    def turn_right(self):
        wall_ids = list(self.walls.keys())
        current_idx = wall_ids.index(self.current_wall)
        self.current_wall = wall_ids[(current_idx + 1) % len(wall_ids)]

    def turn_left(self):
        wall_ids = list(self.walls.keys())
        current_idx = wall_ids.index(self.current_wall)
        self.current_wall = wall_ids[(current_idx - 1) % len(wall_ids)]

    def get_current_wall(self) -> WallState:
        return self.walls[self.current_wall]

    def get_available_actions(self) -> List[str]:
        actions = []
        wall_directions = ["NORTH", "EAST", "SOUTH", "WEST"]
        current_idx = wall_directions.index(self.current_wall)
        for direction in wall_directions:
            if direction != self.current_wall:
                actions.append(f"turn_to_{direction.lower()}")

        if self.current_view == "WALL":
            current_wall = self.get_current_wall()
            actions.extend(
                [f"inspect {obj_id}" for obj_id in current_wall.receptacles.keys()]
            )

        elif self.current_view == "RECEPTACLE":  # receptacle view
            actions.append("step_back")
            if self.inspected_receptacle:
                receptacle = self.get_current_wall().get_receptacle(
                    self.inspected_receptacle
                )
                if not receptacle:
                    return []
                for action in receptacle.get_available_actions():
                    if "use" not in action:
                        actions.append(action)

                for item_name, item in self.context.player_inventory.items():
                    actions.append(f"use {item_name}")

                receptacle_interactable_items = (
                    receptacle.game_receptacle.get_interactable_items_in_current_state()
                )
                for item in receptacle_interactable_items:
                    actions.extend(item.get_actions())
        elif self.current_view == "ITEM":
            current_item = (
                self.get_current_wall()
                .get_receptacle(self.inspected_receptacle)
                .get_item_state(self.current_item)
                .game_item
            )
            actions.append("step_back")
            for item_name, item in self.context.player_inventory.items():
                actions.append(f"use {item_name}")

        return list(dict.fromkeys(actions))

    def _get_turns_to_target(self, target_direction: str) -> List[str]:
        wall_directions = ["NORTH", "EAST", "SOUTH", "WEST"]
        current_idx = wall_directions.index(self.current_wall)
        target_idx = wall_directions.index(target_direction)

        clockwise_steps = (target_idx - current_idx) % 4
        counter_clockwise_steps = (current_idx - target_idx) % 4

        turns = []
        if clockwise_steps <= counter_clockwise_steps:
            turns.extend(["turn_right"] * clockwise_steps)
        else:
            turns.extend(["turn_left"] * counter_clockwise_steps)
        return turns

    def handle_action(self, action: str) -> bool:
        result = False
        if action.startswith("turn_to_"):
            target_direction = action.split("turn_to_")[1].upper()
            if target_direction == self.current_wall:
                return False

            for turn in self._get_turns_to_target(target_direction):
                if turn == "turn_right":
                    self.turn_right()
                else:
                    self.turn_left()

            self.current_view = "WALL"
            self.inspected_receptacle = None
            self.current_item = None
            result = True
            return result

        if self.current_view == "WALL":
            if action.startswith("inspect "):
                receptacle_id = action.split("inspect ")[1]
                if self.get_current_wall().get_receptacle(receptacle_id):
                    self.current_view = "RECEPTACLE"
                    self.inspected_receptacle = receptacle_id
                    result = True

        elif self.current_view == "RECEPTACLE":
            if action not in self.get_available_actions():
                return False
            if action == "step_back":
                self.current_view = "WALL"
                self.inspected_receptacle = None
                result = True
            elif action.startswith("inspect "):
                item_name = action.split("inspect ")[1]
                receptacle = self.get_current_wall().get_receptacle(
                    self.inspected_receptacle
                )
                if receptacle and receptacle.get_item_state(item_name):
                    self.current_view = "ITEM"
                    self.current_item = item_name
                    result = True
                else:
                    raise ValueError(
                        f"item {item_name} is not in the receptacle {self.inspected_receptacle}."
                    )
            elif action.startswith("use "):
                item_to_use_name = action.split("use ")[1]
                item_to_use = self.get_item_by_name(item_to_use_name)
                receptacle = self.get_current_wall().get_receptacle(
                    self.inspected_receptacle
                )

                # Find the first lock item in the receptacle
                lock_item = None
                for item_name, item_state in receptacle.item_states.items():
                    if "lock" in item_state.game_item.item_type.lower():
                        lock_item = item_state
                        break
                if (
                    item_to_use
                    and lock_item
                    and isinstance(lock_item.game_item, QuizItem)
                ):
                    if lock_item.solve_question(action):
                        trigger_name = f"used {item_to_use_name}"
                        self.context.triggers[trigger_name] = True
                        result = self._handle_action_on_receptacle(
                            self.inspected_receptacle, action, item_to_use
                        )
                        receptacle.game_receptacle.remove_item(item_to_use)
                elif item_to_use and isinstance(item_to_use, PickableItem):
                    current_receptacle = self.get_receptacle_by_id(
                        self.inspected_receptacle
                    )
                    possible_transitions = (
                        current_receptacle.game_receptacle.get_total_transitions()
                    )
                    if any(t["action"] == action for t in possible_transitions):
                        trigger_name = f"used {item_to_use_name}"
                        self.context.triggers[trigger_name] = True
                        result = self._handle_action_on_receptacle(
                            self.inspected_receptacle, action, item_to_use
                        )

            else:
                if " " in action:
                    item_to_use = self.get_item_by_name(action.split(" ")[1])
                else:
                    item_to_use = None
                result = self._handle_action_on_receptacle(
                    self.inspected_receptacle, action, item_to_use
                )

        elif self.current_view == "ITEM":  # QuizItem and StaticItem
            if not self.current_item:
                return False
            receptacle = self.get_current_wall().get_receptacle(
                self.inspected_receptacle
            )
            item_state = receptacle.get_item_state(self.current_item)

            if action == "step_back":
                self.current_view = "RECEPTACLE"
                self.current_item = None
                result = True
            elif action.startswith("use "):
                item_to_use_name = action.split("use ")[1]
                item_to_use = self.get_item_by_name(item_to_use_name)
                if item_to_use and isinstance(item_state.game_item, QuizItem):
                    if item_state.solve_question(action):
                        trigger_name = f"used {item_to_use_name}"
                        self.context.triggers[trigger_name] = True
                        result = self._handle_action_on_receptacle(
                            self.inspected_receptacle, action, item_to_use
                        )

                        receptacle.game_receptacle.remove_item(item_to_use)
                        self.current_view = "RECEPTACLE"
                        self.current_item = None
            else:
                if item_state.solve_question(action):
                    trigger_name = f"solved_{self.current_item}"
                    self.context.triggers[trigger_name] = True
                    target_receptacle_id = item_state.game_item.appliable_receptacle
                    target_receptacle = self.get_current_wall().get_receptacle(
                        target_receptacle_id
                    )
                    if target_receptacle:
                        result = target_receptacle.apply_action(action, self.context)
                        self.current_view = "RECEPTACLE"
                        self.current_item = None
                    else:
                        print(f"Error: Can't find {target_receptacle_id}.")
                        result = False
        else:
            raise ValueError(f"Invalid view mode: {self.current_view}")
        if result:
            self.check_game_clear()
        return result

    def _handle_action_on_receptacle(
        self, receptacle_id: str, action: str, item_to_use: Item
    ) -> bool:
        if item_to_use:
            current_wall = self.get_current_wall()
            current_receptacle = self.get_receptacle_by_id(receptacle_id)

            target_receptacle = self.get_receptacle_by_id(
                item_to_use.appliable_receptacle
            )
            if target_receptacle:
                if (
                    target_receptacle.current_state["receptacle_state"]
                    == item_to_use.appliable_state
                ):
                    self.context.triggers[action] = True

                    return target_receptacle.change_state(item_to_use.after_solve_state)
            else:
                return current_receptacle.apply_action(action, self.context)
            return False
        else:
            current_receptacle = self.get_receptacle_by_id(receptacle_id)
            if current_receptacle:
                return current_receptacle.apply_action(action, self.context)
            return False

    def set_clear_condition(self, receptacle_id: str, state: str):
        self.clear_condition = {"receptacle_id": receptacle_id, "state": state}

    def check_game_clear(self) -> bool:
        if self.clear_condition is None:
            return False

        game_clear_receptacle = self.get_receptacle_by_id(
            self.clear_condition["receptacle_id"]
        )
        if game_clear_receptacle:
            if (
                game_clear_receptacle.current_state["receptacle_state"]
                == self.clear_condition["state"]
            ):
                self.game_clear = True
                print("Game Clear!!")
                return True
        return False

    def get_current_location(self) -> str:
        """Returns a string describing the current location/view in the game.

        Returns:
            str: Description of current location based on the view mode
        """
        if self.current_view == "WALL":
            return f"At {self.current_wall} side of room, "
        elif self.current_view == "RECEPTACLE":
            if self.inspected_receptacle:
                receptacle = self.get_current_wall().get_receptacle(
                    self.inspected_receptacle
                )
                if receptacle:
                    return f"At {receptacle.game_receptacle.id}, "
        elif self.current_view == "ITEM":
            if self.current_item:
                receptacle = self.get_current_wall().get_receptacle(
                    self.inspected_receptacle
                )
                if receptacle:
                    item_state = receptacle.get_item_state(self.current_item)
                    if item_state:
                        return f"At {item_state.game_item.item_name}, "

        return "Unknown location"  # fallback for any unexpected states
