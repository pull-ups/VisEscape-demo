import json

import cv2
import numpy as np


class ReplayVideoCreator:
    def __init__(self, log_file_path: str, output_path: str, fps: int = 1):
        with open(log_file_path, "r") as f:
            self.history = json.load(f)

        self.output_path = output_path
        self.fps = fps

        # Set video (1280x720)
        self.width = 1280
        self.height = 720
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    def create_text_frame(self, turn_data: dict) -> np.ndarray:
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_color = (0, 0, 0)
        line_type = 2

        text = turn_data["chosen_action"]

        (text_width, text_height), _ = cv2.getTextSize(
            text, font, font_scale, line_type
        )
        x_position = (self.width - text_width) // 2
        y_position = (self.height + text_height) // 2

        cv2.putText(
            frame,
            text,
            (x_position, y_position),
            font,
            font_scale,
            font_color,
            line_type,
        )

        return frame

    def resize_image(self, image_path: str) -> np.ndarray:
        img = cv2.imread(image_path)
        if img is None:
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)

        h, w = img.shape[:2]
        ratio = min(self.width / w, self.height / h)
        new_size = (int(w * ratio), int(h * ratio))
        resized = cv2.resize(img, new_size)

        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        y_offset = (self.height - new_size[1]) // 2
        x_offset = (self.width - new_size[0]) // 2
        canvas[y_offset : y_offset + new_size[1], x_offset : x_offset + new_size[0]] = (
            resized
        )

        return canvas

    def create_video(self):
        video_writer = cv2.VideoWriter(
            self.output_path, self.fourcc, self.fps, (self.width, self.height)
        )

        try:
            for turn_data in self.history:
                if turn_data.get("experiment_summary"):
                    continue

                game_frame = self.resize_image(turn_data["image_path"])
                video_writer.write(game_frame)

                text_frame = self.create_text_frame(turn_data)
                video_writer.write(text_frame)

                print(f"Processed turn {turn_data['turn_number']}")

        finally:
            video_writer.release()

        print(f"Video created successfully at {self.output_path}")
