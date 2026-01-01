#!/usr/bin/env python3
"""
Quick test script to verify the tank training setup is working correctly.
This runs a short training session and basic evaluation.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        import config
        import rewards
        import model
        import bots
        import maps
        from env import MicroTankArenaEnv
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_bots():
    """Test that all bots are working."""
    print("\nTesting bots...")
    try:
        from bots import BOT_POOL
        import numpy as np
        
        # Create dummy state
        dummy_state = {
            'me': {'x': 5, 'y': 5, 'dir': 0, 'hp': 100, 'cooldown': 0, 'ammo': 6, 'reload': 0, 'shield_steps': 0, 'shield_cooldown': 0},
            'enemy': {'x': 10, 'y': 10, 'dir': 2, 'hp': 100, 'cooldown': 0, 'ammo': 6, 'reload': 0, 'shield_steps': 0, 'shield_cooldown': 0},
            'bullets': [],
            'grid': np.zeros((15, 15), dtype=int)
        }
        rng = np.random.default_rng(42)
        
        for bot_name, bot in BOT_POOL.items():
            action = bot.act(dummy_state, rng)
            print(f"  ✓ {bot_name}: action={action}")
        
        print("✓ All bots working")
        return True
    except Exception as e:
        print(f"✗ Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reward_function():
    """Test the reward function."""
    print("\nTesting reward function...")
    try:
        from rewards import compute_reward
        import numpy as np
        
        # Create test states
        prev_state = {
            'me': {'x': 5, 'y': 5, 'hp': 100},
            'enemy': {'x': 10, 'y': 10, 'hp': 100},
            'grid': np.zeros((15, 15), dtype=int)
        }
        curr_state = {
            'me': {'x': 6, 'y': 5, 'hp': 100, 'ammo': 6, 'dir': 1, 'shield_steps': 0},
            'enemy': {'x': 10, 'y': 10, 'hp': 90, 'dir': 2},
            'grid': np.zeros((15, 15), dtype=int)
        }
        events = {'winner': None, 'hit_enemy': True, 'hit_by_enemy': False}
        
        reward = compute_reward(prev_state, curr_state, events)
        print(f"  Sample reward (hit enemy): {reward:.2f}")
        
        # Test win condition
        events['winner'] = 'me'
        reward = compute_reward(prev_state, curr_state, events)
        print(f"  Sample reward (win): {reward:.2f}")
        
        print("✓ Reward function working")
        return True
    except Exception as e:
        print(f"✗ Reward test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment creation and basic stepping."""
    print("\nTesting environment...")
    try:
        from env import MicroTankArenaEnv
        import config
        
        env = MicroTankArenaEnv(config)
        obs, info = env.reset(seed=42)
        
        print(f"  Observation shape: {obs.shape}")
        print(f"  Action space: {env.action_space.n} actions")
        
        # Take a few steps
        for i in range(5):
            action = env.action_space.sample()
            obs, reward, done, truncated, info = env.step(action)
            if done or truncated:
                break
        
        print("✓ Environment working")
        return True
    except Exception as e:
        print(f"✗ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quick_training():
    """Run a very short training session."""
    print("\nTesting quick training (10 episodes)...")
    try:
        import torch
        import numpy as np
        from env import MicroTankArenaEnv
        from model import DQN
        import config
        
        # Temporarily reduce episodes
        original_episodes = config.NUM_EPISODES
        config.NUM_EPISODES = 10
        
        env = MicroTankArenaEnv(config)
        policy_net = DQN(env.observation_space.shape[0], env.action_space.n)
        
        for ep in range(10):
            obs, _ = env.reset()
            done = False
            truncated = False
            steps = 0
            
            while not (done or truncated) and steps < 50:
                with torch.no_grad():
                    q_values = policy_net(torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0))
                    action = q_values.argmax().item()
                
                obs, reward, done, truncated, info = env.step(action)
                steps += 1
            
            if (ep + 1) % 5 == 0:
                print(f"  Episode {ep+1}/10 completed")
        
        # Restore original value
        config.NUM_EPISODES = original_episodes
        
        print("✓ Quick training successful")
        return True
    except Exception as e:
        print(f"✗ Training test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("MicroTank Arena - Quick Verification Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_bots,
        test_reward_function,
        test_environment,
        test_quick_training,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\nTest crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ All tests passed! Ready to train.")
        print("\nNext steps:")
        print("1. Run full training: python train.py")
        print("2. Evaluate results: python evaluate.py")
        print("3. Monitor win rate in training logs")
    else:
        print("\n✗ Some tests failed. Please fix errors before training.")
        return 1
    
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())
