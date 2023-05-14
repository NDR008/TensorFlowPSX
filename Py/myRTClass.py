from pygamepad import controlGamepad
from rtgym import RealTimeGymInterface, DEFAULT_CONFIG_DICT
from serverClass import server 
import gymnasium.spaces as spaces
import cv2
# import gymnasium
import numpy as np
import logging
from collections import deque
from threading import Thread
from rewardGT import RewardFunction

class MyGranTurismoRTGYM(RealTimeGymInterface):
    def __init__(self, debugFlag=False, img_hist_len=3, modelMode=2, agent="PPO", imageHeight=240, imageWidth=320, trackChoice=1):
        print("GT Real Time instantiated")
        self.server = server(debug=debugFlag)
        self.display = None
        self.renderImage = None
        self.gamepad = None
        self.img = None # for render
        self.modelMode = modelMode # 2 = reduced observation
        if self.modelMode == 1:
            self.img_hist_len = img_hist_len
        self.img_hist = None
        self.raceState = None
        self.rewardFunction = None 
        self.agent = agent
        self.imageSize = (imageWidth, imageHeight)
        self.colour = False
        self.trackChoice = trackChoice

        self.inititalizeCommon() # starts the TCP server and waits for the emulator to connect

    # Maybe needed (at least as a helper) wrong place?
    def getDataImage(self):  
        import cv2
        self.server.receiveOneFrame()
        eClutch = np.array([self.server.myData.VS.eClutch], dtype='float32')
        eSpeed = np.array([self.server.myData.VS.engSpeed], dtype='float32')
        eBoost = np.array([self.server.myData.VS.engBoost], dtype='float32')
        eGear  = np.array([self.server.myData.VS.engGear], dtype='float32')
        vSpeed = np.array([self.server.myData.VS.speed], dtype='float32')
        vSteer = np.array([self.server.myData.VS.steer], dtype='float32')
        vDir = np.array([self.server.myData.drivingDir], dtype='float32')
        vPosition = np.array([self.server.myData.posVect.x, self.server.myData.posVect.y], dtype='float32')
        trackID = self.server.myData.trackID
        self.raceState = self.server.myData.GS.raceState     
        rState = np.array([self.raceState], dtype='float32')
        # raceState
        # 1: Race Start (count down)
        # 2: Racing (from post-countdown till final lap finish line)
        # 3: Race finished
        # 5: Some undefined state (like main menu, etc)
        tmp = cv2.resize(self.server.pic, (self.imageSize[0], self.imageSize[1]))
        # print(tmp.shape)
        # cv2.imshow("original",tmp)
        # cv2.waitKey(0)
        
        tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        # print(tmp.shape)
        # cv2.imshow("grey",tmp)
        # cv2.waitKey(0)
        
        tmp2 = tmp.reshape(self.imageSize[1], self.imageSize[0],  1)
        # print(tmp2.shape)
        # cv2.imshow("reshaped",tmp2)
        # cv2.waitKey(0)
        
        self.renderImage = tmp2
        return trackID, rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, self.renderImage

    def startServerToRedux(self):
        self.server.connect()
        logging.debug("Server session started")
        
    def initControl(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()
        logging.debug("Virtual Dual Shock 4 loaded")
        
    def inititalizeCommon(self):
        if self.modelMode == 1:
            self.img_hist = deque(maxlen=self.img_hist_len)
        self.initControl()
        self.startServerToRedux()
        self.rewardFunction = RewardFunction()
        
    # Mandatory method        
    def get_observation_space(self):
        # eXXXX for engineXXXX
        # vXXX for vehicleXXX
        eClutch = spaces.Box(low=0, high=3, shape=(1,), dtype='float32')
        eSpeed = spaces.Box(low=0, high=10000, shape=(1,), dtype='float32')
        eBoost = spaces.Box(low=0, high=10000, shape=(1,), dtype='float32')
        eGear =  spaces.Box(low=0, high=6, shape=(1,), dtype='float32')
        vSpeed = spaces.Box(low=0, high=500, shape=(1,), dtype='float32')
        rState = spaces.Box(low=0, high=5, shape=(1,), dtype='float32')
        # data = (eSpeed, eBoost, eGear, vSpeed, vSteer)
        # rState = spaces.Box(low=0, high=1, shape=(1,))
        # fLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # fRighttSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rLeftSlip = spaces.Box(low=0, high=256, shape=(1,))
        # rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
        vDir = spaces.Box(low=0, high=3, shape=(1,), dtype='float32')
        
        if self.modelMode == 1:
            vSteer = spaces.Box(low=-1024, high=1024, shape=(1,), dtype='float32')
            vPosition = spaces.Box(low=-3000000, high=3000000, shape=(2,), dtype='float32')         
            images = spaces.Box(low=0.0, high=255.0, shape=(self.img_hist_len, self.imageSize[1], self.imageSize[0],1), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, images))
        
        if self.modelMode == 3:
            vSteer = spaces.Box(low=-1024, high=1024, shape=(1,), dtype='float32')
            vPosition = spaces.Box(low=-3000000, high=3000000, shape=(2,), dtype='float32')         
            images = spaces.Box(low=0.0, high=255.0, shape=(self.imageSize[1], self.imageSize[0],1), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, images))
        
        elif self.modelMode == 2:
            return spaces.Tuple((rState, eClutch, eSpeed, eGear, vSpeed, vDir))
        

    # Mandatory method
    def get_action_space(self):
        #return spaces.Box(low=-1.0, high=1.0, shape=(3,))
        if self.agent == "SAC" or "A3C":
            return spaces.Box(low=np.array([0.0, 0.0, -1.0]), high=np.array([1.0, 1.0, 1.0]), dtype='float64')
        else:
            return spaces.MultiDiscrete([ 2, 2, 3 ])
    
    # Mandatory method
    def get_default_action(self):
        if self.agent == "SAC" or "A3C":
            return np.array([.0, 0.0, 0.0], dtype='float64')
        else:
            return np.array([0, 0, 0])
    
    # Mandatory method
    def reset(self, seed=None, options=None):
        print("reset triggered")
        self.server.reloadSave(self.trackChoice+1) # loads the save state
        trackID, rstate, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display = self.getDataImage()
       
        if self.modelMode == 1:
            for _ in range(self.img_hist_len):
                self.img_hist.append(display)
            imgs = np.array(list(self.img_hist), dtype='uint8')
            obs = [rstate, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, imgs]

        if self.modelMode == 3:
            obs = [rstate, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display]
        
        elif self.modelMode == 2:    
            obs = [rstate, eClutch, eSpeed, eGear, vSpeed, vDir]
        # obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display]
        self.rewardFunction.reset() # reward_function not implemented yet
        return obs, {}
        
    # Mandatory method
    def get_obs_rew_terminated_info(self):
        trackID, rstate, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display = self.getDataImage()
        reward, terminated = self.rewardFunction.computeReward(self.modelMode, trackID, vSpeed, vDir)
        
        if self.modelMode == 1:
            self.img_hist.append(display)
            imgs = np.array(list(self.img_hist), dtype='uint8') # we need numpy array float32 avoids warning
            obs = [rstate, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, imgs]

        if self.modelMode == 3:
            obs = [rstate, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, display]
            
        elif self.modelMode == 2:    
            obs = [rstate, eClutch, eSpeed, eGear, vSpeed, vDir]            
            
        info = {}
        if self.raceState == 3:
            terminated = True
        elif self.raceState == 1:
            terminated = False
        else:
            terminated = False
        return obs, reward, terminated, info
    
    # Mandatory method
    def send_control(self, control):
        controlGamepad(self.gamepad, control, self.agent)

    # Optional method
    def wait(self):
        self.send_control(self.get_default_action())
        # self.server.reloadSave()
        
    # Optional method
    def render(self):
        #cv2.imshow('Render Display', self.server.pic)
        cv2.imshow('Render Display', self.renderImage)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return