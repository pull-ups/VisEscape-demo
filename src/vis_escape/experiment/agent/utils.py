import json
import os
from typing import Dict, List

from vis_escape.constants import EVALUATION_DIR, SCRIPTS_DIR
from vis_escape.game.manage.game_state import GameState
from vis_escape.game.run.replay import ReplayVideoCreator


def load_game_state_from_config(config_path: str) -> "GameState":
    """Load game state dynamically from config.py"""
    import importlib.util

    spec = importlib.util.spec_from_file_location("config", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    return config_module.game_state


def save_run_history(
    run_history: list,
    room_name: str,
    model_name: str,
    run_mode: str,
    hint_mode: str,
    run_start_time: str,
    current_dir: str,
    agent_type: str = None,
):
    if agent_type:
        log_dir = os.path.join(
            SCRIPTS_DIR,
            f"results_{agent_type}",
            "logs",
            model_name,
            run_mode,
            hint_mode,
            room_name,
        )
    else:
        log_dir = os.path.join(
            SCRIPTS_DIR,
            f"results_{run_mode}",
            "logs",
            model_name,
            run_mode,
            hint_mode,
            room_name,
        )
    print(log_dir)
    os.makedirs(log_dir, exist_ok=True)
    filename = f"{log_dir}/run_history_{run_start_time}.json"

    existing_history = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_history = json.load(f)

    if isinstance(run_history, list) and len(run_history) > 0:
        existing_history.append(run_history[-1])

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_history, f, ensure_ascii=False, indent=2)


def _parse_spatial_memory(spatial_memory_str: str) -> Dict:
    """Parse the spatial memory string into a structured dictionary.

    Args:
        spatial_memory_str (str): Raw spatial memory string from the agent

    Returns:
        dict: Either parsed sections or error info with raw string
    """
    try:
        import re

        # Case-insensitive section markers
        spatial_pattern = re.compile(r"\[spatial memory\]", re.IGNORECASE)
        inspected_pattern = re.compile(r"\[inspected objects\]", re.IGNORECASE)
        uninspected_pattern = re.compile(r"\[uninspected objects\]", re.IGNORECASE)
        additional_pattern = re.compile(r"\[additional memory\]", re.IGNORECASE)

        # Split sections using the patterns
        parts = re.split(inspected_pattern, spatial_memory_str)
        spatial_part = re.split(spatial_pattern, parts[0])[-1]

        remaining = parts[1]
        parts = re.split(uninspected_pattern, remaining)
        inspected_part = parts[0]

        remaining = parts[1]
        parts = re.split(additional_pattern, remaining)
        uninspected_part = parts[0]
        additional_part = parts[1] if len(parts) > 1 else ""

        # Parse each section
        spatial_dict = json.loads(spatial_part.strip())
        inspected_dict = json.loads(inspected_part.strip())
        uninspected_list = (
            []
            if uninspected_part.strip("[]").strip() == ""
            else uninspected_part.strip("[]").split(", ")
        )
        additional_list = (
            []
            if additional_part.strip("[]").strip() == ""
            else [
                item.strip()
                for item in additional_part.strip("[]").split(".")
                if item.strip()
            ]
        )

        return True, {
            "SPATIAL MEMORY": spatial_dict,
            "INSPECTED OBJECTS": inspected_dict,
            "UNINSPECTED OBJECTS": uninspected_list,
            "ADDITIONAL MEMORY": additional_list,
        }

    except Exception as e:
        return False, spatial_memory_str



def _parse_salient_action_history(salient_action_history: List[str]) -> str:
    """Parse and consolidate salient action history

    Args:
        salient_action_history (List[str]): List of action history strings

    Returns:
        str: Processed action history with duplicates removed and tries grouped
    """

    processed_actions = {}
    for action_str in salient_action_history:
        location_action, feedback = action_str.split(" - ")[0], "".join(
            action_str.split(" - ")[1:]
        )
        location, action = location_action.split(", ")
        key = f"{location}, {action}"
        if "try" not in action:
            if "no change" in feedback.lower():
                if key + "_no_change" not in processed_actions:
                    processed_actions[key + "_no_change"] = [feedback]
            else:
                if key + "_other" not in processed_actions:
                    processed_actions[key + "_other"] = [feedback]
                else:
                    processed_actions[key + "_other"].append(feedback)
        else:
            trial_key = f"{location}, try"
            tried_answer = action.split("try ")[1]
            if "no change" in feedback.lower():
                if trial_key + "_no_change" not in processed_actions:
                    processed_actions[trial_key + "_no_change"] = [
                        (tried_answer, feedback)
                    ]
                else:
                    processed_actions[trial_key + "_no_change"].append(
                        (tried_answer, feedback)
                    )
            else:
                if trial_key + "_other" not in processed_actions:
                    processed_actions[trial_key + "_other"] = [(tried_answer, feedback)]
                else:
                    processed_actions[trial_key + "_other"].append(
                        (tried_answer, feedback)
                    )
    for key, value in processed_actions.items():
        string = ""
        if ", try" in key:
            if "_no_change" in key:
                original_key = key.replace("_no_change", "")
                tried_answer = [i[0] for i in value]
                string += f"{original_key} [{', '.join(tried_answer)}] - {value[0][1]}"
            else:
                original_key = key.replace("_other", "")
                for i in value:
                    string += f"{original_key} [{i[0]}] - {i[1]}"
        else:
            if "_no_change" in key:
                original_key = key.replace("_no_change", "")
                string += f"{original_key} - {value[0]}"
            else:
                original_key = key.replace("_other", "")
                for i in value:
                    string += f"{original_key} - {i}"
        processed_actions[key] = string
    return [i for i in processed_actions.values()]


def save_spatial_memory_evaluation(
    spatial_memory: str,
    game_state: "GameState",
    step_count: int,
    room_name: str,
    model_name: str,
    run_start_time: str,
) -> None:
    """Save spatial memory evaluation results to a JSON file

    Args:
        spatial_memory (str): Current spatial memory string
        game_state (GameState): Current game state
        step_count (int): Current step count
        room_name (str): Name of the room
        model_name (str): Name of the model
        run_start_time (str): Run start timestamp
    """
    parsed, parsed_memory = _parse_spatial_memory(spatial_memory)
    if parsed:
        result = {
            "success": True,
            "pred": {
                "receptacle_memory": parsed_memory["SPATIAL MEMORY"],
                "inspected_objects": parsed_memory["INSPECTED OBJECTS"],
                "uninspected_objects": parsed_memory["UNINSPECTED OBJECTS"],
                "additional_memory": parsed_memory["ADDITIONAL MEMORY"],
            },
            "gt": game_state.export_current_state(),
        }
    else:
        result = {
            "success": False,
            "pred": parsed_memory,
            "gt": game_state.export_current_state(),
        }

    target_dir = os.path.join(
        EVALUATION_DIR, "spatial_memory", model_name, room_name, run_start_time
    )
    os.makedirs(target_dir, exist_ok=True)

    with open(os.path.join(target_dir, f"current_state_{step_count}.json"), "w") as f:
        json.dump(result, f, indent=4)


def create_replay_video(room_name: str, run_start_time: str, current_dir: str):
    log_dir = os.path.join(current_dir, "results", "logs", room_name)
    history_file = f"{log_dir}/run_history_{run_start_time}.json"
    video_filename = f"replay_{run_start_time}.mp4"
    video_path = os.path.join(log_dir, video_filename)

    creator = ReplayVideoCreator(
        log_file_path=history_file, output_path=video_path, fps=1
    )
    creator.create_video()
    print(f"Video created at: {video_path}")

