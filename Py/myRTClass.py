from pygamepad import controlGamepad
from rtgym import RealTimeGymInterface
from serverClass import server 
import gymnasium.spaces as spaces
import numpy as np

class MyGranTurismoRTGYM(RealTimeGymInterface):
    def __init__(self,debugFlag=False,histSize=4):
        print("GT Real Time instantiated")
        self.server = server(debug=debugFlag)
        self.display = None
        self.gamepad = None
        self.histSize = histSize

    def startSession(self):
        self.server.connect()
        
    def init_control(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()

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
        view = spaces.Box(low=0.0, high=255.0, shape=(self.histSize, 240, 320, 3))        
        return spaces.Tuple((vSpeed,vSteer,view))
    
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

    def wait(self):
        self.send_control(self.get_default_action())
        # self.server.reloadSave()