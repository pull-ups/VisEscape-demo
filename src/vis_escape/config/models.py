from pathlib import Path

import yaml


def get_config(config_path=None):
    """
    Load the unified endpoints configuration file.
    
    Args:
        config_path: Optional path to config file. Defaults to endpoints.yaml
    
    Returns:
        Dictionary containing 'models' and 'presets' sections
    """
    if not config_path:
        config_path = Path(__file__).parent / "yamls" / "endpoints.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config


def get_model_config(model_name: str, config_path=None):
    """
    Get configuration for a specific model.
    
    Args:
        model_name: The model name (e.g., 'gpt-4o-mini' or 'Qwen/Qwen2.5-32B-Instruct')
        config_path: Optional path to config file
    
    Returns:
        Dictionary with model configuration (type, model_name/base_url)
    """
    config = get_config(config_path)
    return config["models"].get(model_name, None)


def get_preset(preset_name: str = None, config_path=None):
    """
    Get preset configuration or all presets.
    
    Args:
        preset_name: Optional preset name. If None, returns all presets.
        config_path: Optional path to config file
    
    Returns:
        Single preset dict or all presets dict
    """
    config = get_config(config_path)
    
    if preset_name:
        return config["presets"].get(preset_name, None)
    else:
        return config["presets"]


# Backward compatibility functions
def get_model_tag(name, model_cfg=None):
    """
    DEPRECATED: Returns the model name as-is for backward compatibility.
    In the new system, model names are used directly.
    """
    return name


def get_model_long(model_cfg=None):
    """
    DEPRECATED: Returns model endpoint configurations.
    Use get_config()['models'] instead.
    """
    config = get_config(model_cfg)
    
    # Convert new format to old format for backward compatibility
    result = {}
    for model_name, model_config in config["models"].items():
        if model_config["type"] == "vllm":
            # Extract hostname and port from base_url
            base_url = model_config["base_url"]
            # Parse "http://127.0.0.1:39001/v1"
            parts = base_url.replace("http://", "").replace("/v1", "").split(":")
            result[model_name] = {
                "hostname": parts[0],
                "port": int(parts[1])
            }
    
    return result


if __name__ == "__main__":
    config = get_config()
    print("Models:", list(config["models"].keys()))
    print("Presets:", list(config["presets"].keys()))
    print("\nExample preset 'gpt4o-mini':", get_preset("gpt4o-mini"))
