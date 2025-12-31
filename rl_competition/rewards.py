import numpy as np
from constants import (
    GRID_SIZE, MAX_HP, DAMAGE_PER_HIT,
    DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT
)

def _los(me, enemy, grid):
    """True iff enemy is in straight line of sight from me (no wall)."""
    mx, my = me["x"], me["y"]
    ex, ey = enemy["x"], enemy["y"]

    if mx == ex:
        if my > ey:
            # enemy above
            for y in range(ey + 1, my):
                if grid[y, mx] == 1:
                    return False
            return True
        if my < ey:
            # enemy below
            for y in range(my + 1, ey):
                if grid[y, mx] == 1:
                    return False
            return True

    if my == ey:
        if mx > ex:
            for x in range(ex + 1, mx):
                if grid[my, x] == 1:
                    return False
            return True
        if mx < ex:
            for x in range(mx + 1, ex):
                if grid[my, x] == 1:
                    return False
            return True

    return False

def _facing_enemy(me, enemy):
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
    """Reward shaping tuned for: win-rate first, then HP diff, then speed."""
    me0, en0 = prev_state["me"], prev_state["enemy"]
    me1, en1 = curr_state["me"], curr_state["enemy"]
    grid = curr_state.get("grid", prev_state.get("grid"))

    reward = 0.0

    # Terminal
    if events.get("winner") == "me":
        reward += 120.0
    elif events.get("winner") == "enemy":
        reward -= 120.0

    # HP delta shaping (dense and stable)
    # Positive if we improved HP diff this step.
    hp_diff0 = (me0["hp"] - en0["hp"])
    hp_diff1 = (me1["hp"] - en1["hp"])
    reward += 0.8 * float(hp_diff1 - hp_diff0)

    # Hits (extra sparse bonus/penalty)
    if events.get("hit_enemy"):
        reward += 12.0
    if events.get("hit_by_enemy"):
        reward -= 14.0

    # Prefer faster resolution (small, so it doesn't overpower learning)
    reward -= 0.015

    # Distance shaping: only mild (prevents reckless chasing)
    prev_dist = abs(me0["x"] - en0["x"]) + abs(me0["y"] - en0["y"])
    curr_dist = abs(me1["x"] - en1["x"]) + abs(me1["y"] - en1["y"])
    reward += 0.03 * float(prev_dist - curr_dist)

    # Tactical shaping
    # 1) Prefer having line-of-sight and being oriented correctly (helps learning to aim)
    prev_los = _los(me0, en0, grid)
    curr_los = _los(me1, en1, grid)
    reward += 0.6 * (1.0 if curr_los else 0.0) - 0.6 * (1.0 if prev_los else 0.0)

    prev_face = _facing_enemy(me0, en0)
    curr_face = _facing_enemy(me1, en1)
    reward += 0.25 * (1.0 if curr_face else 0.0) - 0.25 * (1.0 if prev_face else 0.0)

    # 2) Shield usage: reward when shield is active while under threat (enemy has LOS)
    enemy_has_los_prev = _los(en0, me0, grid)
    enemy_has_los_curr = _los(en1, me1, grid)
    if me1.get("shield_steps", 0) > 0 and (enemy_has_los_prev or enemy_has_los_curr):
        reward += 0.20

    # 3) Light penalty for wasting shots (ammo decreased without hitting this step)
    # (We can't see the action, but we can infer a shot if ammo went down.)
    if me1.get("ammo", 0) < me0.get("ammo", 0) and not events.get("hit_enemy"):
        reward -= 0.25

    return float(reward)
