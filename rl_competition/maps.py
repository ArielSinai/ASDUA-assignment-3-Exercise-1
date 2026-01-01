import numpy as np
from constants import GRID_SIZE

# Map definitions
# 0: Empty
# 1: Wall

# Base grid
MAP_EMPTY = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

# Add border walls
MAP_EMPTY[0, :] = 1
MAP_EMPTY[-1, :] = 1
MAP_EMPTY[:, 0] = 1
MAP_EMPTY[:, -1] = 1

# Helper indices
MID = GRID_SIZE // 2
INNER_START = 2
INNER_END = GRID_SIZE - 2

# Cross map
MAP_CROSS = MAP_EMPTY.copy()
MAP_CROSS[MID, INNER_START:INNER_END] = 1
MAP_CROSS[INNER_START:INNER_END, MID] = 1
MAP_CROSS[MID, MID] = 0

# Four pillars map
MAP_FOUR_PILLARS = MAP_EMPTY.copy()
PILLAR_OFFSET = 2
MAP_FOUR_PILLARS[MID - PILLAR_OFFSET, MID - PILLAR_OFFSET] = 1
MAP_FOUR_PILLARS[MID - PILLAR_OFFSET, MID + PILLAR_OFFSET] = 1
MAP_FOUR_PILLARS[MID + PILLAR_OFFSET, MID - PILLAR_OFFSET] = 1
MAP_FOUR_PILLARS[MID + PILLAR_OFFSET, MID + PILLAR_OFFSET] = 1

# Diagonal map
MAP_DIAGONAL = MAP_EMPTY.copy()
for i in range(INNER_START, INNER_END):
    MAP_DIAGONAL[i, i] = 1
    MAP_DIAGONAL[i, GRID_SIZE - 1 - i] = 1
MAP_DIAGONAL[MID, MID] = 0
MAP_DIAGONAL[INNER_START, INNER_START] = 0
MAP_DIAGONAL[INNER_START, GRID_SIZE - 1 - INNER_START] = 0
MAP_DIAGONAL[GRID_SIZE - 1 - INNER_START, INNER_START] = 0
MAP_DIAGONAL[GRID_SIZE - 1 - INNER_START, GRID_SIZE - 1 - INNER_START] = 0

# Corridors map (narrow passages)
MAP_CORRIDORS = MAP_EMPTY.copy()
for i in range(INNER_START, INNER_END, 3):
    MAP_CORRIDORS[i, INNER_START:INNER_END] = 1
# Clear middle corridor for movement
MAP_CORRIDORS[MID, :] = 0
MAP_CORRIDORS[:, MID] = 0

# Scattered obstacles map
MAP_SCATTERED = MAP_EMPTY.copy()
# Create scattered 2x2 blocks
positions = [
    (4, 4), (4, 10),
    (7, 7),
    (10, 4), (10, 10)
]
for py, px in positions:
    if py < GRID_SIZE - 2 and px < GRID_SIZE - 2:
        MAP_SCATTERED[py:py+2, px:px+2] = 1

MAP_POOL = {
    "empty": MAP_EMPTY,
    "cross": MAP_CROSS,
    "pillars": MAP_FOUR_PILLARS,
    "diagonal": MAP_DIAGONAL,
    "corridors": MAP_CORRIDORS,
    "scattered": MAP_SCATTERED,
}

def get_random_map(rng):
    """Selects a random map from the pool."""
    name = rng.choice(list(MAP_POOL.keys()))
    return MAP_POOL[name], name
