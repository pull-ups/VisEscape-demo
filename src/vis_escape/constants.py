import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
EVALUATION_DIR = os.path.join(PROJECT_ROOT, "evaluation")

RUN_MODE = "base"

