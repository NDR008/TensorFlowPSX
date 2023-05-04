from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import gymnasium
import ray
from ray.rllib.algorithms import ppo

my_config = DEFAULT_CONFIG_DICT
my_config["interface"] = MyGranTurismoRTGYM
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
#my_config["ep_max_length"] = 100
my_config["act_buf_len"] = 4
my_config["reset_act_buf"] = False
my_config["benchmark"] = True
my_config["benchmark_polyak"] = 0.2

ppoconfig = ppo.DEFAULT_CONFIG.copy()              # PPO's default configuration. See the next code cell.
ppoconfig["log_level"] = "INFO"                    # Suppress too many messages, but try "INFO" to see what can be printed.
ppoconfig["num_workers"] = 1                       # Use > 1 for using more CPU cores, including over a cluster
ppoconfig["num_sgd_iter"] = 1                      # Number of SGD (stochastic gradient descent) iterations per training minibatch.
                                                # I.e., for each minibatch of data, do this many passes over it to train. 
ppoconfig["sgd_minibatch_size"] = 128              # The amount of data records per minibatch
ppoconfig["model"]["fcnet_hiddens"] = [50, 50]    #
ppoconfig["num_cpus_per_worker"] = 0 

#env = gymnasium.make("real-time-gym-v1", config=my_config)
def env_creator(env_config):
  env = gymnasium.make("real-time-gym-v1", config=my_config)()
  return env  # return an env instance

from ray.tune.registry import register_env
register_env("gt-rtgym-env-v1", env_creator)

ppoconfig["env"] = "gt-rtgym-env-v1"

ray.init()
algo = ppo.PPO(config=ppoconfig)



# obs, info = env.reset()
# terminated = False
# truncated = False
# obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
# obs_space = env.observation_space
# while not (terminated or truncated):
#     obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
#     env.render()
#     print(f"rew:{rew}")