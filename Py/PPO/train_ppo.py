# to read later: https://raw.githubusercontent.com/ray-project/ray/master/rllib/examples/unity3d_env_local.py
from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import gymnasium
import ray
from ray import tune, air
from ray.rllib.algorithms import ppo
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.sac import SACConfig
from ray.rllib.algorithms.a3c import A3CConfig
import json
import numpy as np
from time import sleep
ray.shutdown()

my_config = DEFAULT_CONFIG_DICT
my_config["interface"] = MyGranTurismoRTGYM
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
my_config["ep_max_length"] = 512
my_config["act_buf_len"] = 3
my_config["reset_act_buf"] = False
my_config["benchmark"] = True
my_config["benchmark_polyak"] = 0.2

def env_creator(env_config):
  env = gymnasium.make("real-time-gym-v1", config=my_config)
  return env  # return an env instance

from ray.tune.registry import register_env
register_env("gt-rtgym-env-v1", env_creator)
ray.init()

algo = (
    #PPOConfig()
    #SACConfig()
    PPOConfig()
    .resources(
        #num_gpus=1
        )
    .rollouts(
        num_rollout_workers=1,
        # batch_mode="truncate_episodes",
        # rollout_fragment_length=128,
        )
    .framework("torch")
    .environment(
        env="gt-rtgym-env-v1",
        disable_env_checking=True,
        render_env=False,
        )
    .training(
            #lr=tune.grid_search([0.01, 0.001, 0.0001])
            #lambda_=0.95,
            #gamma=0.99,
            #sgd_minibatch_size=128,
            #train_batch_size=1024,
            #num_sgd_iter=8,
            #clip_param=0.2,
            #model={"fcnet_hiddens": [12, 12]},
        )
    .build()
)

N = 2000

for n in range(N):
    result = algo.train()
    if n % 10 == 0:
        print("Saved", n)
        algo.save()
path_to_checkpoint = algo.save()
print(
    "An Algorithm checkpoint has been created inside directory: "
    f"'{path_to_checkpoint}'."
)

ray.shutdown()