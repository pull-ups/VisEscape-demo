import json
import os
import sys
import tkinter as tk

import click

from vis_escape.constants import ASSETS_DIR
from vis_escape.experiment.human.experiment_runner import RoomView


def get_oracle_actions(oracle_file_path):
    with open(oracle_file_path, "r") as f:
        oracle_data = json.load(f)

    actions = []
    for turn in oracle_data:
        action = turn["chosen_action"]
        actions.append(action)

    return actions


def execute_actions(app, actions, delay_ms=500):
    if not actions:
        return

    action = actions[0]
    remaining_actions = actions[1:]

    def execute():
        app.handle_action(action)
        if remaining_actions:
            app.root.after(
                delay_ms, lambda: execute_actions(app, remaining_actions, delay_ms)
            )

    app.root.after(delay_ms, execute)


def check_file(room_name):
    mapping_dir = os.path.join(ASSETS_DIR, room_name, "mapping")
    image_dir = os.path.join(ASSETS_DIR, room_name, "image")

    for viewtype in ["object_view", "wall_view"]:
        view_dir = os.path.join(mapping_dir, viewtype)
        for file in os.listdir(view_dir):
            if not file.endswith(".json"):
                continue
            mapping_file_path = os.path.join(
                view_dir, file
            )
            image_dir_path = os.path.join(image_dir, viewtype, file.split(".")[0])

            with open(mapping_file_path, "r") as f:
                data = json.load(f)
        

@click.command()
@click.option("-r", "--room-name", type=str, required=False, default="room1")
@click.option("-m", "--mode", type=str, required=False, default="verbose")
def main(room_name, mode):
    os.environ["TK_SILENCE_DEPRECATION"] = "1"
    root = tk.Tk()
    check_file(room_name)
    app = RoomView(root, room_name, mode)
    
    oracle_file_path = os.path.join(ASSETS_DIR, room_name, "walkthrough_oracle.json")
    oracle_actions = get_oracle_actions(oracle_file_path)
    
    execute_actions(app, oracle_actions)
    root.mainloop()


if __name__ == "__main__":
    main()
