from pathlib import Path

import yaml


def get_model_tag(name, model_cfg=None):
    if not model_cfg:
        model_cfg = Path(__file__).parent / "yamls" / "models.yaml"

    with open(model_cfg, "r") as f:
        model_table = yaml.safe_load(f)

    return model_table.get(name, None)


def get_model_long(model_cfg=None):
    if not model_cfg:
        model_cfg = Path(__file__).parent / "yamls" / "models_long.yaml"

    with open(model_cfg, "r") as f:
        model_table = yaml.safe_load(f)

    return model_table


def get_preset(preset_cfg=None):
    if not preset_cfg:
        preset_cfg = Path(__file__).parent / "yamls" / "preset.yaml"

    with open(preset_cfg, "r") as f:
        preset = yaml.safe_load(f)

    return preset


if __name__ == "__main__":
    print(get_model_tag("llava"))
