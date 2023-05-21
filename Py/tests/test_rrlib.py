# to read later: https://raw.githubusercontent.com/ray-project/ray/master/rllib/examples/unity3d_env_local.py

from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import gymnasium
import ray
from ray.rllib.algorithms import ppo
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.sac import SACConfig
import json
import numpy as np

my_config = DEFAULT_CONFIG_DICT
my_config["interface"] = MyGranTurismoRTGYM
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
my_config["ep_max_length"] = 1024
my_config["act_buf_len"] = 3
my_config["reset_act_buf"] = False
my_config["benchmark"] = True
my_config["benchmark_polyak"] = 0.2

ppoconfig = ppo.DEFAULT_CONFIG.copy()              # PPO's default configuration. See the next code cell.
ppoconfig["log_level"] = "WARN"                    # Suppress too many messages, but try "INFO" to see what can be printed.
ppoconfig["num_workers"] = 1                       # Use > 1 for using more CPU cores, including over a cluster
ppoconfig["num_sgd_iter"] = 4                      # Number of SGD (stochastic gradient descent) iterations per training minibatch.
ppoconfig["sgd_minibatch_size"] = 4              # The amount of data records per minibatch
ppoconfig["model"]["fcnet_hiddens"] = [10, 10]    #
ppoconfig["num_cpus_per_worker"] = 0 
ppoconfig["framework"] = "torch"
ppoconfig["disable_env_checking"] = True

def env_creator(env_config):
  env = gymnasium.make("real-time-gym-v1", config=my_config)
  return env  # return an env instance

from ray.tune.registry import register_env
register_env("gt-rtgym-env-v1", env_creator)

ray.init()

#agent = ppo.PPO(env="gt-rtgym-env-v1", config=ppoconfig)

algo = (
    PPOConfig()
    #SACConfig()
    .resources(
        num_gpus=1
        )
    .rollouts(
        num_rollout_workers=1,
        #batch_mode="truncate_episodes",
        #rollout_fragment_length=128
        )
    .framework("torch")
    .environment(
        env="gt-rtgym-env-v1",
        disable_env_checking=False,
        render_env=True,
        )
    .training(
            #lr=0.0003,
            #lambda_=0.95,
            #gamma=0.99,
            #sgd_minibatch_size=512,
            train_batch_size=512,
            #num_sgd_iter=8,
            #clip_param=0.2,
            model={"fcnet_hiddens": [128, 128]},
        )
    .build()
)

N = 50
results = []
episode_data = []
episode_json = []


for n in range(N):
    result = algo.train()
    results.append(result)
  
    episode = {
        "n": n,
        "episode_reward_mean": result["episode_reward_mean"], 
        "episode_reward_max":  result["episode_reward_max"],  
        "episode_len_mean":    result["episode_len_mean"],
    }

    episode_data.append(episode)
    episode_json.append(json.dumps(episode))
    
    print(f'Max reward: {episode["episode_reward_max"]}')
    
path_to_checkpoint = algo.save()
print(
    "An Algorithm checkpoint has been created inside directory: "
    f"'{path_to_checkpoint}'."
)

ray.shutdown()