from myRTClass import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
import numpy as np

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

#env = gymnasium.make("real-time-gym-v1", config=my_config)
# https://gymnasium.farama.org/api/experimental/wrappers/#gymnasium.experimental.wrappers.FrameStackObservationV0
#wrapped_env = FrameStackObservationV0(env,4)
#obs, _ = env.reset()

granTurismo = MyGranTurismoRTGYM(debugFlag=True)
granTurismo.inititalizeCommon()
print(granTurismo.get_observation_space())
granTurismo.reset()
granTurismo.wait()
granTurismo.server.receiveAllAlways()