from pygamepad import controlGamepad
from rtgym import RealTimeGymInterface, DEFAULT_CONFIG_DICT
from serverClass import server 
import gymnasium.spaces as spaces
import gymnasium
import numpy as np
import logging
from collections import deque

from gymnasium.experimental.wrappers import FrameStackObservationV0

class MyGranTurismoRTGYM(RealTimeGymInterface):
    def __init__(self, debugFlag=False, img_hist_len=3):
        print("GT Real Time instantiated")
        self.server = server(debug=debugFlag)
        self.display = None
        self.gamepad = None
        self.img = None # for render
        self.img_hist_len = img_hist_len
        self.img_hist = deque(maxlen=img_hist_len)
        self.raceState = None

    # Maybe needed (at least as a helper) wrong place?
    def getDataImage(self):  
        self.server.receiveOneFrame()
        eSpeed = np.array(self.server.myData.VS.engSpeed, dtype='int32')
        eBoost = np.array(self.server.myData.VS.engBoost, dtype='int32')
        eBoost = np.array(self.server.myData.VS.engBoost, dtype='int32')
        eBoost = np.array(self.server.myData.VS.engBoost, dtype='int32')
        eBoost = np.array(self.server.myData.VS.engBoost, dtype='int32')
        eGear  = np.array(self.server.myData.VS.engGear, dtype='int32')
        vSpeed = np.array(self.server.myData.VS.speed, dtype='int32')
        vSteer = np.array(self.server.myData.VS.steer, dtype='int32')
        self.raceState = self.server.myData.GS.raceState 
        # raceState
        # 1: Race Start (count down)
        # 2: Racing (from post-countdown till final lap finish line)
        # 3: Race finished
        # 5: Some undefined state (like main menu, etc)
        
        # eSpeed = self.server.myData.VS.engSpeed
        # eBoost = self.server.myData.VS.engBoost
        # eBoost = self.server.myData.VS.engBoost
        # eBoost = self.server.myData.VS.engBoost
        # eBoost = self.server.myData.VS.engBoost
        # eGear  = self.server.myData.VS.engGear
        # vSpeed = self.server.myData.VS.speed
        # vSteer = self.server.myData.VS.steer
        # 
        vPosition = np.array((self.server.myData.posVect.x, self.server.myData.posVect.y), dtype='int32')
        display = self.server.pic     
        return eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display

    def startSession(self):
        self.server.connect()
        logging.debug("Server session started")
        
    def initControl(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()
        logging.debug("Virtual Dual Shock 4 loaded")
        
    def inititalizeCommon(self):
        self.img_hist = deque(maxlen=self.img_hist_len)
        self.initControl()
        self.startSession()
        
    # Mandatory method        
    def get_observation_space(self):
        # eXXXX for engineXXXX
        # vXXX for vehicleXXX
        eSpeed = spaces.Box(low=0, high=10000, shape=(1,), dtype='int32')
        eBoost = spaces.Box(low=0, high=10000, shape=(1,), dtype='int32')
        eGear =  spaces.Box(low=0, high=6, shape=(1,), dtype='int32')
        vSpeed = spaces.Box(low=0, high=500, shape=(1,), dtype='int32')
        vSteer = spaces.Box(low=-580, high=580, shape=(1,), dtype='int32')
        vPosition = spaces.Box(low=-3000000, high=3000000, shape=(2,), dtype='int32')         
        # data = (eSpeed, eBoost, eGear, vSpeed, vSteer)
        # rState = spaces.Box(low=0, high=1, shape=(1,))
        # fLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # fRighttSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
        #display = spaces.Box(low=0.0, high=255.0, shape=(self.img_hist_len, 240, 320, 3))
        display = spaces.Box(low=0, high=255, shape=(240, 320, 3), dtype=np.uint8)
        return spaces.Tuple((eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display))
    
    # Mandatory method
    def get_action_space(self):
        return spaces.Box(low=0.0, high=1.0, shape=(3,))
    
    # Mandatory method
    def get_default_action(self):
        return np.array([1,0,0], dtype='int32')
    
    # Mandatory method
    def reset(self, seed=None, options=None):
        self.inititalizeCommon() #only used to debug this
        eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display = self.getDataImage()
        # I think this method should return an initial observation
        # since it is a reset state, the display history is the current display repeated
        for _ in range(self.img_hist_len):
            self.img_hist.append(display)
        # may revisit to use tensors instead
        imgs = np.array(list(self.img_hist), dtype='uint8')
        obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, imgs]
        #obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display]
        # self.reward_function.reset() # reward_function not implemented yet
        return obs, {}
        
    # Mandatory method
    def get_obs_rew_terminated_info(self):
        eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display = self.getDataImage()
        self.img_hist.append(display)
        # may revisit to use tensors instead
        imgs = np.array(list(self.img_hist), dtype='uint8') # we need numpy array
        obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, imgs]
        rew = 0 # for now
        info = {}
        if self.raceState == 3:
            terminated = True
        else:
            terminated = False
        return obs, rew, terminated, info
    
    # Mandatory method
    def send_control(self, control):
        controlGamepad(self.gamepad, control)

    # Optional method
    def wait(self):
        self.send_control(self.get_default_action())
        # self.server.reloadSave()
        
    # Optional method
    def render(self):
        pass    
    
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
wrapped_env = FrameStackObservationV0(env,4)
obs, _ = env.reset()
#print(obs)
print("boo")