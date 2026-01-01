import numpy as np
from constants import DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT

def _los(me, enemy, grid):
    """Check if enemy is in line of sight (no walls blocking)."""
    mx, my = me["x"], me["y"]
    ex, ey = enemy["x"], enemy["y"]

    if mx == ex:
        if my > ey:
            # Enemy above
            for y in range(ey + 1, my):
                if grid[y, mx] == 1:
                    return False
            return True
        if my < ey:
            # Enemy below
            for y in range(my + 1, ey):
                if grid[y, mx] == 1:
                    return False
            return True

    if my == ey:
        if mx > ex:
            # Enemy to the left
            for x in range(ex + 1, mx):
                if grid[my, x] == 1:
                    return False
            return True
        if mx < ex:
            # Enemy to the right
            for x in range(mx + 1, ex):
                if grid[my, x] == 1:
                    return False
            return True

    return False

def _facing_enemy(me, enemy):
    """Check if tank is facing toward enemy."""
    mx, my = me["x"], me["y"]
    ex, ey = enemy["x"], enemy["y"]
    d = me["dir"]

    if d == DIR_UP:
        return mx == ex and my > ey
    if d == DIR_DOWN:
        return mx == ex and my < ey
    if d == DIR_LEFT:
        return my == ey and mx > ex
    if d == DIR_RIGHT:
        return my == ey and mx < ex
    return False

def compute_reward(prev_state, curr_state, events):
    """
    Balanced reward function optimized for win rate, HP difference, and speed.
    
    Args:
        prev_state: State before the action
        curr_state: State after the action
        events: Dictionary with 'winner', 'hit_enemy', 'hit_by_enemy', etc.
    
    Returns:
        float: Scalar reward
    """
    me0, en0 = prev_state["me"], prev_state["enemy"]
    me1, en1 = curr_state["me"], curr_state["enemy"]
    grid = curr_state.get("grid", prev_state.get("grid"))
    
    reward = 0.0
    
    # ===== TERMINAL OUTCOMES (Priority 1: Win Rate) =====
    if events.get("winner") == "me":
        reward += 100.0
    elif events.get("winner") == "enemy":
        reward -= 100.0
    
    # ===== DAMAGE EVENTS (Priority 2: HP Difference) =====
    # Direct hit feedback
    if events.get("hit_enemy"):
        reward += 15.0
    if events.get("hit_by_enemy"):
        reward -= 15.0
    
    # HP difference shaping (smooth gradient for learning)
    hp_diff_prev = me0["hp"] - en0["hp"]
    hp_diff_curr = me1["hp"] - en1["hp"]
    hp_diff_delta = hp_diff_curr - hp_diff_prev
    reward += 2.0 * hp_diff_delta
    
    # ===== SPEED INCENTIVE (Priority 3: Faster Wins) =====
    # Small step penalty to encourage efficiency
    reward -= 0.02
    
    # ===== TACTICAL POSITIONING =====
    # Reward good combat positioning (LOS + facing enemy)
    curr_los = _los(me1, en1, grid)
    curr_face = _facing_enemy(me1, en1)
    
    if curr_los and curr_face:
        reward += 0.5  # In position to shoot
    elif curr_los:
        reward += 0.2  # At least have sight
    
    # ===== DEFENSIVE PLAY =====
    # Reward smart shield usage when under threat
    enemy_los = _los(en1, me1, grid)
    if me1.get("shield_steps", 0) > 0 and enemy_los:
        reward += 0.3
    
    # ===== ENGAGEMENT DISTANCE =====
    # Moderate distance shaping (prevent passive play)
    prev_dist = abs(me0["x"] - en0["x"]) + abs(me0["y"] - en0["y"])
    curr_dist = abs(me1["x"] - en1["x"]) + abs(me1["y"] - en1["y"])
    
    if curr_dist < prev_dist:
        reward += 0.1  # Closing distance
    elif curr_dist > prev_dist and curr_dist > 8:
        reward -= 0.05  # Penalize retreating when far
    
    # ===== AMMO MANAGEMENT =====
    # Small penalty for missing shots
    if me1.get("ammo", 0) < me0.get("ammo", 0) and not events.get("hit_enemy"):
        reward -= 0.2
    
    return float(reward)
