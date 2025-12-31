from constants import *

class BaseBot:
    def act(self, state, rng):
        return ACTION_DO_NOTHING

class RandomBot(BaseBot):
    def act(self, state, rng):
        me = state["me"]
        grid = state["grid"]

        actions = [ACTION_MOVE_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_SHOOT]

        nx = me["x"] + DX[me["dir"]]
        ny = me["y"] + DY[me["dir"]]
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE) or grid[ny, nx] == 1:
            actions = [a for a in actions if a != ACTION_MOVE_FORWARD]

        can_shoot = (
            me.get("cooldown", 0) == 0
            and me.get("ammo", 0) > 0
            and me.get("reload", 0) == 0
        )
        if not can_shoot:
            actions = [a for a in actions if a != ACTION_SHOOT]

        if not actions:
            return ACTION_TURN_LEFT

        return rng.choice(actions)

class AggressiveBot(BaseBot):
    def act(self, state, rng):
        me = state["me"]
        enemy = state["enemy"]

        if self._can_use_shield(me) and self._can_hit_enemy(enemy, me, state["grid"]):
            return ACTION_SHIELD

        if self._can_hit_enemy(me, enemy, state["grid"]) and self._can_shoot(me):
            return ACTION_SHOOT

        target_dir = self._get_dir_to(me["x"], me["y"], enemy["x"], enemy["y"])
        if me["dir"] == target_dir:
            return ACTION_MOVE_FORWARD
        diff = (target_dir - me["dir"]) % 4
        return ACTION_TURN_RIGHT if diff == 1 else ACTION_TURN_LEFT

    def _get_dir_to(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            return DIR_RIGHT if dx > 0 else DIR_LEFT
        return DIR_DOWN if dy > 0 else DIR_UP

    def _can_hit_enemy(self, me, enemy, grid):
        if me["dir"] == DIR_UP and me["x"] == enemy["x"] and me["y"] > enemy["y"]:
            for y in range(enemy["y"] + 1, me["y"]):
                if grid[y, me["x"]] == 1:
                    return False
            return True
        if me["dir"] == DIR_DOWN and me["x"] == enemy["x"] and me["y"] < enemy["y"]:
            for y in range(me["y"] + 1, enemy["y"]):
                if grid[y, me["x"]] == 1:
                    return False
            return True
        if me["dir"] == DIR_LEFT and me["y"] == enemy["y"] and me["x"] > enemy["x"]:
            for x in range(enemy["x"] + 1, me["x"]):
                if grid[me["y"], x] == 1:
                    return False
            return True
        if me["dir"] == DIR_RIGHT and me["y"] == enemy["y"] and me["x"] < enemy["x"]:
            for x in range(me["x"] + 1, enemy["x"]):
                if grid[me["y"], x] == 1:
                    return False
            return True
        return False

    def _can_shoot(self, tank):
        return (
            tank.get("cooldown", 0) == 0
            and tank.get("ammo", 0) > 0
            and tank.get("reload", 0) == 0
        )

    def _can_use_shield(self, tank):
        return (
            tank.get("shield_steps", 0) == 0
            and tank.get("shield_cooldown", 0) == 0
        )

class CamperBot(BaseBot):
    def act(self, state, rng):
        me = state["me"]
        enemy = state["enemy"]

        aggr = AggressiveBot()
        if aggr._can_use_shield(me) and aggr._can_hit_enemy(enemy, me, state["grid"]):
            return ACTION_SHIELD

        if aggr._can_hit_enemy(me, enemy, state["grid"]) and aggr._can_shoot(me):
            return ACTION_SHOOT

        target_dir = aggr._get_dir_to(me["x"], me["y"], enemy["x"], enemy["y"])
        if me["dir"] != target_dir:
            diff = (target_dir - me["dir"]) % 4
            return ACTION_TURN_RIGHT if diff == 1 else ACTION_TURN_LEFT

        return ACTION_DO_NOTHING

class EvadeBot(BaseBot):
    def act(self, state, rng):
        me = state["me"]
        enemy = state["enemy"]
        grid = state["grid"]

        target_dir = self._get_dir_to(me["x"], me["y"], enemy["x"], enemy["y"])
        away_dir = (target_dir + 2) % 4

        if me["dir"] == away_dir:
            nx = me["x"] + DX[away_dir]
            ny = me["y"] + DY[away_dir]
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny, nx] == 0:
                return ACTION_MOVE_FORWARD

        diff = (away_dir - me["dir"]) % 4
        if diff == 1:
            return ACTION_TURN_RIGHT
        if diff == 3:
            return ACTION_TURN_LEFT
        if diff == 2:
            return ACTION_TURN_LEFT

        return ACTION_DO_NOTHING

    def _get_dir_to(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            return DIR_RIGHT if dx > 0 else DIR_LEFT
        return DIR_DOWN if dy > 0 else DIR_UP

class StrafeBot(BaseBot):
    """Moves to keep walls between it and you; shoots when it has a lane."""
    def act(self, state, rng):
        me = state["me"]
        enemy = state["enemy"]
        grid = state["grid"]
        aggr = AggressiveBot()

        # Defensive shield if needed
        if aggr._can_use_shield(me) and aggr._can_hit_enemy(enemy, me, grid):
            return ACTION_SHIELD

        # If we can shoot safely, shoot
        if aggr._can_hit_enemy(me, enemy, grid) and aggr._can_shoot(me):
            return ACTION_SHOOT

        # Try to step sideways relative to enemy direction
        dir_to_enemy = aggr._get_dir_to(me["x"], me["y"], enemy["x"], enemy["y"])
        side_dir = (dir_to_enemy + (1 if rng.random() < 0.5 else 3)) % 4

        # Turn towards side_dir then move
        if me["dir"] != side_dir:
            diff = (side_dir - me["dir"]) % 4
            return ACTION_TURN_RIGHT if diff == 1 else ACTION_TURN_LEFT

        nx = me["x"] + DX[me["dir"]]
        ny = me["y"] + DY[me["dir"]]
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny, nx] == 0:
            return ACTION_MOVE_FORWARD

        return ACTION_TURN_LEFT

BOT_POOL = {
    "random": RandomBot(),
    "aggressive": AggressiveBot(),
    "camper": CamperBot(),
    "evade": EvadeBot(),
    "strafe": StrafeBot(),
}
