import base64
import io
import os

import time
from openai import OpenAI
from PIL import Image

from vis_escape.config.models import get_model_tag


def _encode_image(image_path: str) -> str:
    with Image.open(image_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


def run_inference_vision_caption_vllm(
    image_path: str,
    prompt: str,
    model_name: str,
    base_url: str,
) -> str:

    real_model_name = get_model_tag(model_name)

    client = OpenAI(
        api_key="EMPTY",
        base_url=base_url,
    )
    try:
        base64_image = _encode_image(image_path)
        chat_response = client.chat.completions.create(
            model=real_model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        # NOTE: The prompt formatting with the image token `<image>` is not needed
                        # since the prompt will be processed automatically by the API server.
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating caption for {image_path}: {e}")
        return f"Failed to generate caption: {str(e)}"

def run_inference_vision_caption_openai(
    image_path: str,
    prompt: str,
    model_name: str,
) -> str:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    base64_image = _encode_image(image_path)
    while True:
        try:
            response = client.chat.completions.create(
                
                #model="gpt-4o-2024-08-06",
                #model="gpt-4o-mini",
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during API call: {e}")
            time.sleep(5)
            continue