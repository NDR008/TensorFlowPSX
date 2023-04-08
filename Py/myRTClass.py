from pygamepad import controlGamepad
from rtgym import RealTimeGymInterface
from serverClass import server 
import gymnasium.spaces as spaces
import numpy as np
import logging

class MyGranTurismoRTGYM(RealTimeGymInterface):
    def __init__(self, debugFlag=False, displayHist=3):
        print("GT Real Time instantiated")
        self.server = server(debug=debugFlag)
        self.display = None
        self.gamepad = None
        self.histSize = displayHist

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
        
    def getDataImage(self):
        self.server.receiveOneFrame
        # Maybe better not to copy but....
        # myVS = self.server.myData.VS
        # myGS = self.server.myData.GS
        # posVect = self.server.myData.posVect       
        return (self.server.myData.VS, self.server.myData.GS, self.server.myData.posVect, self.server.pic)
    

    # Mandatory method        
    def get_observation_space(self):
        # eSpeed = spaces.Box(low=0, high=10000, shape=(1,))
        # eBoost = spaces.Box(low=0, high=10000, shape=(1,))
        # eGear = spaces.Box(low=0, high=6, shape=(1,))
        vSpeed = spaces.Box(low=0, high=500, shape=(1,))
        vSteer = spaces.Box(low=-580, high=580, shape=(1,))
        # rState = spaces.Box(low=0, high=1, shape=(1,))
        # fLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # fRighttSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
        display = spaces.Box(low=0.0, high=255.0, shape=(self.histSize, 240, 320, 3))
        position = spaces.Box(low=-3000000, high=3000000, shape=(2,))        
        return spaces.Tuple((position, vSpeed, vSteer, display))
    
    # Mandatory method
    def get_action_space(self):
        return np.array([0,0,0], dtype='float32')
    
    # Mandatory method
    def get_default_action(self):
        return np.array([1,0,0], dtype='float32')
    
    # Mandatory method
    def reset(self, seed=None, options=None):
        self.server.reloadSave()
    
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