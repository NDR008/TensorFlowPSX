from myClass import MyGranTurismoGYM
import numpy as np
from time import sleep
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from gymnasium.experimental.wrappers import FrameStackObservationV0
import gymnasium as gym

env = MyGranTurismoGYM()
# https://gymnasium.farama.org/api/experimental/wrappers/#gymnasium.experimental.wrappers.FrameStackObservationV0
wrapped_env = FrameStackObservationV0(env,4)
model = PPO("MlpPolicy", wrapped_env, verbose=1)
model.learn(total_timesteps=25000)
model.save("test")

del model # remove to demonstrate saving and loading

model = PPO.load("test")

obs, info = env.reset()
#check_env(env)
terminated = False
obs_space = env.observation_space

while not (terminated):
    obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
    env.render()