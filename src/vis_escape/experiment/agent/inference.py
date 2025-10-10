import base64
import io
import time

from PIL import Image


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
    """
    Run text inference using the specified model.
    
    Args:
        clients: Dictionary of model name -> OpenAI client
        model: Model name (e.g., 'gpt-4o-mini' or 'Qwen/Qwen2.5-32B-Instruct')
        prompt: The prompt text
        prompt_type: Type of prompt (for logging)
        system_prompt: Optional system prompt
    
    Returns:
        Generated text response
    """
    if model not in clients:
        raise ValueError(f"Model '{model}' not found in configured clients. Available models: {list(clients.keys())}")
    
    client = clients[model]
    r1_error_count = 0
    retry_count = 0

    while retry_count < 3:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                print(f"Running Inference with {model} with system prompt")
            else:
                print(f"Running Inference with {model}")
            
            messages.append({"role": "user", "content": prompt})
            
            chat_response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            
            response_text = chat_response.choices[0].message.content.strip()
            
            # Special handling for DeepSeek R1 models
            if "R1" in model or "DeepSeek" in model:
                if "</think>" not in response_text:
                    r1_error_count += 1
                    if r1_error_count >= 3:
                        print("R1 model failed to return <think> tag 3 times, returning response anyway")
                        return response_text
                    raise Exception("R1 model did not return <think> tag")
                else:
                    # Extract content after </think> tag
                    return response_text.split("</think>")[1].strip()
            else:
                return response_text

        except Exception as e:
            print(f"Error during API call: {e}")
            retry_count += 1
            time.sleep(5)
    
    return ""


def run_inference_vision(clients, model_name: str, image_path: str, prompt: str) -> str:
    """
    Run vision inference using the specified model.
    
    Args:
        clients: Dictionary of model name -> OpenAI client
        model_name: Model name (e.g., 'gpt-4o-mini' or 'OpenGVLab/InternVL2_5-38B')
        image_path: Path to the image file
        prompt: The prompt text
    
    Returns:
        Generated text response
    """
    if model_name not in clients:
        raise ValueError(f"Model '{model_name}' not found in configured clients. Available models: {list(clients.keys())}")
    
    client = clients[model_name]
    print(f"Running Vision Inference with {model_name}")
    
    retry_count = 0
    while retry_count < 3:
        try:
            base64_image = _encode_image(image_path)
            
            # Determine detail level based on model type
            image_config = {"url": f"data:image/jpeg;base64,{base64_image}"}
            if "gpt" in model_name.lower():
                image_config["detail"] = "low"
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": image_config,
                            },
                        ],
                    }
                ],
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error during Vision API call: {e}")
            retry_count += 1
            if retry_count < 3:
                time.sleep(5)
            else:
                return ""
    
    return ""


def run_inference_vision_noimage(
    clients,
    model_name: str,
    prompt: str,
    prompt_type: str = "action",
    system_prompt: str = None,
) -> str:
    """
    Run text-only inference (fallback for vision models).
    
    Args:
        clients: Dictionary of model name -> OpenAI client
        model_name: Model name
        prompt: The prompt text
        prompt_type: Type of prompt (for logging)
        system_prompt: Optional system prompt
    
    Returns:
        Generated text response
    """
    if model_name not in clients:
        raise ValueError(f"Model '{model_name}' not found in configured clients")
    
    client = clients[model_name]
    
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            print(f"Running Inference with {model_name} WITHOUT image, with system prompt!")
        else:
            print(f"Running Inference with {model_name} WITHOUT image, without system prompt!")
        
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        
        chat_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
        )
        return chat_response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error during API call: {e}")
        return ""


def run_inference_vision_caption(
    client, image_path: str, prompt: str, model: str = "gpt-4o-mini"
) -> str:
    """
    Run vision inference for captioning (backward compatibility).
    
    Args:
        client: OpenAI client instance
        image_path: Path to the image file
        prompt: The prompt text
        model: Model name
    
    Returns:
        Generated caption
    """
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
