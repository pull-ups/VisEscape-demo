import json
import os
from pathlib import Path
from typing import Mapping, Optional

import click

from vis_escape.utils import run_inference_vision_caption

def update_captions_json(
    captions_file: str, object_type: str, image_path: str, caption: str
):
    """Update the shared captions JSON file under the OV (Object View) section"""
    captions = {}
    if os.path.exists(captions_file):
        with open(captions_file, "r", encoding="utf-8") as f:
            captions = json.load(f)

    if "object_view" not in captions:
        captions["object_view"] = {}

    filename = os.path.basename(image_path)
    if object_type not in captions["object_view"]:
        captions["object_view"][object_type] = {}
    captions["object_view"][object_type][filename] = caption

    with open(captions_file, "w", encoding="utf-8") as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)


def process_object_view_json(
    json_path: str,
    assets_dir: str,
    captions_file: str,
    model_name: str,
    base_url: str,
):
    """Process a single object view JSON file and generate captions for its states"""
    object_type = Path(json_path).stem  # Get filename without extension
    with open(json_path, "r", encoding="utf-8") as f:
        object_data = json.load(f)

    for state in object_data["scene_states"]:
        image_path = os.path.join(
            assets_dir, "image", "object_view", object_type, state["image_path"]
        )

        if not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}")
            continue

        # Create prompt based on state information
        receptacle_state = state["object_states"]["receptacle_state"]
        items = state["object_states"]["items"]

        # Convert items list to comma-separated string with quotes
        items_str = ", ".join(f"'{item}'" for item in items) if items else ""

        prompt = f"""This image is a close-up view of an object '{object_type}'. {f"In {object_type}, the following objects are present: {items_str}" if items else ""}
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

        update_captions_json(captions_file, object_type, state["image_path"], caption)


@click.command()
@click.option("-a", "--assets-dir", type=str, required=True)
@click.option("-m", "--model-name", type=str, required=True)
@click.option("-u", "--agent-hostname", type=str, required=False, default=None)
@click.option("-p", "--agent-port", type=int, required=False, default=None)
def main(assets_dir, model_name, agent_hostname, agent_port):
    assets_dir = Path(assets_dir).expanduser().absolute()

    object_view_dir = assets_dir / "mapping" / "object_view"
    if not object_view_dir.exists():
        raise ValueError(f"Directory not found: {object_view_dir}")

    captions_file = assets_dir / "captions" / model_name / "image_captions.json"
    captions_file.parent.mkdir(parents=True, exist_ok=True)

    # Get base url for vLLM (None if using OpenAI)
    base_url = f"http://{agent_hostname}:{agent_port}/v1" if agent_hostname and agent_port else None
    if base_url:
        print("Using vLLM server at:", base_url)
    else:
        print("Using OpenAI API")
    # Process json
    for json_path in object_view_dir.glob("*.json"):
        print(f"\nProcessing object view file: {json_path.name}")
        process_object_view_json(
            str(json_path),
            str(assets_dir),
            str(captions_file),
            model_name,
            base_url,
        )

    print(f"\nObject view captions have been saved to {captions_file}")


if __name__ == "__main__":
    main()
