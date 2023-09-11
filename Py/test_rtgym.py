from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import numpy as np
import gymnasium
from time import sleep

my_config = DEFAULT_CONFIG_DICT
my_config["interface"] = MyGranTurismoRTGYM
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
my_config["ep_max_length"] = 2000
my_config["act_buf_len"] = 4
my_config["reset_act_buf"] = False
my_config["benchmark"] = True
my_config["benchmark_polyak"] = 0.2

my_config["interface_kwargs"] = {
  'debugFlag': False, # do not use render() while True
  'img_hist_len': 3,
  'modelMode': 4,
  'agent' : 'PPO',
  #  [42, 42, K], [84, 84, K], [10, 10, K], [240, 320, K] and  [480, 640, K]
  'imageWidth' : 42, # there is a default Cov layer for PPO with 240 x 320
  'imageHeight' : 42,
  'trackChoice' : 2, # 1 is High Speed Ring, 2 is 0-400m, 
}

env = gymnasium.make("real-time-gym-v1", config=my_config)
# https://gymnasium.farama.org/api/experimental/wrappers/#gymnasium.experimental.wrappers.FrameStackObservationV0
# wrapped_env = FrameStackObservationV0(env,4)
#obs, _ = env.reset()

obs, info = env.reset()
obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
obs_space = env.observation_space
print(f"observation space: {obs_space}")
print("")
print(f"observation actual: {obs}")
while not (terminated or truncated):
    #env.render()
    #act = model(obs)
    act = env.action_space.sample()
    #print(act)
    obs, rew, terminated, truncated, info = env.step(act)
    #sleep(0.1)
    env.render()
    #print(f"rew:{rew}")
    #break
    

# granTurismo = MyGranTurismoRTGYM(debugFlag=True)
# granTurismo.inititalizeCommon()
# print(granTurismo.get_observation_space())
# granTurismo.reset()
# granTurismo.wait()
# granTurismo.server.receiveAllAlways()