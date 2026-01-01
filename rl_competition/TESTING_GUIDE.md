# Testing & Verification Guide

## Quick Test
Before running full training, verify everything works:

```bash
python test_setup.py
```

This will test:
- ✓ All module imports
- ✓ Bot behaviors
- ✓ Reward function
- ✓ Environment mechanics
- ✓ Quick 10-episode training loop

## Full Training Workflow

### 1. Train the agent (headless, faster)
```bash
# Make sure rendering is OFF in config.py
# USE_PYGAME_RENDER = False

python train.py
```

**Expected output:**
- Episodes progress from 1 to 10,000
- Win rate should increase over time
- Every 50 episodes you'll see stats like:
  ```
  Episode 1000/10000 | Avg reward (last 50): 15.32 | Win rate (last 50): 65.0% | Epsilon: 0.80
  ```

**Good signs:**
- Win rate > 60% by episode 5000
- Win rate > 70% by episode 8000
- Rewards trending upward

**Warning signs:**
- Win rate stuck below 40% after 3000 episodes → May need to adjust rewards
- Win rate dropping after initial increase → Learning rate may be too high

### 2. Evaluate the trained agent
```bash
python evaluate.py
```

**Target metrics:**
- Win Rate: > 70%
- Avg HP Diff: > 20
- Avg Steps: < 60 (faster is better)

### 3. Optional: Watch with visualization
```bash
# Set in config.py:
# USE_PYGAME_RENDER = True

python evaluate.py
```

## Performance Benchmarks

### Episode Milestones
- **Episode 1000:** Win rate should be > 40%
- **Episode 3000:** Win rate should be > 55%
- **Episode 5000:** Win rate should be > 65%
- **Episode 8000:** Win rate should be > 70%

### Final Evaluation Targets
- **Win Rate:** 70-80% (priority #1)
- **HP Difference:** +20 to +40 (priority #2)
- **Speed:** 40-60 steps (priority #3)

## Troubleshooting

### Low Win Rate (<50%)
- Increase NUM_EPISODES to 15000
- Check reward balance in rewards.py
- Verify bots are not too strong

### High Loss Rate
- Reduce LEARNING_RATE to 1e-4
- Increase MIN_BUFFER_SIZE to 10000
- Add more exploration (increase EPS_DECAY_STEPS)

### Slow Training
- Use smaller HIDDEN_SIZES like [64, 64]
- Reduce BUFFER_SIZE to 50000
- Disable pygame rendering

## Git Commit Messages

### For these changes:
```bash
git add config.py rewards.py model.py bots.py maps.py
git commit -m "Improve agent: balanced rewards, tactical bot, larger network, diverse maps"
```

### Alternative commit messages:
- Short: `"Enhanced training: better rewards, smarter bots, more maps"`
- Detailed: `"Optimize RL agent: rebalanced reward shaping, added TacticalBot, increased network capacity to 128x128, expanded map pool for robust training"`

### When to commit:
1. **After initial testing:** `"Verify setup: all tests passing"`
2. **After parameter tuning:** `"Tune hyperparameters: 10k episodes, lower LR, longer exploration"`
3. **After full training:** `"Complete training run: 75% win rate achieved"`
4. **Before submission:** `"Final model: ready for competition"`

## Training Tips

1. **Start small:** Test with 100 episodes first
2. **Monitor logs:** Watch for win rate trends
3. **Iterate:** If stuck, tweak rewards or add more diverse bots
4. **Be patient:** 10k episodes can take 1-2 hours depending on hardware
5. **Save often:** The trainer auto-saves, but commit after good runs

## What Changed

### config.py
- Increased training to 10,000 episodes
- Larger buffer (80k) for better experience diversity
- Slower learning rate (2e-4) for stability
- Longer exploration (5000 steps)

### rewards.py
- Balanced terminal rewards (±100)
- Added tactical positioning bonuses
- Smart shield usage rewards
- HP difference shaping
- Ammo management penalties

### model.py
- Increased network to [128, 128] for better learning capacity

### bots.py
- Added TacticalBot: combines aggression with HP-based retreats
- 5 diverse bots total for robust training

### maps.py
- Added corridors map for tight spaces
- Added scattered obstacles map
- 6 diverse maps total

## Success Criteria

Your agent is ready to submit when:
- [ ] Win rate > 70% on evaluate.py
- [ ] Wins against all bot types
- [ ] Performs well on all map types
- [ ] No negative average rewards
- [ ] Stable performance across seeds
