from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import numpy as np
from time import sleep
from tmrl.util import partial
from tmrl.envs import GenericGymEnv

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

env_cls=partial(GenericGymEnv, id="real-time-gym-v1", gym_kwargs={"config": my_config})
env = env_cls()