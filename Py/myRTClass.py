from pygamepad import controlGamepad
from rtgym import RealTimeGymInterface, DEFAULT_CONFIG_DICT
from serverClass import server 
import gymnasium.spaces as spaces
import gymnasium
import numpy as np
import logging

class MyGranTurismoRTGYM(RealTimeGymInterface):
    def __init__(self, debugFlag=False, img_hist_len=3):
        print("GT Real Time instantiated")
        self.server = server(debug=debugFlag)
        self.display = None
        self.gamepad = None
        self.img = None # for render
        self.img_hist_len = img_hist_len
        self.img_hist = None        

    # Maybe needed (at least as a helper) wrong place?
    def getDataImage(self):  
        self.server.receiveOneFrame()
        eSpeed = self.server.myData.VS.engSpeed
        eBoost = self.server.myData.VS.engBoost
        eBoost = self.server.myData.VS.engBoost
        eBoost = self.server.myData.VS.engBoost
        eBoost = self.server.myData.VS.engBoost
        eGear = self.server.myData.VS.engGear
        vSpeed = self.server.myData.VS.speed
        vSteer = self.server.myData.VS.steer
        vPosition = (self.server.myData.posVect.x, self.server.myData.posVect.y) 
        display = self.server.pic     
        return eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display

    def startSession(self):
        self.server.connect()
        logging.debug("Server session started")
        
    def init_control(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()
        logging.debug("Virtual Dual Shock 4 loaded")
        
    def inititalizeCommon(self):
        self.init_control()
        self.startSession()
        
    # Mandatory method        
    def get_observation_space(self):
        # eXXXX for engineXXXX
        # vXXX for vehicleXXX
        eSpeed = spaces.Box(low=0, high=10000, shape=(1,))
        eBoost = spaces.Box(low=0, high=10000, shape=(1,))
        eGear = spaces.Box(low=0, high=6, shape=(1,))
        vSpeed = spaces.Box(low=0, high=500, shape=(1,))
        vSteer = spaces.Box(low=-580, high=580, shape=(1,))
        vPosition = spaces.Box(low=-3000000, high=3000000, shape=(2,))         
        # data = (eSpeed, eBoost, eGear, vSpeed, vSteer)
        # rState = spaces.Box(low=0, high=1, shape=(1,))
        # fLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # fRighttSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
        display = spaces.Box(low=0.0, high=255.0, shape=(self.img_hist_len, 240, 320, 3))
        return spaces.Tuple((eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display))
    
    # Mandatory method
    def get_action_space(self):
        return np.array([0,0,0], dtype='float32')
    
    # Mandatory method
    def get_default_action(self):
        return np.array([1,0,0], dtype='float32')
    
    # Mandatory method
    def reset(self, seed=None, options=None):
        eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display = self.getDataImage()
        # I think this method should return an initial observation
        # since it is a reset state, the display history is the current display repeated
        for _ in range(self.img_hist_len):
            self.img_hist.append(display)
        imgs = np.array(list(self.img_hist))
        obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, imgs]
        self.reward_function.reset()
        return obs, {}
        
    # Mandatory method
    def get_obs_rew_terminated_info(self):
        return super().get_obs_rew_terminated_info()
    
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