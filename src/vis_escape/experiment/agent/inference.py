import base64
import io
import time

from PIL import Image

from vis_escape.config.models import get_model_tag


def _encode_image(image_path: str) -> str:
    with Image.open(image_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


def run_inference_text(
    clients,
    model: str,
    prompt: str,
    prompt_type: str = "action",
    system_prompt: str = None,
) -> str:
    if "gpt" in model:
        client = clients["gpt"]
        retry_count = 0
        while retry_count < 3:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error during API call: {e}")
                retry_count += 1
                time.sleep(5)
        return ""
    else:
        client = clients[model]
        real_model_name = get_model_tag(model)
        r1_error_count = 0
        retry_count = 0

        while retry_count < 3:
            try:
                if system_prompt:
                    print(
                        f"Running Inference with {real_model_name} with system prompt"
                    )
                    chat_response = client.chat.completions.create(
                        model=real_model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                    )
                else:
                    print(f"Running Inference with {real_model_name}")
                    chat_response = client.chat.completions.create(
                        model=real_model_name,
                        messages=[
                            {"role": "user", "content": prompt},
                        ],
                    )

                if "R1" in real_model_name:
                    if (
                        "</think>"
                        not in chat_response.choices[0].message.content.strip()
                    ):
                        r1_error_count += 1
                        if r1_error_count >= 3:
                            print(
                                "R1 model failed to return <think> tag 3 times, returning response anyway"
                            )
                            return chat_response.choices[0].message.content.strip()
                        raise Exception("R1 model did not return <think> tag")
                    else:
                        return (
                            chat_response.choices[0]
                            .message.content.strip()
                            .split("</think>")[1]
                            .strip()
                        )
                else:
                    return chat_response.choices[0].message.content.strip()

            except Exception as e:
                print(f"Error during API call: {e}")
                retry_count += 1
                time.sleep(5)
        return ""


def run_inference_vision(clients, model_name: str, image_path: str, prompt: str) -> str:
    if "gpt" in model_name:
        client = clients["gpt"]
        return run_inference_vision_gpt(client, model_name, image_path, prompt)
    else:
        client = clients[model_name]
        real_model_name = get_model_tag(model_name)

        print(f"Running Inference with {real_model_name} WITH image!")
        try:
            base64_image = _encode_image(image_path)
            chat_response = client.chat.completions.create(
                model=real_model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
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
            return ""


def run_inference_vision_gpt(
    client, model_name: str, image_path: str, prompt: str, system_prompt: str = None
) -> str:
    print("------------------Inference with Vision!------------------------------")
    base64_image = _encode_image(image_path)
    while True:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "low",
                                },
                            },
                        ],
                    }
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during API call: {e}")
            time.sleep(5)
            continue


def run_inference_vision_noimage(
    clients,
    model_name: str,
    prompt: str,
    prompt_type: str = "action",
    system_prompt: str = None,
) -> str:
    if "gpt" in model_name:
        raise NotImplementedError
        # client = clients["gpt"]
        # return run_inference_vision_gpt_noimage(client, model_name, prompt)
    else:
        client = clients[model_name]
        real_model_name = get_model_tag(model_name)

        try:
            if system_prompt:
                print(
                    f"Running Inference with {real_model_name} WITHOUT image, with system prompt!"
                )

                chat_response = client.chat.completions.create(
                    model=real_model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                            ],
                        },
                    ],
                )
            else:
                print(
                    f"Running Inference with {real_model_name} WITHOUT image, without system prompt!"
                )
                chat_response = client.chat.completions.create(
                    model=real_model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                )
            return chat_response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during API call: {e}")
            return ""


def run_inference_vision_caption(
    client, image_path: str, prompt: str, model: str = "gpt-4o-mini"
) -> str:
    base64_image = _encode_image(image_path)
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
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
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during API call: {e}")
            time.sleep(5)
            continue
