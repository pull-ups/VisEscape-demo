import copy
import json
import os
from datetime import datetime

from vis_escape.constants import ASSETS_DIR
from vis_escape.experiment.agent import utils
from vis_escape.experiment.agent.visescaper.agent import Agent
from vis_escape.game.manage.view_manager import ViewManager
from vis_escape.game.run.replay import ReplayVideoCreator


class AIExperimentRunner:
    def __init__(self, room_name="_room1_base"):
        self.room_name = room_name
        self.action_count = 0
        self.ai_player = Agent()
        self.run_history = []
        self.run_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.view_manager = ViewManager(os.path.join(ASSETS_DIR, room_name))
        self.game_state = utils.load_game_state_from_config(
            os.path.join(ASSETS_DIR, room_name, "config.py")
        )

        self.previous_game_state = None

        self.experiment_result = {
            "success": False,
            "steps_taken": 0,
            "reason": "incomplete",
        }

        # for AI inputs
        self.previous_info = {"path_previous_scene": None, "previous_action": None}
        self.action_history = []
        self.action_history_with_feedback = []
        self.longterm_memory = ""
        self.current_plan = ""

    def save_run_history(self):
        os.makedirs(f"./results/logs_ai/{self.room_name}", exist_ok=True)
        filename = (
            f"./results/logs_ai/{self.room_name}/run_history_{self.run_start_time}.json"
        )
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.run_history, f, ensure_ascii=False, indent=2)

    def create_replay_video(self, log_path: str):
        video_filename = f"replay_{self.run_start_time}.mp4"
        video_path = os.path.join(os.path.dirname(log_path), video_filename)

        creator = ReplayVideoCreator(
            log_file_path=log_path, output_path=video_path, fps=1
        )
        creator.create_video()
        print(f"Video created at: {video_path}")

    def run_experiment(self, max_steps=50):
        while self.action_count < max_steps:
            path_current_scene = self.view_manager.get_current_view_image(
                self.game_state, self.previous_game_state, verbose=False
            )
            available_actions = self.game_state.get_available_actions()
            inventory = ", ".join(self.game_state.context.get_player_inventory_str())
            direction = self.game_state.get_current_wall().wall_id

            ### get action feedback
            if self.action_count > 0:
                if self.previous_info["path_previous_scene"] == path_current_scene:
                    self.action_history_with_feedback.append(
                        {
                            "action": action,
                            "analysis of action": "The action no visible effect.",
                        }
                    )
                else:
                    action_feedback = self.ai_player.get_action_feedback(
                        path_previous_scene=self.previous_info["path_previous_scene"],
                        path_current_scene=path_current_scene,
                        previous_action=self.previous_info["previous_action"],
                    )
                    self.action_history_with_feedback.append(
                        {"action": action, "analysis of action": action_feedback}
                    )
                    print("\033[92m[FEEDBACK]: ", action_feedback, "\033[0m")

            # update longterm memory
            if self.action_count != 0 and self.action_count % 10 == 0:
                self.longterm_memory = self.ai_player.get_memory_management(
                    longterm_memory=self.longterm_memory,
                    action_history_with_feedback=self.action_history_with_feedback[
                        -10:
                    ],
                )
                # print as red
                print("\033[91m[LONGTERM MEMORY]: ", self.longterm_memory, "\033[0m")
                print("---------------------------------------")

            # update current plan
            if self.action_count != 0 and self.action_count % 5 == 0:
                self.current_plan, raw_response = (
                    self.ai_player.get_short_term_planning(
                        current_plan=self.current_plan,
                        inventory=inventory,
                        longterm_memory=self.longterm_memory,
                        action_history_with_feedback=self.action_history_with_feedback[
                            -10:
                        ],
                    )
                )
                # print as red
                print("\033[91m[CURRENT PLAN]: ", self.current_plan, "\033[0m")
                print("---------------------------------------")

            ### get action
            if self.action_count == 0:
                action, raw_response = self.ai_player.get_next_action_first_turn(
                    direction=direction,
                    path_current_scene=path_current_scene,
                    inventory=inventory,
                    available_actions=available_actions,
                )
            else:
                action, raw_response = self.ai_player.get_next_action(
                    direction=direction,
                    path_current_scene=path_current_scene,
                    inventory=inventory,
                    longterm_memory=self.longterm_memory,
                    current_plan=self.current_plan,
                    action_history_with_feedback=self.action_history_with_feedback[
                        -10:
                    ],
                    available_actions=available_actions,
                )
            print("ACTION: ", action)

            self.previous_game_state = copy.deepcopy(self.game_state)

            result = self.game_state.handle_action(action)
            triggers = self.game_state.context.triggers.copy()
            inventory = ", ".join(self.game_state.context.get_player_inventory_str())

            turn_info = {
                "turn_number": self.action_count,
                "available_actions": available_actions,
                "raw_response": raw_response,
                "chosen_action": action,
                "action_feedback": (
                    self.action_history_with_feedback[-1]["analysis of action"]
                    if self.action_count > 0
                    else ""
                ),
                "longterm_memory": self.longterm_memory,
                "current_plan": self.current_plan,
                "image_path": path_current_scene,
                "previous_image_path": self.previous_info["path_previous_scene"],
                "triggers": triggers.copy(),
                "inventory": inventory,
            }
            self.action_count += 1

            self.run_history.append(turn_info)
            self.action_history.append(action)
            self.save_run_history()

            self.previous_info["path_previous_scene"] = path_current_scene
            self.previous_info["previous_action"] = action

            if self.game_state.check_game_clear():
                self.experiment_result["success"] = True
                self.experiment_result["steps_taken"] = self.action_count
                self.experiment_result["reason"] = "success"
                print(f"Experiment successful! Completed in {self.action_count} steps")
                break

            if self.action_count >= max_steps:
                self.experiment_result["reason"] = "max_steps_exceeded"
                print(f"Experiment failed: Reached maximum {self.action_count} steps")
                break

        self.run_history.append({"experiment_summary": self.experiment_result})
        self.save_run_history()

        log_path = (
            f"./results/logs_ai/{self.room_name}/run_history_{self.run_start_time}.json"
        )
        self.create_replay_video(log_path)

        return self.experiment_result


if __name__ == "__main__":
    runner = AIExperimentRunner(room_name="room2_refactor")
    result = runner.run_experiment()
    print(f"\nExperiment Summary:")
    print(f"Success: {result['success']}")
    print(f"Steps Taken: {result['steps_taken']}")
    print(f"Reason: {result['reason']}")
