from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import numpy as np
import gymnasium
from time import sleep

my_config = DEFAULT_CONFIG_DICT
my_config["interface"] = MyGranTurismoRTGYM
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
my_config["act_buf_len"] = 4
my_config["reset_act_buf"] = False
my_config["benchmark"] = True
my_config["benchmark_polyak"] = 0.2

env = gymnasium.make("real-time-gym-v1", config=my_config)
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

check_env(env)


env.reset()
obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
obs_space = env.observation_space
print(f"observation space: {obs_space}")
print("")
print(f"observation actual: {obs}")

model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=100)

obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
obs_space = env.observation_space
while not (terminated or truncated):
    obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
    env.render()