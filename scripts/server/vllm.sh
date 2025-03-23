#!/bin/bash

# Variables
# export CUDA_VISIBLE_DEVICES=
# NUM_GPUS=
# VLLM_PORT=
# HF_MODEL_NAME=
# MAX_MODEL_LEN=

# example:
export CUDA_VISIBLE_DEVICES=0,1
NUM_GPUS=2
VLLM_PORT=39011
HF_MODEL_NAME="llava-hf/llava-v1.6-34b-hf"
MAX_MODEL_LEN=4096



# Initialize Virtualenvs
# Virtualenv should contain vllm==0.7.3
eval "$($MAMBA_EXE shell hook --shell=bash)"
conda activate vis-escape-server

# Serve vllm
vllm serve \
    --host 0.0.0.0 \
    --port $VLLM_PORT \
    --dtype bfloat16 \
    --max-model-len $MAX_MODEL_LEN \
    --tensor-parallel-size $NUM_GPUS \
    $HF_MODEL_NAME
