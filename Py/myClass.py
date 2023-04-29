from pygamepad import controlGamepad
from gymnasium import Env
from serverClass import server 
import gym.spaces as spaces
import cv2
import numpy as np
import logging
from collections import deque
from threading import Thread
from rewardGT import RewardFunction

class MyGranTurismoGYM(Env):
    def __init__(self):
        print("GT Real Time instantiated")
        self.server = server(debug=False)
        self.display = None
        self.gamepad = None
        self.img = None # for render
        self.raceState = None
        self.rewardFunction = None 
        self.renderingThread = Thread(target=self._renderingThread, args=(), kwargs={}, daemon=True)
        eSpeed = spaces.Box(low=0, high=10000, shape=(1,), dtype='float32')
        eBoost = spaces.Box(low=0, high=10000, shape=(1,), dtype='float32')
        eGear =  spaces.Box(low=0, high=6, shape=(1,), dtype='float32')
        vSpeed = spaces.Box(low=0, high=500, shape=(1,), dtype='float32')
        vSteer = spaces.Box(low=-580, high=580, shape=(1,), dtype='float32')
        vPosition = spaces.Box(low=-3000000, high=3000000, shape=(2,), dtype='float32')         
    
        images = spaces.Box(low=0.0, high=255.0, shape=(240, 320, 3), dtype='uint8')
        self.observation_space = spaces.Tuple((eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, images))
        self.action_space = spaces.Box(low=np.array([0.0, 0.0, -1.0]), high=np.array([1.0, 1.0, 1.0]), dtype='float64')

    
    # Mandatory method
    def reset(self, seed=None, options=None):
        self.inititalizeCommon() #only used to debug this
        self.server.reloadSave()
        trackID, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display = self.getDataImage()
        obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display]
        
        self.rewardFunction.reset()
        return obs, None
    
    # rendering from the gym env in a seperate thread    
    def _renderingThread(self):
        #from time import sleep
        while True:
            #sleep(0.1)
            self.render()
            
    def close(self):
        pass

    # Maybe needed (at least as a helper) wrong place?
    def getDataImage(self):  
        self.server.receiveOneFrame()
        eSpeed = np.array([self.server.myData.VS.engSpeed], dtype='float32')
        eBoost = np.array([self.server.myData.VS.engBoost], dtype='float32')
        eGear  = np.array([self.server.myData.VS.engGear], dtype='float32')
        vSpeed = np.array([self.server.myData.VS.speed], dtype='float32')
        vSteer = np.array([self.server.myData.VS.steer], dtype='float32')
        vDir = np.array([self.server.myData.drivingDir], dtype='float32')
        vPosition = np.array([self.server.myData.posVect.x, self.server.myData.posVect.y], dtype='float32')
        trackID = self.server.myData.trackID
        self.raceState = self.server.myData.GS.raceState     
        # raceState
        # 1: Race Start (count down)
        # 2: Racing (from post-countdown till final lap finish line)
        # 3: Race finished
        # 5: Some undefined state (like main menu, etc)
        
        display = self.server.pic     
        return trackID, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display

    def startSession(self):
        self.server.connect()
        logging.debug("Server session started")
        
    def initControl(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()
        logging.debug("Virtual Dual Shock 4 loaded")
        
    def inititalizeCommon(self):
        self.initControl()
        self.startSession()
        self.rewardFunction = RewardFunction()
        
    # Mandatory method        
    def get_observation_space(self):
        # eXXXX for engineXXXX
        # vXXX for vehicleXXX
        eSpeed = spaces.Box(low=0, high=10000, shape=(1,), dtype='float32')
        eBoost = spaces.Box(low=0, high=10000, shape=(1,), dtype='float32')
        eGear =  spaces.Box(low=0, high=6, shape=(1,), dtype='float32')
        vSpeed = spaces.Box(low=0, high=500, shape=(1,), dtype='float32')
        vSteer = spaces.Box(low=-580, high=580, shape=(1,), dtype='float32')
        vPosition = spaces.Box(low=-3000000, high=3000000, shape=(2,), dtype='float32')         
        
        images = spaces.Box(low=0, high=255, shape=(240, 320, 3), dtype=np.uint8)
        return spaces.Tuple((eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, images))
    
    # Mandatory method
    def get_action_space(self):
        #return spaces.Box(low=-1.0, high=1.0, shape=(3,))
        return spaces.Box(low=np.array([0.0, 0.0, -1.0]), high=np.array([1.0, 1.0, 1.0]), dtype='float64')
    
    # Mandatory method
    def get_default_action(self):
        return np.array([1.0, 0.0, 0.0], dtype='float64')
        
    # Mandatory method
    def step(self, control):
        self.send_control(control)
        trackID, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display = self.getDataImage()
        reward, terminated = self.rewardFunction.computeReward(trackID, vSpeed, vDir)
        obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display]
        info = {}
        if self.raceState == 3:
            terminated = True
        elif self.raceState == 1:
            terminated = False
            self.rewardFunction.reset()
        else:
            terminated = False
        return obs, reward, terminated, False, info
    
    def _get_info(self):
        return {"info": 0}
    
    def _get_obs(self):
        trackID, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display = self.getDataImage()
        obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display]
        return obs
    # Mandatory method
    def send_control(self, control):
        controlGamepad(self.gamepad, control)

    # Optional method
    def wait(self):
        self.send_control(self.get_default_action())
        
    # Optional method
    def render(self):
        cv2.imshow('Render Display', self.server.pic)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return