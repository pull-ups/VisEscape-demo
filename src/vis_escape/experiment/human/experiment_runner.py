import copy
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from PIL import Image, ImageTk

from vis_escape.constants import ASSETS_DIR
from vis_escape.game.manage.game_state import GameState
from vis_escape.game.manage.view_manager import ViewManager
from vis_escape.objects.item import QuizItem


class RoomView:
    def __init__(self, root, room_name="room1_refactor", mode="verbose"):
        self.room_name = room_name
        self.root = root
        self.root.title("Room Escape")
        self.mode = mode
        self.action_count = 0
        self.previous_view = None

        # For logging
        self.run_history = []
        self.run_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.experiment_result = {
            "success": False,
            "steps_taken": 0,
            "reason": "incomplete",
        }

        # Load GameState
        self.game_state = self.load_game_state_from_config(
            os.path.join(ASSETS_DIR, room_name, "config.py")
        )

        # Initialize GameState
        self.view_manager = ViewManager(
            os.path.join(ASSETS_DIR, room_name), "", self.game_state, play_mode="human"
        )

        # Save previous state (for generating transition msgs)
        self.previous_game_state = None

        # Initialize UI
        self.setup_ui()
        self.update_view()

    def load_game_state_from_config(self, config_path: str) -> GameState:
        """Load gamestate dynamically from config.py"""
        import importlib.util

        spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        return config_module.game_state

    def save_run_history(self):
        os.makedirs(f"./results/Human/{self.room_name}", exist_ok=True)
        filename = f"./results/Human/{self.room_name}/run_history_{self.run_start_time}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.run_history, f, ensure_ascii=False, indent=2)

    def setup_ui(self):
        # Action counter label
        self.counter_label = ttk.Label(self.root, text="Actions taken: 0")
        self.counter_label.pack(pady=5)

        # System messages
        self.message_frame = ttk.LabelFrame(self.root, text="System Message")
        self.message_frame.pack(pady=5, padx=10, fill="x")
        self.message_label = ttk.Label(self.message_frame, wraplength=800)
        self.message_label.pack(pady=5, padx=5)

        # Images
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

        # Quizes
        self.quiz_frame = ttk.LabelFrame(self.root, text="Quiz Input")
        self.quiz_frame.pack(pady=10, padx=10, fill="x")
        self.quiz_frame.pack_forget()  # Hide initially

        self.quiz_entry = ttk.Entry(self.quiz_frame)
        self.quiz_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.submit_button = ttk.Button(
            self.quiz_frame, text="Submit Answer", command=self.handle_quiz_submit
        )
        self.submit_button.pack(side="left", padx=5, pady=5)

        # Listup available actions
        self.actions_frame = ttk.LabelFrame(self.root, text="Available Actions")
        self.actions_frame.pack(pady=10, padx=10, fill="x")

        # Frames that contains action buttons
        self.buttons_frame = ttk.Frame(self.actions_frame)
        self.buttons_frame.pack(pady=5, padx=5)

    def update_view(self):
        # Update image
        image_path = self.view_manager.get_current_view_image(
            self.game_state,
            self.previous_game_state,
            verbose=False,
        )
        # Update system message
        system_message="""You are playing a room escape game. The room is surrounded by 4 walls, and you can explore other walls by "turn_to_[direction]". Each wall has objects that you can interact with, and you can inspect the object by "inspect [object]".
When you need to input an answer, enter it in the text prompt window.
Good Luck!"""
        self.message_label.config(text=system_message)

        # Save current as previous
        self.previous_game_state = copy.deepcopy(self.game_state)

        # Check whether current item is quiz
        # If not key, set puzzle=True
        puzzle = False
        if self.game_state.current_view == "ITEM" and self.game_state.current_item:
            receptacle = self.game_state.get_current_wall().get_receptacle(
                self.game_state.inspected_receptacle
            )
            if receptacle:
                item_state = receptacle.get_item_state(self.game_state.current_item)
                if (
                    isinstance(item_state.game_item, QuizItem)
                    and "key" not in item_state.game_item.item_name.lower()
                ):
                    puzzle = True            
        if image_path:
            image = Image.open(image_path)

            # Align image size (e.g. Fix height as 600pxs)
            height = 400
            ratio = height / image.size[1]
            width = int(image.size[0] * ratio)
            image = image.resize((width, height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo

        # Show/hide quiz
        if self.game_state.current_item is not None:
            self.quiz_frame.pack(pady=10, padx=10, fill="x")
        else:
            self.quiz_frame.pack_forget()

        # Update available action buttons
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        # Generate currently available action buttons
        available_actions = self.game_state.get_available_actions()
        for action in available_actions:
            ttk.Button(
                self.buttons_frame,
                text=action,
                command=lambda a=action: self.handle_action(a),
            ).pack(side="left", padx=2)

    def handle_action(self, action: str):
        available_actions = self.game_state.get_available_actions()

        # Handle actions with GameState
        result = self.game_state.handle_action(action)
        current_view = self.view_manager.get_current_view_image(
            self.game_state, self.previous_game_state, action
        )

        self.action_count += 1

        turn_info = {
            "turn_number": self.action_count,
            "available_actions": available_actions,
            "chosen_action": action,
            "image_path": current_view,
            "previous_image_path": self.previous_view,
        }
        self.run_history.append(turn_info)

        self.save_run_history()

        self.previous_view = current_view

        self.counter_label.config(text=f"Actions taken: {self.action_count}")
        self.update_view()

        if self.game_state.check_game_clear():
            self.experiment_result["success"] = True
            self.experiment_result["steps_taken"] = self.action_count
            self.experiment_result["reason"] = "success"
            print(f"Game completed in {self.action_count} steps!")
            self.finish_experiment()
            return

    def handle_quiz_submit(self):
        answer = self.quiz_entry.get().strip()
        if answer:
            self.handle_action(answer)
            self.quiz_entry.delete(0, tk.END)


    def finish_experiment(self):
        self.run_history.append({"experiment_summary": self.experiment_result})

        log_path = f"./results/logs_human/{self.room_name}/run_history_{self.run_start_time}.json"
        self.save_run_history()

        print(f"\nExperiment Summary:")
        print(f"Success: {self.experiment_result['success']}")
        print(f"Steps Taken: {self.experiment_result['steps_taken']}")
        print(f"Reason: {self.experiment_result['reason']}")

        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    room_view = RoomView(root, "room1")
    root.mainloop()
