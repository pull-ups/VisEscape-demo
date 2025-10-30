"""Generate a deterministic state graph for a room that can be consumed by the
static web client.

Usage:
    python3 scripts/export_room_static.py --room room1

This produces `web/static_data/room1.js` containing all reachable states,
actions, quiz metadata, and image references needed for a browser-only
experience.
"""

from __future__ import annotations

import argparse
import copy
import contextlib
import io
import json
import os
import sys
from collections import deque
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from vis_escape.constants import ASSETS_DIR  # noqa: E402
from vis_escape.game.manage.game_state import GameState  # noqa: E402
from vis_escape.game.manage.view_manager import ViewManager  # noqa: E402
from vis_escape.objects.item import QuizItem  # noqa: E402
from vis_escape.game.manage.game_state import ItemState  # noqa: E402

SYSTEM_MESSAGE = (
    "You are playing a room escape game. The room is surrounded by 4 walls, and "
    'you can explore other walls by "turn_to_[direction]". Each wall has objects '
    'that you can interact with, and you can inspect the object by "inspect '
    '[object]".\nWhen you need to input an answer, enter it in the text prompt '
    "window.\nGood Luck!"
)


class StateEncoder(json.JSONEncoder):
    def default(self, obj):  # type: ignore[override]
        if isinstance(obj, set):
            return sorted(list(obj))
        if isinstance(obj, ItemState):
            return {
                "item_name": obj.game_item.item_name,
                "item_type": obj.game_item.item_type,
                "state": obj.current_state,
            }
        return super().default(obj)


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(value[k]) for k in sorted(value.keys())}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, set):
        return sorted(value)
    return value


def _export_game_state(game_state: GameState) -> Dict[str, Any]:
    walls = {}
    for wall_id, wall_state in game_state.walls.items():
        receptacles = {}
        for receptacle_id, receptacle in wall_state.receptacles.items():
            receptacles[receptacle_id] = {
                "receptacle_state": _normalize(receptacle.current_state),
                "items": {
                    item_id: {
                        "state": item_state.current_state,
                        "item_type": item_state.game_item.item_type,
                    }
                    for item_id, item_state in receptacle.item_states.items()
                },
            }
        walls[wall_id] = {"receptacles": receptacles}

    return {
        "current_view": game_state.current_view,
        "current_wall": game_state.current_wall,
        "inspected_receptacle": game_state.inspected_receptacle,
        "current_item": game_state.current_item,
        "inventory": sorted(list(game_state.context.get_player_inventory_str())),
        "triggers": {k: v for k, v in game_state.context.triggers.items() if v},
        "walls": walls,
        "game_clear": game_state.game_clear,
    }


def _state_key(game_state: GameState) -> str:
    export = _export_game_state(game_state)
    return json.dumps(export, sort_keys=True, cls=StateEncoder)


def _relative_image_path(image_path: str) -> str:
    rel_path = os.path.relpath(image_path, ASSETS_DIR)
    return rel_path.replace(os.sep, "/")


def _quiz_meta(game_state: GameState) -> Dict[str, Any]:
    if game_state.current_view != "ITEM":
        return {}
    receptacle = game_state.get_current_wall().get_receptacle(
        game_state.inspected_receptacle
    )
    if not receptacle:
        return {}
    item_state = receptacle.get_item_state(game_state.current_item)
    if not item_state:
        return {}
    if isinstance(item_state.game_item, QuizItem):
        return {
            "question": item_state.game_item.question_text or "",
            "answer": item_state.game_item.answer,
            "item": item_state.game_item.item_name,
        }
    return {}


