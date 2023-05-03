from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import ray
from ray.rllib.agents.ppo import DEFAULT_CONFIG
import ray
import ray.rllib.agents.ppo as ppo
import ray.rllib.algorithms as algs
import numpy as np
import gymnasium
from time import sleep
import pandas as pd
import json
import os
import shutil
import sys

# I am not sure if all of this makes any sense anymore?
# these are things that are required by rtgym...
my_config = DEFAULT_CONFIG_DICT
my_config["interface"] = MyGranTurismoRTGYM
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
my_config["ep_max_length"] = 100
my_config["act_buf_len"] = 4
my_config["reset_act_buf"] = False
my_config["benchmark"] = True
my_config["benchmark_polyak"] = 0.2
from tmrl.util import partial
from tmrl.envs import GenericGymEnv

def env_creater(env_config):
    env_cls=partial(GenericGymEnv, id="real-time-gym-v1", gym_kwargs={"config": env_config})
    dummy_env = env_cls()
    return dummy_env

from ray.tune.registry import register_env
register_env("my_env", env_creater)

info = ray.init(ignore_reinit_error=True)
print("Dashboard URL: http://{}".format(info["webui_url"]))


N_ITER = 10                                     # Number of training runs.
config = ppo.DEFAULT_CONFIG.copy()              # PPO's default configuration. See the next code cell.
config["log_level"] = "INFO"                    # Suppress too many messages, but try "INFO" to see what can be printed.
config["num_workers"] = 1                       # Use > 1 for using more CPU cores, including over a cluster
config["num_sgd_iter"] = 1                      # Number of SGD (stochastic gradient descent) iterations per training minibatch.
                                                # I.e., for each minibatch of data, do this many passes over it to train. 
config["sgd_minibatch_size"] = 128              # The amount of data records per minibatch
config["model"]["fcnet_hiddens"] = [50, 50]    #
config["num_cpus_per_worker"] = 0 

ppo.PPOConfig(config)

# here I have 3 issues:
# 1: Which config to pass? th env needs its config, and the algorithm needs its config.
# 2: MyGranTurismoRTGYM is MyGranTurismoRTGYM(RealTimeGymInterface) which is not 
# BaseEnv, gymnasium.Env, gym.Env, MultiAgentEnv, VectorEnv, RemoteBaseEnv, ExternalMultiAgentEnv, ExternalEnv...

agent = algs.Algorithm(config, env="my_env") 

checkpoint_root = "tmp/ppo/cart"
# Where checkpoints are written:
shutil.rmtree(checkpoint_root, ignore_errors=True, onerror=None)

# Where some data will be written and used by Tensorboard below:
ray_results = f'{os.getenv("HOME")}/ray_results/'
shutil.rmtree(ray_results, ignore_errors=True, onerror=None)

results = []
episode_data = []
episode_json = []

for n in range(N_ITER):
    result = agent.train()
    results.append(result)
    
    episode = {
        "n": n,
        "episode_reward_min": result["episode_reward_min"],
        "episode_reward_mean": result["episode_reward_mean"], 
        "episode_reward_max": result["episode_reward_max"],  
        "episode_len_mean": result["episode_len_mean"],
    }
    
    episode_data.append(episode)
    episode_json.append(json.dumps(episode))
    file_name = agent.save(checkpoint_root)
    
    print(f'{n:3d}: Min/Mean/Max reward: {result["episode_reward_min"]:8.4f}/{result["episode_reward_mean"]:8.4f}/{result["episode_reward_max"]:8.4f}. Checkpoint saved to {file_name}')