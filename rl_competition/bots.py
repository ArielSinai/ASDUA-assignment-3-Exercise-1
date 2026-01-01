from constants import *

class BaseBot:
    def act(self, state, rng):
        """
        state: A dictionary containing at least:
            'me': {'x', 'y', 'dir', 'cooldown', 'hp', 'ammo', 'reload', 'shield_steps', 'shield_cooldown', ...}
            'enemy': {'x', 'y', 'dir', 'cooldown', 'hp', 'ammo', 'reload', 'shield_steps', 'shield_cooldown', ...}
            'bullets': list of {'x', 'y', 'dir', 'owner'}
            'grid': 2D numpy array (1 = wall, 0 = empty)
        rng: numpy random generator
        """
        return ACTION_DO_NOTHING

class RandomBot(BaseBot):
    def act(self, state, rng):
        me = state["me"]
        grid = state["grid"]
        actions = [ACTION_MOVE_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_SHOOT]

        # Filter out forward moves that would hit a wall or go out of bounds
        nx = me["x"] + DX[me["dir"]]
        ny = me["y"] + DY[me["dir"]]
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE) or grid[ny, nx] == 1:
            actions = [a for a in actions if a != ACTION_MOVE_FORWARD]

        # Filter out shooting when the tank cannot actually shoot
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
        me = state['me']
        enemy = state['enemy']
        
        # If enemy has a clear shot on us and our shield is ready, use it
        if self._can_use_shield(me) and self._can_hit_enemy(enemy, me, state['grid']):
            return ACTION_SHIELD
        
        # If in line of sight and the gun is ready, shoot
        if self._can_hit_enemy(me, enemy, state['grid']) and self._can_shoot(me):
            return ACTION_SHOOT
        
        # Move towards enemy
        target_dir = self._get_dir_to(me['x'], me['y'], enemy['x'], enemy['y'])
        if me['dir'] == target_dir:
            return ACTION_MOVE_FORWARD
        else:
            diff = (target_dir - me['dir']) % 4
            if diff == 1:
                return ACTION_TURN_RIGHT
            else:
                return ACTION_TURN_LEFT

    def _get_dir_to(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            return DIR_RIGHT if dx > 0 else DIR_LEFT
        else:
            return DIR_DOWN if dy > 0 else DIR_UP

    def _can_hit_enemy(self, me, enemy, grid):
        if me['dir'] == DIR_UP:
            if me['x'] == enemy['x'] and me['y'] > enemy['y']:
                for y in range(enemy['y'] + 1, me['y']):
                    if grid[y, me['x']] == 1:
                        return False
                return True
        elif me['dir'] == DIR_DOWN:
            if me['x'] == enemy['x'] and me['y'] < enemy['y']:
                for y in range(me['y'] + 1, enemy['y']):
                    if grid[y, me['x']] == 1:
                        return False
                return True
        elif me['dir'] == DIR_LEFT:
            if me['y'] == enemy['y'] and me['x'] > enemy['x']:
                for x in range(enemy['x'] + 1, me['x']):
                    if grid[me['y'], x] == 1:
                        return False
                return True
        elif me['dir'] == DIR_RIGHT:
            if me['y'] == enemy['y'] and me['x'] < enemy['x']:
                for x in range(me['x'] + 1, enemy['x']):
                    if grid[me['y'], x] == 1:
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
        me = state['me']
        enemy = state['enemy']
        aggr = AggressiveBot()
        
        # If enemy can hit us and shield is ready, use it
        if aggr._can_use_shield(me) and aggr._can_hit_enemy(enemy, me, state['grid']):
            return ACTION_SHIELD
        
        # If can shoot, shoot
        if aggr._can_hit_enemy(me, enemy, state['grid']) and aggr._can_shoot(me):
            return ACTION_SHOOT
        
        # Face enemy
        target_dir = aggr._get_dir_to(me['x'], me['y'], enemy['x'], enemy['y'])
        if me['dir'] != target_dir:
            diff = (target_dir - me['dir']) % 4
            if diff == 1:
                return ACTION_TURN_RIGHT
            else:
                return ACTION_TURN_LEFT
        
        return ACTION_DO_NOTHING

class EvadeBot(BaseBot):
    def act(self, state, rng):
        me = state["me"]
        enemy = state["enemy"]
        grid = state["grid"]

        # Direction from me to enemy
        target_dir = self._get_dir_to(me["x"], me["y"], enemy["x"], enemy["y"])
        # Direction pointing away from enemy
        away_dir = (target_dir + 2) % 4

        # If we are already facing away and the tile ahead is free, move forward
        if me["dir"] == away_dir:
            nx = me["x"] + DX[away_dir]
            ny = me["y"] + DY[away_dir]
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny, nx] == 0:
                return ACTION_MOVE_FORWARD

        # Otherwise, turn towards the away direction
        diff = (away_dir - me["dir"]) % 4
        if diff == 1:
            return ACTION_TURN_RIGHT
        elif diff == 3:
            return ACTION_TURN_LEFT
        elif diff == 2:
            return ACTION_TURN_LEFT

        return ACTION_DO_NOTHING

    def _get_dir_to(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            return DIR_RIGHT if dx > 0 else DIR_LEFT
        else:
            return DIR_DOWN if dy > 0 else DIR_UP

class TacticalBot(BaseBot):
    """Advanced bot that combines aggression with tactical retreats and HP-based decisions."""
    
    def act(self, state, rng):
        me = state['me']
        enemy = state['enemy']
        grid = state['grid']
        
        # Use shield if enemy can hit us
        if self._can_use_shield(me) and self._can_hit_enemy(enemy, me, grid):
            return ACTION_SHIELD
        
        # If low HP, prioritize evasion
        if me['hp'] < 30:
            return self._evade_move(me, enemy, grid)
        
        # If enemy is low HP and we can shoot, finish them
        if enemy['hp'] < 30 and self._can_shoot(me):
            if self._can_hit_enemy(me, enemy, grid):
                return ACTION_SHOOT
            # Turn to face if close
            target_dir = self._get_dir_to(me['x'], me['y'], enemy['x'], enemy['y'])
            if me['dir'] != target_dir:
                diff = (target_dir - me['dir']) % 4
                return ACTION_TURN_RIGHT if diff == 1 else ACTION_TURN_LEFT
        
        # Standard combat: shoot if aligned
        if self._can_hit_enemy(me, enemy, grid) and self._can_shoot(me):
            return ACTION_SHOOT
        
        # Move toward enemy
        target_dir = self._get_dir_to(me['x'], me['y'], enemy['x'], enemy['y'])
        if me['dir'] == target_dir:
            nx = me['x'] + DX[target_dir]
            ny = me['y'] + DY[target_dir]
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny, nx] == 0:
                return ACTION_MOVE_FORWARD
        
        # Turn toward target
        diff = (target_dir - me['dir']) % 4
        return ACTION_TURN_RIGHT if diff == 1 else ACTION_TURN_LEFT
    
    def _evade_move(self, me, enemy, grid):
        """Move away from enemy when low on HP."""
        away_dir = (self._get_dir_to(me['x'], me['y'], enemy['x'], enemy['y']) + 2) % 4
        
        if me['dir'] == away_dir:
            nx = me['x'] + DX[away_dir]
            ny = me['y'] + DY[away_dir]
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny, nx] == 0:
                return ACTION_MOVE_FORWARD
        
        diff = (away_dir - me['dir']) % 4
        return ACTION_TURN_RIGHT if diff == 1 else ACTION_TURN_LEFT
    
    def _get_dir_to(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            return DIR_RIGHT if dx > 0 else DIR_LEFT
        else:
            return DIR_DOWN if dy > 0 else DIR_UP
    
    def _can_hit_enemy(self, me, enemy, grid):
        if me['dir'] == DIR_UP:
            if me['x'] == enemy['x'] and me['y'] > enemy['y']:
                for y in range(enemy['y'] + 1, me['y']):
                    if grid[y, me['x']] == 1:
                        return False
                return True
        elif me['dir'] == DIR_DOWN:
            if me['x'] == enemy['x'] and me['y'] < enemy['y']:
                for y in range(me['y'] + 1, enemy['y']):
                    if grid[y, me['x']] == 1:
                        return False
                return True
        elif me['dir'] == DIR_LEFT:
            if me['y'] == enemy['y'] and me['x'] > enemy['x']:
                for x in range(enemy['x'] + 1, me['x']):
                    if grid[me['y'], x] == 1:
                        return False
                return True
        elif me['dir'] == DIR_RIGHT:
            if me['y'] == enemy['y'] and me['x'] < enemy['x']:
                for x in range(me['x'] + 1, enemy['x']):
                    if grid[me['y'], x] == 1:
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

# Bot pool for training
BOT_POOL = {
    "random": RandomBot(),
    "aggressive": AggressiveBot(),
    "camper": CamperBot(),
    "evade": EvadeBot(),
    "tactical": TacticalBot(),
}
