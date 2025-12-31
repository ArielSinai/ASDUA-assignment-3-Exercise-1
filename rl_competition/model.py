import torch
import torch.nn as nn

# Student Editable: Network Architecture
# Constraints: Max 3 hidden layers, max 256 neurons per layer.
HIDDEN_SIZES = [128, 128]

class DQN(nn.Module):
    def __init__(self, obs_dim, action_dim, hidden_sizes=None):
        super().__init__()

        if hidden_sizes is None:
            hidden_sizes = HIDDEN_SIZES

        self.hidden_sizes = hidden_sizes
        self.obs_dim = obs_dim
        self.action_dim = action_dim

        layers = []
        in_dim = obs_dim
        for h in hidden_sizes:
            layers.append(nn.Linear(in_dim, h))
            layers.append(nn.ReLU())
            in_dim = h
        layers.append(nn.Linear(in_dim, action_dim))

        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)
