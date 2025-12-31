import torch

# Repro
SEED = 42

# Training
NUM_EPISODES = 8000
MAX_STEPS_PER_EPISODE = 120

LEARNING_RATE = 3e-4
GAMMA = 0.985
BATCH_SIZE = 128
BUFFER_SIZE = 80_000
MIN_BUFFER_SIZE = 5_000

# Exploration (linear)
EPS_START = 1.0
EPS_END = 0.05
EPS_DECAY = 0.999  # unused when EPS_DECAY_STEPS > 0
EPS_DECAY_STEPS = 4000  # reach EPS_END around episode ~4000

# DQN
TARGET_UPDATE_FREQ = 1500  # NOTE: in train.py this is in *steps* (global_step)
TRAIN_FREQ = 1

# Rendering
USE_PYGAME_RENDER = False

# Checkpoints
CHECKPOINT_DIR = "checkpoints"
MODEL_SAVE_PATH = "checkpoints/agent.pt"
MODEL_CONFIG_PATH = "checkpoints/model_config.json"

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
if torch.backends.mps.is_available():
    DEVICE = "mps"