def build_state_graph(room_name: str) -> Dict[str, Any]:
    import importlib.util

    room_assets = Path(ASSETS_DIR) / room_name
    config_path = room_assets / "config.py"

    spec = importlib.util.spec_from_file_location(f"vis_escape_room_{room_name}", config_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    game_state: GameState = module.game_state

    initial_state = copy.deepcopy(game_state)

    graph: Dict[str, Any] = {}
    queue: deque[GameState] = deque([initial_state])
    visited: set[str] = set()
    key_to_id: Dict[str, str] = {}

    def ensure_state_id(gs: GameState) -> tuple[str, str]:
        key = _state_key(gs)
        if key not in key_to_id:
            key_to_id[key] = f"s{len(key_to_id)}"
        return key, key_to_id[key]

    while queue:
        current_state = queue.popleft()
        state_key, state_id = ensure_state_id(current_state)
        if state_key in visited:
            continue
        visited.add(state_key)

        node_export = _export_game_state(current_state)
        # Build display info for this node
        vm_for_node = ViewManager(str(room_assets), "", copy.deepcopy(current_state), play_mode="human")
        image_path = vm_for_node.get_current_view_image(current_state)
        node_data = {
            "id": state_id,
            "view": node_export["current_view"],
            "wall": node_export["current_wall"],
            "inspected": node_export["inspected_receptacle"],
            "item": node_export["current_item"],
            "inventory": node_export["inventory"],
            "triggers": node_export["triggers"],
            "gameClear": node_export["game_clear"],
            "image": _relative_image_path(image_path) if image_path else None,
            "quiz": _quiz_meta(current_state),
            "actions": [],
            "inputActions": [],
        }

        actions = current_state.get_available_actions()
        used_action_labels: set[str] = set()

        for action in actions:
            next_state = copy.deepcopy(current_state)
            prev_snapshot = copy.deepcopy(current_state)
            with contextlib.redirect_stdout(io.StringIO()):
                success = next_state.handle_action(action)
            if not success:
                continue

            transition_vm = ViewManager(str(room_assets), "", copy.deepcopy(next_state), play_mode="human")
            image_after = transition_vm.get_current_view_image(
                next_state, prev_snapshot, action
            )

            next_key, next_id = ensure_state_id(next_state)
            action_entry = {
                "label": action,
                "type": "button",
                "next": next_id,
                "messages": {
                    "action": transition_vm.last_message.get("action_message", ""),
                    "after": transition_vm.last_message.get("after_state_message", ""),
                },
                "image": _relative_image_path(image_after) if image_after else None,
            }
            node_data["actions"].append(action_entry)
            used_action_labels.add(action)

            if next_key not in visited:
                queue.append(next_state)

        # Typed answers for quizzes
        quiz = _quiz_meta(current_state)
        if quiz:
            answer = quiz.get("answer")
            if answer and answer not in used_action_labels:
                solved_state = copy.deepcopy(current_state)
                prev_snapshot = copy.deepcopy(current_state)
                with contextlib.redirect_stdout(io.StringIO()):
                    success = solved_state.handle_action(answer)
                if success:
                    vm_after_answer = ViewManager(
                        str(room_assets), "", copy.deepcopy(solved_state), play_mode="human"
                    )
                    image_after = vm_after_answer.get_current_view_image(
                        solved_state, prev_snapshot, answer
                    )
                    next_key, next_id = ensure_state_id(solved_state)
                    node_data["inputActions"].append(
                        {
                            "expected": answer,
                            "next": next_id,
                            "messages": {
                                "action": vm_after_answer.last_message.get(
                                    "action_message", ""
                                ),
                                "after": vm_after_answer.last_message.get(
                                    "after_state_message", ""
                                ),
                            },
                            "image": _relative_image_path(image_after)
                            if image_after
                            else None,
                        }
                    )
                    if next_key not in visited:
                        queue.append(solved_state)

        graph[state_id] = node_data

    initial_vm = ViewManager(str(room_assets), "", copy.deepcopy(initial_state), play_mode="human")
    initial_image = initial_vm.get_current_view_image(initial_state)
    _, initial_state_id = ensure_state_id(initial_state)

    return {
        "room": room_name,
        "systemMessage": SYSTEM_MESSAGE,
        "initialState": initial_state_id,
        "initialMessages": {
            "action": initial_vm.last_message.get("action_message", ""),
            "after": initial_vm.last_message.get("after_state_message", ""),
        },
        "initialImage": _relative_image_path(initial_image) if initial_image else None,
        "states": graph,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a room graph for the static web client")
    parser.add_argument("--room", required=True, help="Room name (e.g., room1)")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "web" / "static_data",
        help="Directory to write the JSON graph",
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    graph = build_state_graph(args.room)
    output_path = args.output / f"{args.room}.js"
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":"))
    js_content = (
        "(window.__VisEscapeGraphs = window.__VisEscapeGraphs || {})"
        f"['{args.room}'] = {payload};\n"
    )
    with output_path.open("w", encoding="utf-8") as fh:
        fh.write(js_content)
    print(f"Exported {args.room} graph to {output_path}")


if __name__ == "__main__":
    main()
