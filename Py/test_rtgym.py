from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import numpy as np
import gymnasium
import pprint
from time import sleep
mode = 1

my_config = DEFAULT_CONFIG_DICT
my_config["interface"] = MyGranTurismoRTGYM
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
#my_config["ep_max_length"] = 2000
my_config["act_buf_len"] = 4
my_config["reset_act_buf"] = False
my_config["benchmark"] = False
my_config["benchmark_polyak"] = 0.2

my_config["interface_kwargs"] = {
'debugFlag': False, # do not use render() while True
'discreteAccel' : True,
'accelAndBrake' : False,
'discSteer' : True,
'contAccelOnly' : False,
'discAccelOnly' : False,
'modelMode': mode,
'agent' : 'PPO',
#  [42, 42, K], [84, 84, K], [10, 10, K], [240, 320, K] and  [480, 640, K]
'imageWidth' : 42, # there is a default Cov layer for PPO with 240 x 320
'imageHeight' : 42,
'trackChoice' : 1, # 1 is High Speed Ring, 2 is 0-400m, 
}

env = gymnasium.make("real-time-gym-v1", config=my_config)
pp = pprint.PrettyPrinter(indent=4)
obs, info = env.reset()
obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
obs_space = env.observation_space
act_space = env.action_space
obs, info = env.reset()
print("observation space:")
for i in obs_space:
    print(i)
print("observation:")
for i in obs:
    print("value:", i, "with shape:", i.shape, i.dtype)
#for i in range(0,3):
while True:
    act = env.action_space.sample()
    obs, rew, terminated, truncated, info = env.step(act)
    env.render()
    

# granTurismo = MyGranTurismoRTGYM(debugFlag=True)
# granTurismo.inititalizeCommon()
# print(granTurismo.get_observation_space())
# granTurismo.reset()
# granTurismo.wait()
# granTurismo.server.receiveAllAlways()