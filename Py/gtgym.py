import os
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import (
    SubprocVecEnv,
    VecFrameStack,
    VecMonitor,
)
from stable_baselines3.common.atari_wrappers import ClipRewardEnv
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
)
from stable_baselines3.common.evaluation import evaluate_policy
from torch import nn