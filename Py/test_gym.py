from myClass import MyGranTurismoGYM
import numpy as np
from time import sleep
from stable_baselines3.common.env_checker import check_env


env = MyGranTurismoGYM()
# https://gymnasium.farama.org/api/experimental/wrappers/#gymnasium.experimental.wrappers.FrameStackObservationV0
# wrapped_env = FrameStackObservationV0(env,4)
#obs, _ = env.reset()
check_env(env)

obs, info = env.reset()
terminated = False
obs_space = env.observation_space

print(f"observation space: {obs_space}")
print("")
print(f"observation actual: {obs}")
while not (terminated):
    obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
    env.render()
    break