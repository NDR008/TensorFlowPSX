from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import numpy as np
import gymnasium
from time import sleep

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

env = gymnasium.make("real-time-gym-v1", config=my_config)
# https://gymnasium.farama.org/api/experimental/wrappers/#gymnasium.experimental.wrappers.FrameStackObservationV0
# wrapped_env = FrameStackObservationV0(env,4)
#obs, _ = env.reset()

obs, info = env.reset()
terminated = False
obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
obs_space = env.observation_space
print(f"observation space: {obs_space}")
print("")
print(f"observation actual: {obs}")
while not (terminated):
    #env.render()
    #act = model(obs)
    obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
    #sleep(0.1)
    env.render()
    print(f"rew:{rew}")
    #break
    

# granTurismo = MyGranTurismoRTGYM(debugFlag=True)
# granTurismo.inititalizeCommon()
# print(granTurismo.get_observation_space())
# granTurismo.reset()
# granTurismo.wait()
# granTurismo.server.receiveAllAlways()