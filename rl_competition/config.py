import torch

# Random Seed (for reproducibility)
SEED = 42

# Training Hyperparameters
NUM_EPISODES = 10000  # Increased for better learning
MAX_STEPS_PER_EPISODE = 120  # Slightly longer episodes

LEARNING_RATE = 2e-4  # Lower for stability
GAMMA = 0.99  # Standard discount factor
BATCH_SIZE = 128
BUFFER_SIZE = 80000  # Large buffer for diverse experiences
MIN_BUFFER_SIZE = 5000  # Start training with more data

# Epsilon Greedy Schedule
EPS_START = 1.0
EPS_END = 0.05
EPS_DECAY = 0.999  # Unused when EPS_DECAY_STEPS > 0
EPS_DECAY_STEPS = 5000  # Decay linearly over this many episodes

# DQN Specifics
TARGET_UPDATE_FREQ = 5000  # Update target network every N steps
TRAIN_FREQ = 1  # Train every step

# Visualization (pygame)
USE_PYGAME_RENDER = False  # Set to True only for debugging

# Checkpointing
CHECKPOINT_DIR = "checkpoints"
MODEL_SAVE_PATH = "checkpoints/agent.pt"
MODEL_CONFIG_PATH = "checkpoints/model_config.json"

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
if torch.backends.mps.is_available():
    DEVICE = "mps"
