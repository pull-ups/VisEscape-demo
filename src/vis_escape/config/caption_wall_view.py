import json
import os
from pathlib import Path
from typing import Mapping, Optional

import click

from vis_escape.utils import run_inference_vision_caption

def update_captions_json(
    captions_file: str, wall_direction: str, image_path: str, caption: str
):
    """Update the shared captions JSON file under the WV (Wall View) section"""
    captions = {}
    if os.path.exists(captions_file):
        captions = json.load(open(captions_file))

    if "wall_view" not in captions:
        captions["wall_view"] = {}

    # Initialize dictionary for wall_direction if it doesn't exist
    if wall_direction not in captions["wall_view"]:
        captions["wall_view"][wall_direction] = {}

    filename = os.path.basename(image_path)
    captions["wall_view"][wall_direction][filename] = caption

    with open(captions_file, "w", encoding="utf-8") as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)


def process_wall_view_json(
    json_path: str,
    assets_dir: str,
    captions_file: str,
    model_name: str,
    base_url: str,
):
    """Process a single wall view JSON file and generate captions for its states"""
    wall_direction = Path(
        json_path
    ).stem  # Get filename without extension (EAST, WEST, etc.)

    with open(json_path, "r", encoding="utf-8") as f:
        wall_data = json.load(f)

    for state in wall_data["scene_states"]:
        image_path = os.path.join(
            assets_dir, "image", "wall_view", wall_direction, state["image_path"]
        )

        if not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}")
            continue

        # Create objects list including items
        objects = []
        for obj, state_info in state["object_states"].items():
            objects.append(obj)
            if state_info.get("items"):
                objects.extend(state_info["items"])

        prompt = f"""This image is a wall view of a room, with following objects: {objects}
Describe this image. The names of visible objects should be expressed using the given object names above, enclosed in "".
Your description should fulfill the following rules:
1. Description should include every visual information, but concise and clear.
2. Do not include any analysis of the scene or the room, just describe the image.
3. Do not start description with phrases like 'The image depicts', 'The image shows', etc."""
        print(f"\nProcessing {state['image_path']}...")
        print(f"Prompt: {prompt}")

        caption = run_inference_vision_caption(
            image_path,
            prompt,
            model_name,
            base_url,
        )
        print(f"Generated caption: {caption}")

        update_captions_json(
            captions_file, wall_direction, state["image_path"], caption
        )


@click.command()
@click.option("-a", "--assets-dir", type=str, required=True)
@click.option("-m", "--model-name", type=str, required=True)
@click.option("-u", "--agent-hostname", type=str, required=False, default=None)
@click.option("-p", "--agent-port", type=int, required=False, default=None)
def main(assets_dir, model_name, agent_hostname, agent_port):
    assets_dir = Path(assets_dir).expanduser().absolute()

    wall_view_dir = assets_dir / "mapping" / "wall_view"
    if not wall_view_dir.exists():
        raise ValueError(f"Directory not found: {wall_view_dir}")

    captions_file = assets_dir / "captions" / model_name / f"image_captions.json"
    captions_file.parent.mkdir(parents=True, exist_ok=True)

    # Get base url for vLLM (None if using OpenAI)
    base_url = f"http://{agent_hostname}:{agent_port}/v1" if agent_hostname and agent_port else None


    # Process each wall view JSON file
    for json_file in os.listdir(wall_view_dir):
        if json_file.endswith(".json"):
            json_path = os.path.join(wall_view_dir, json_file)
            print(f"\nProcessing wall view file: {json_file}")
            process_wall_view_json(
                str(json_path),
                str(assets_dir),
                str(captions_file),
                model_name,
                base_url,
            )

    print(f"\nWall view captions have been saved to {captions_file}")


if __name__ == "__main__":
    main()
