import json
import os
import platform
from pathlib import Path
from typing import Dict, Optional

from vis_escape.game.manage.game_state import (
    GameState,
    ItemState,
    ReceptacleState,
    WallState,
)
from vis_escape.game.manage.message_manager import ActionType, MessageManager



class ViewManager:
    def __init__(self, room_asset_dir: str, model_name: str, game_state: GameState, play_mode="ai"):
        """
        Args:
            room_asset_dir: Directory path to room assets
        """
        self.play_mode = play_mode
        self.asset_dir = Path(room_asset_dir)
        self.image_dir = self.asset_dir / "image"
        self.mapping_dir = self.asset_dir / "mapping"
        if play_mode == "ai":
            self.captions_path = (
                self.asset_dir / "captions" / model_name / "image_captions.json"
            )
        self.wall_images: Dict[str, Dict[str, str]] = {}
        self.object_images: Dict[str, Dict[str, str]] = {}
        self.item_images: Dict[str, Dict[str, str]] = {}
        self._load_image_mappings()
        self._load_image_captions()
        self.message_manager = MessageManager()
        self.last_message = {
            "action_message": "",
            "after_state_message": self._get_image_caption(
                self._get_wall_view_image(game_state)
            ),
        }

    def _load_image_mappings(self):
        """Load image mappings

        Current directory structure:
        image_dir/
        ├── wall_view/
        │   ├── NORTH/
        │   │   ├── 0.png
        │   │   ├── 1.png
        │   │   └── ...
        ├── object_view/
        │   ├── front_door/
        │   │   ├── 0.png
        │   │   ├── 1.png
        │   │   └── 2.png
        │   └── ...
        ├── item_view/
        │   ├── quiz_A/
        │   │   ├── 0.png
        │   │   ├── 1.png
        │   │   └── ...
        │   └── ...
        """
        # Load wall image
        walls_dir = self.image_dir / "wall_view"
        for wall_dir in walls_dir.iterdir():
            if wall_dir.is_dir():
                wall_id = wall_dir.name
                self.wall_images[wall_id] = {
                    path.stem: str(path) for path in wall_dir.glob("*.png")
                }

        objects_dir = self.image_dir / "object_view"
        for obj_dir in objects_dir.iterdir():
            if obj_dir.is_dir():
                obj_id = obj_dir.name
                self.object_images[obj_id] = {
                    path.stem: str(path) for path in obj_dir.glob("*.png")
                }
        objects_dir = self.image_dir / "item_view"
        for obj_dir in objects_dir.iterdir():
            if obj_dir.is_dir():
                obj_id = obj_dir.name
                self.item_images[obj_id] = {
                    path.stem: str(path) for path in obj_dir.glob("*.png")
                }

    def _load_image_captions(self):
        if self.play_mode == "ai":
            with open(self.captions_path, "r") as f:
                self.image_captions = json.load(f)
        else:
            self.image_captions = {}

    def _get_image_caption(self, image_path: str) -> Optional[str]:
        if not image_path:
            return None

        path_parts = Path(image_path).parts
        view_type = path_parts[-3]  # wall_view, object_view, item_view
        object_id = path_parts[-2]  # NORTH, cupboard, keylock_A, ...
        image_name = path_parts[-1]  # image.png

        try:
            if view_type == "wall_view":
                return self.image_captions["wall_view"][object_id][image_name]
            elif view_type == "object_view":
                return self.image_captions["object_view"][object_id][image_name]
            elif view_type == "item_view":
                return self.image_captions["item_view"][object_id][image_name]
        except KeyError:
            return None

        return None

    def get_current_view_image(
        self,
        game_state: GameState,
        prev_state: Optional[GameState] = None,
        action: Optional[str] = None,
        verbose: bool = False,
    ) -> str:
        img_path = ""
        if game_state.current_view == "WALL":
            img_path = self._get_wall_view_image(game_state)
            image_caption = self._get_image_caption(img_path)
        elif game_state.current_view == "RECEPTACLE":
            img_path = self._get_receptacle_view_image(game_state)
            image_caption = self._get_image_caption(img_path)
        elif game_state.current_view == "ITEM":
            img_path = self._get_item_view_image(game_state)
            image_caption = self._get_image_caption(img_path)
        else:
            image_caption = self._get_image_caption(img_path)

        if prev_state and action:
            action_type = self._determine_action_type(prev_state, game_state, action)
            self.last_message = self.message_manager.get_transition_message(
                prev_state=prev_state,
                current_state=game_state,
                action_type=action_type,
                image_caption=image_caption,
                action=action,
            )

        if verbose:
            self._print_game_status(game_state, img_path, image_caption)
        return img_path

    def _print_game_status(
        self, game_state: GameState, img_path: str, image_caption: str = ""
    ):
        """Visualize game status"""
        border_width = 200 
        clear_screen()
        print("\033[H")  

        def print_line(content: str = ""):
            padding = border_width - len(content) - 1 if content else border_width
            print(f"│ {content}{' ' * padding}│")

        print(f"{' Game Status ':^{border_width}}")
        print("┌" + "─" * border_width + "┐")

        if game_state.current_view == "WALL":
            print_line(f"VIEW: WALL ({game_state.current_wall})")
            print_line(
                f"Current state: {game_state.get_current_wall().get_state_snapshot()}"
            )
            print_line(f"Available actions: {game_state.get_available_actions()}")
            print_line(f"Inventory: {game_state.context.get_player_inventory_str()}")
            print_line(f"Triggers: {game_state.context.triggers}")
            print_line(f"Image path: {img_path}")
            print_line(f"Image caption: {image_caption}")
            print_line(f"Game clear: {game_state.check_game_clear()}")

        elif game_state.current_view == "RECEPTACLE":
            obj = game_state.get_current_wall().get_receptacle(
                game_state.inspected_receptacle
            )
            print_line(f"VIEW: RECEPTACLE ({game_state.inspected_receptacle})")
            print_line(f"Current state: {obj.game_receptacle.get_full_state()}")
            print_line(f"Available actions: {game_state.get_available_actions()}")
            print_line(
                f"Interactable items: {obj.game_receptacle.get_interactable_items_in_current_state()}"
            )
            print_line(f"Inventory: {game_state.context.get_player_inventory_str()}")
            print_line(f"Triggers: {game_state.context.triggers}")
            print_line(f"Image path: {img_path}")
            print_line(f"Image caption: {image_caption}")
            print_line(f"Game clear: {game_state.check_game_clear()}")
        elif game_state.current_view == "ITEM":
            item = (
                game_state.get_current_wall()
                .get_receptacle(game_state.inspected_receptacle)
                .get_item_state(game_state.current_item)
            )
            print_line(f"VIEW: ITEM ({game_state.current_item})")
            print_line(f"Current state: {item.get_current_state()}")
            print_line(f"Available actions: {game_state.get_available_actions()}")
            print_line(f"Inventory: {game_state.context.get_player_inventory_str()}")
            print_line(f"Triggers: {game_state.context.triggers}")
            print_line(f"Image path: {img_path}")
            print_line(f"Image caption: {image_caption}")
            print_line(f"Game clear: {game_state.check_game_clear()}")

        else:
            raise ValueError(f"Invalid view type: {game_state.current_view}")

        print("└" + "─" * border_width + "┘")

    def _get_wall_view_image(self, game_state: GameState) -> str:
        wall_id = game_state.current_wall
        wall_state = game_state.get_current_wall()

        state_key = self._encode_wall_state(wall_state)

        wall_images = self.wall_images.get(wall_id, {})

        return wall_images.get(state_key, wall_images.get("default", ""))

    def _get_receptacle_view_image(self, game_state: GameState) -> str:
        if not game_state.inspected_receptacle:
            return ""

        obj = game_state.get_current_wall().get_receptacle(
            game_state.inspected_receptacle
        )
        if not obj:
            return ""

        image_filename = self._encode_receptacle_state(
            game_state.inspected_receptacle, obj
        )
        if image_filename:
            return str(
                self.image_dir
                / "object_view"
                / game_state.inspected_receptacle
                / image_filename
            )
        return ""

    def _get_item_view_image(self, game_state: GameState) -> str:
        receptacle_id = game_state.inspected_receptacle
        item_id = game_state.current_item

        item = (
            game_state.get_current_wall()
            .get_receptacle(receptacle_id)
            .get_item_state(item_id)
        )
        if not item:
            return ""

        image_filename = self._encode_item_state(item)

        if image_filename:
            return str(self.image_dir / "item_view" / item_id / image_filename)
        return ""


    def _encode_wall_state(self, wall_state: WallState) -> str:
        receptacle_states = {
            obj_id: {
                "receptacle_state": obj.current_state["receptacle_state"],
                "items": obj.current_state["interactable_items"],
            }
            for obj_id, obj in wall_state.receptacles.items()
        }
        mapping_file = self.mapping_dir / "wall_view" / f"{wall_state.wall_id}.json"

        with open(mapping_file, "r") as f:
            mapping_data = json.load(f)

        matching_scenes = []
        for scene in mapping_data["scene_states"]:
            states_match = all(
                scene["object_states"][obj_id]["receptacle_state"]
                == states["receptacle_state"]
                for obj_id, states in receptacle_states.items()
                if obj_id in scene["object_states"]
            )
            if states_match:
                matching_scenes.append(scene)

        if not matching_scenes:
            return "0"

        if len(matching_scenes) == 1:
            return matching_scenes[0]["image_path"].split(".")[0]

        else:
            matching_count = [0 for _ in range(len(matching_scenes))]
            best_scene = None
            for i, scene in enumerate(matching_scenes):
                for obj_id, states in receptacle_states.items():
                    if obj_id in scene["object_states"]:
                        scene_items = set(scene["object_states"][obj_id]["items"])
                        current_items = set(states["items"])
                        if scene_items == current_items:
                            matching_count[i] += 1
            best_scene_idx = matching_count.index(max(matching_count))
            best_scene = matching_scenes[best_scene_idx]
            return best_scene["image_path"].split(".")[0]

    def _encode_receptacle_state(
        self, receptacle_id: str, obj: ReceptacleState
    ) -> Optional[str]:
        mapping_file = self.mapping_dir / "object_view" / f"{receptacle_id}.json"
        try:
            with open(mapping_file, "r") as f:
                mapping_data = json.load(f)

            current_state = obj.current_state
            for scene in mapping_data["scene_states"]:
                if scene["object_states"]["receptacle_state"] == current_state[
                    "receptacle_state"
                ] and set(scene["object_states"]["items"]) == set(
                    current_state["interactable_items"]
                ):
                    return scene["image_path"]

            return None
        except (FileNotFoundError, json.JSONDecodeError):
            print("object mapping file not found or json decode error")
            return None

    def _encode_item_state(self, item_state: ItemState) -> Optional[str]:
        mapping_file = (
            self.mapping_dir / "item_view" / f"{item_state.game_item.item_name}.json"
        )
        try:
            with open(mapping_file, "r") as f:
                mapping_data = json.load(f)

            current_state = item_state.get_current_state()

            for state in mapping_data["item_states"]:
                if state["name"] == current_state:
                    return state["image_path"]
            return None
        except (FileNotFoundError, json.JSONDecodeError):
            print("item mapping file not found or json decode error")
            return None

    def _determine_action_type(
        self, prev_state: GameState, current_state: GameState, action: str
    ) -> ActionType:
        if action.startswith("turn_to_"):
            return ActionType.TURN

        if action.startswith("inspect "):
            return ActionType.INSPECT

        if action == "step_back":
            return ActionType.STEP_BACK

        if action.startswith("use "):
            if prev_state.context.triggers == current_state.context.triggers:
                return ActionType.USE_INVALID
            return ActionType.USE_VALID

        if action.startswith("pick "):
            return ActionType.PICK

        return ActionType.RECEPTACLE_ACTION


def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
