#!/bin/bash

cd $(dirname ${BASH_SOURCE[0]})/../..

# Variables
ASSET_ROOT="./assets"
# Get your model name (refer to: `src/vis_escape/config/yamls/models.yaml`)
# MODEL_NAME="your_model_name"
# AGENT_HOSTNAME="your_hostname"
# AGENT_PORT="PORT_NUMBER[INT:10000-65535]"

# example:
MODEL_NAME="llava"
AGENT_HOSTNAME="localhost"
AGENT_PORT=39002

# Initialize Virtualenvs
eval "$($MAMBA_EXE shell hook --shell=bash)"
conda activate vis-escape


ARGS_STRING=" \
    --assets-dir $ASSET_ROOT/room1 \
    --model-name $MODEL_NAME \
    --agent-hostname $AGENT_HOSTNAME \
    --agent-port $AGENT_PORT
"
python -m vis_escape.config.caption_item_view $ARGS_STRING
python -m vis_escape.config.caption_wall_view $ARGS_STRING
python -m vis_escape.config.caption_object_view $ARGS_STRING
