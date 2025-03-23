#!/bin/bash

cd $(dirname ${BASH_SOURCE[0]})/../..

# Variables
ASSET_ROOT="./assets"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
MODEL_NAME="gpt-4o-mini"
AGENT_HOSTNAME="localhost"
AGENT_PORT=0000



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
