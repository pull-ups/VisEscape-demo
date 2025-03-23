# VisEscape: A Benchmark for Evaluating Exploration-driven Decision-making in Virtual Escape Rooms

**Seungwon Lim**, **Sungwoong Kim**, **Jihwan Yu**, **Sungjae Lee**, **Jiwan Chung**, **Youngjae Yu**

Yonsei University

[![arXiv](https://img.shields.io/badge/arXiv-2503.14427-b31b1b.svg)](https://arxiv.org/abs/2503.14427)
## Abstract
> Escape rooms present a unique cognitive challenge that demands exploration-driven planning: players should actively search their environment, continuously update their knowledge based on new discoveries, and connect disparate clues to determine which elements are relevant to their objectives. Motivated by this, we introduce VisEscape, a benchmark of 20 virtual escape rooms specifically designed to evaluate AI models under these challenging conditions, where success depends not only on solving isolated puzzles but also on iteratively constructing and refining spatial-temporal knowledge of a dynamically changing environment. On VisEscape, we observed that even state-of-the-art multimodal models generally fail to escape the rooms, showing considerable variation in their levels of progress and trajectories. To address this issue, we propose VisEscaper, which effectively integrates Memory, Feedback, and ReAct modules, demonstrating significant improvements by performing 3.7 times more effectively and 5.0 times more efficiently on average.


## Installation - for client and running game by yourself
Install on your own machine.  

1. Clone this repository.
    ```bash
    git clone https://github.com/pull-ups/VisEscape.git
    cd VisEscape
    ```
2. [Optional] Create & Activate your virtual env.
    ```bash
    conda create -n vis-escape python=3.9
    conda activate 
    ```
3. Install via poetry.
    ```bash
    pip install poetry

    # Optional: Deactivate auto virtualenv creation
    poetry config virtualenvs.create false

    poetry install
    ```

## Installation - for vLLM server to run open-source models
Install on your server.  
prerequisite: `cuda-toolkit>=12.4`  

1. [Optional] Create & Activate your virtual env.
    ```bash
    conda create -n vis-escape-server python=3.11
    conda activate vis-escape-server
    ```
2. Install `vllm==0.7.3`
    ```bash
    pip install vllm==0.7.3
    ```

## Execution - For Human
You can play the escape rooms game by yourself by executing:
```bash
python scripts/run_ui.py -r room[room_number]
```

## Execution - For AI models

### 1. Launch server (only for open-source models)

Since experiment for VisEscape requires interaction with game environment, we recommend you to launch vLLM server before running experiments, instead of directly calling inference API.

* Change variables in `scripts/config/make_caption.sh`
    - Set `CUDA_VISIBLE_DEVICES` to select GPUs
    - `NUM_GPUS`: Number of GPUs you want to parallelize
    - `VLLM_PORT`: Integer under 65536 (Where you serve)
    - `HF_MODEL_NAME`: Huggingface model tag
    - `MAX_MODEL_LEN`: Max token length

* Execute:
    ```bash
    bash ./scripts/server/vllm.sh
    ```
    Then you can access your vLLM server at `http://0.0.0.0:[VLLM_PORT]/v1`.
### 2. Make captions for each image observations
Since some modules require captions for each image observations instead of raw images, you need to make captions for each image observations before running experiments.  

- For open-source models:
    * Change variables in `scripts/config/make_caption.sh`
        - `ASSET_ROOT`: Directory of ```/assets```
        - `MODEL_NAME`: Model name in short. (see: `src/vis_escape/config/yamls/models.yaml`)
        - `AGENT_HOSTNAME`: Your vLLM server's hostname
        - `AGENT_PORT`: Your vLLM server's port (`VLLM_PORT` above)
    * Execute:
        ```bash
        bash ./scripts/config/make_caption.sh
        ```
        
- For closed-source models(e.g., GPT-4o-mini):
    * Change variables in `scripts/config/make_caption_openai.sh`
        - `ASSET_ROOT`: Directory of ```/assets```
        - `MODEL_NAME`: Model name in short. (see: `src/vis_escape/config/yamls/models.yaml`)
        - `AGENT_HOSTNAME`: Any value
        - `AGENT_PORT`: Any value
    * Execute:
        ```bash
        bash ./scripts/config/make_caption.sh
        ```

### 3. Run experiments
For both open-source models and closed-source models, you can run experiments by executing:
```bash
python scripts/run_ui.py -r room[room_number] 
                         -m [model_name]
                         -n [num_experiments]
                         -t [hint/no_hint]
                         -r [vlm/socratic]
```
Then the metadata for each step and the final result will be saved in `./scripts/results/`.

**More codes and datasets will be available soon!**

