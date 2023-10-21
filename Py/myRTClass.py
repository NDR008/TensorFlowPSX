"""
For CNN
Environment class for a Real Time Gymnasium Environment for Gran Turismo
Written by NDR008
nadir.syedsammut@gmail.com
Development started in December 2022

Notes to self: RLLIB cannot use Boxes for actions, need MultiDiscrete:
(RolloutWorker pid=18956) ValueError: Box(..., `int`) action spaces are not supported. Use MultiDiscrete  or Box(..., `float`).
"""

#scaled


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
    def __init__(self, debugFlag=False, discreteAccel=True, accelAndBrake=False, discSteer=True, contAccelOnly=False, discAccelOnly=False, modelMode=1, imageHeight=240, imageWidth=320, trackChoice=1, carChoice=1, rewardMode="complex"):
        """MyGranTurismoRTGYM returns an environment that contains a gym environment and a server session to receive data from PCSX Redux.
        Args:
            debugFlag (bool, optional): Makes the server do image rendinering (and not use the env.render()). Defaults to False.
            discreteAccel (bool, optional): Determines if the accelerator is discrete, otherwise continuous. Defaults to True.
            accelAndBrake (bool, optional): Determines if the accelerator can be pressed while braking (only for discrete). Defaults to False.
            discSteer (bool, optional): Determines if the steering is discrete, otherwise continuous. Defaults to True.
            contAccelOnly (bool, optional): Detrmines if ONLY accelerator exists in the control space as a continuous space (overwites other parameters). Defaults to False.
            discAccelOnly (bool, optional): Detrmines if ONLY accelerator exists in the control space as a discrete space (overwites other parameters). Defaults to False.
            modelMode (int, optional): Models 1 to 9 use single images, Mode 10 to 14 use parameters only. Defaults to 2.
            Note, discrete is not true discrete. The action space is still a Box, but the results are clipped e.g. >= 0.5 is On, <0.5 is off. This is to deal with algo limitations.
            imageHeight (int, optional): Display resize. Defaults to 240.
            imageWidth (int, optional): Display resize. Defaults to 320.
            trackChoice (int, optional): To be fixed. Defaults to 1.
        """
        print("GT Real Time instantiated")
        self.server = server(debug=debugFlag)
        self.display = None
        self.renderImage = None
        self.gamepad = None
        self.img = None # for render
        self.modelMode = modelMode
        self.img_hist_len = 3
        self.img_hist = None
        self.raceState = None
        self.rewardFunction = None 
        self.imageSize = (imageWidth, imageHeight)
        self.colour = False
        self.trackChoice = trackChoice # 0 is HS, 1 is 400m
        self.carChoice = carChoice # 0 is MR2, 1 is Supra, 2 is Civic
        self.rewardMode = rewardMode
        self.inititalizeCommon() # starts the TCP server and waits for the emulator to connect
        
        self.vPosition = None # used to track wherever the vehicle is and for calculating rewards
        self.vColl = None # used to track the vehicle contact and for calculating rewards
        self.vSpeed = None
        self.vDir = None
        
        if discAccelOnly:
            self.controlChoice = 7
            print("Discrete Accel Only 7")

        elif contAccelOnly:
            self.controlChoice = 6
            print("Cont Accel Only 6")
            
        elif discreteAccel and not accelAndBrake and discSteer: # discreteAccel & not accelAndBrake & discreteSteer
            self.controlChoice = 2
            print("Discrete Accel or Brake (cannot left foot) and Discrete Steering 2")
        
    # Maybe needed (at least as a helper) wrong place?
    def getDataImage(self):  
        import cv2
        self.server.receiveOneFrame()
        self.raceState = np.int64(self.server.myData.GS.raceState)  
        if self.modelMode >= 10:
            dataType = 'int64'
            rState = np.int64(self.server.myData.GS.raceState)  
            eClutch = np.int64(self.server.myData.VS.eClutch)
            eSpeed = np.int64(self.server.myData.VS.engSpeed)
            eBoost = np.int64(self.server.myData.VS.engBoost)
            eGear  = np.int64(self.server.myData.VS.engGear)
            self.vSpeed = np.int64(self.server.myData.VS.speed)
            vSteer = np.int64(self.server.myData.VS.steer)
            self.vDir = np.int64(self.server.myData.drivingDir)
            rState = np.int64(self.server.myData.GS.raceState)
            self.vColl = np.int64(self.server.myData.VS.vColl)
        else:
            dataType = 'float64'
            eClutch = np.array([self.server.myData.VS.eClutch/3], dtype=dataType)
            eSpeed = np.array([self.server.myData.VS.engSpeed/10000], dtype=dataType)
            eBoost = np.array([self.server.myData.VS.engBoost/10000], dtype=dataType)
            eGear  = np.array([self.server.myData.VS.engGear/6], dtype=dataType)
            self.vSpeed = np.array([self.server.myData.VS.speed/500], dtype=dataType)
            vSteer = np.array([self.server.myData.VS.steer/1024], dtype=dataType)
            self.vDir = np.array([self.server.myData.drivingDir/3], dtype=dataType)
            rState = np.array([self.server.myData.GS.raceState], dtype=dataType)
            self.vColl = np.array([self.server.myData.VS.vColl/12], dtype=dataType)
      
       
        fLeftSlip = np.array([self.server.myData.VS.fLeftSlip/256], dtype=dataType)
        fRightSlip =np.array([self.server.myData.VS.fRightSlip/256], dtype=dataType)
        rLeftSlip = np.array([self.server.myData.VS.rLeftSlip/256], dtype=dataType)
        rRightSlip =np.array([self.server.myData.VS.rRightSlip/256], dtype=dataType)
        self.vPosition = np.array([self.server.myData.posVect.x, self.server.myData.posVect.y], dtype=dataType)
        
        fLWheel= np.array([self.server.myData.VS.fLWheel/4], dtype=dataType)
        fRWheel= np.array([self.server.myData.VS.fRWheel/4], dtype=dataType)
        rLWheel= np.array([self.server.myData.VS.rLWheel/4], dtype=dataType)
        rRWheel= np.array([self.server.myData.VS.rRWheel/4], dtype=dataType)
        # trackID = self.server.myData.trackID

        # mode 1 to 15 resizes and
        if self.modelMode >= 1 and self.modelMode < 10:       
            tmp = cv2.resize(self.server.pic, (self.imageSize[0], self.imageSize[1]))
            tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
            tmp = tmp[:,:,np.newaxis]
            self.renderImage = tmp
            # print(tmp.shape)
        else:
            self.renderImage = self.server.pic
        return rState, eClutch, eSpeed, eBoost, eGear, vSteer, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, self.renderImage

    def startServerToRedux(self):
        self.server.connect()
        logging.debug("Server session started")
        
    def initControl(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()
        logging.debug("Virtual Dual Shock 4 loaded")
        
        
    def inititalizeCommon(self):
        self.img_hist = deque(maxlen=self.img_hist_len)
        self.initControl()
        self.startServerToRedux()
        if self.trackChoice == 0:
            self.rewardFunction = RewardFunction(filename='J:\git\TensorFlowPSX\Py\hsSpaced.csv')
                
        elif self.trackChoice == 1:
            self.rewardFunction = RewardFunction(filename='J:\git\TensorFlowPSX\Py\dragSpaced.csv')
        
    # Mandatory method        
    def get_observation_space(self):
        if self.modelMode >= 10:
            eClutch = spaces.Discrete(4)
            eSpeed = spaces.Discrete(10000)
            eBoost = spaces.Discrete(10000)
            eGear =  spaces.Discrete(6)
            vSpeed = spaces.Discrete(500)
            rState = spaces.Discrete(6)
            vDir = spaces.Discrete(4)
            vSteer = spaces.Discrete(1024*2+1, start=-1024)
            vColl = spaces.Discrete(13)
            
            vPosition = spaces.Box(low=-3000000.0, high=3000000.0, shape=(2,), dtype='int64') 
            fLeftSlip  = spaces.Box(low=0, high=256, shape=(1,), dtype='int64')
            fRightSlip = spaces.Box(low=0, high=256, shape=(1,), dtype='int64')
            rLeftSlip  = spaces.Box(low=0, high=256, shape=(1,), dtype='int64')
            rRightSlip = spaces.Box(low=0, high=256, shape=(1,), dtype='int64')
            fLWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='int64')
            fRWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='int64')
            rLWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='int64')
            rRWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='int64')
            
        # vVel = spaces.Box(low=-300.0, high=300, dtype='uint8') # Given up idea (wanted local vedctor speed)
        # https://gymnasium.farama.org/api/spaces/fundamental/#multidiscrete says that it has a start function to offset a multidiscrete box but clearly not
        
        else:
            eClutch = spaces.Box(low=0, high=1, shape=(1,), dtype='float64') # 3
            eSpeed = spaces.Box(low=0, high=1.0, shape=(1,), dtype='float64') # 10000
            eBoost = spaces.Box(low=0, high=1.0, shape=(1,), dtype='float64') # 10000
            eGear =  spaces.Box(low=0, high=1, shape=(1,), dtype='float64') #6
            vSpeed = spaces.Box(low=0, high=1, shape=(1,), dtype='float64') #500
            rState = spaces.Box(low=0, high=3, shape=(1,), dtype='float64') #5
            vDir = spaces.Box(low=0, high=1, shape=(1,), dtype='float64')  # 3
            vSteer = spaces.Box(low=-1, high=1, shape=(1,), dtype='float64') # 1024
            vColl = spaces.Box(low=0, high=1, shape=(1,), dtype='float64') # 12
            image = spaces.Box(low=0, high=255, shape=(self.imageSize[1], self.imageSize[0], 1), dtype='uint8') #255
            
            vPosition = spaces.Box(low=-3000000, high=3000000, shape=(2,), dtype='float64')  #3000000
            fLeftSlip  = spaces.Box(low=0, high=1, shape=(1,), dtype='float64') #256
            fRightSlip = spaces.Box(low=0, high=1, shape=(1,), dtype='float64')
            rLeftSlip  = spaces.Box(low=0, high=1, shape=(1,), dtype='float64')
            rRightSlip = spaces.Box(low=0, high=1, shape=(1,), dtype='float64')
            fLWheel= spaces.Box(low=0, high=1, shape=(1,), dtype='float64') #4
            fRWheel= spaces.Box(low=0, high=1, shape=(1,), dtype='float64')
            rLWheel= spaces.Box(low=0, high=1, shape=(1,), dtype='float64')
            rRWheel= spaces.Box(low=0, high=1, shape=(1,), dtype='float64')

        # 3 images    
        if self.modelMode == 1:
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, image, image, image))
        
        elif self.modelMode == 2:
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vColl, image, image, image))
        
        elif self.modelMode == 3:
            return spaces.Tuple((rState, eClutch, eSpeed, vSpeed, image, image, image))
        
        elif self.modelMode == 3.5:
            return spaces.Tuple((image, image, image))
        
        # single image
        elif self.modelMode == 5:  
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, image))
        
        elif self.modelMode == 6:    
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vColl, image))
        
        elif self.modelMode == 7:      
            return spaces.Tuple((rState, eClutch, eSpeed, vSpeed, image))

        elif self.modelMode == 10:
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vDir, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel))

        elif self.modelMode == 11:
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip))       

        elif self.modelMode == 12:
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip))  
        
        elif self.modelMode == 13:
            return spaces.Tuple((rState, eClutch, eSpeed, vSpeed))    
        
        elif self.modelMode == 14:
            return spaces.Tuple((rState, eClutch, eSpeed, vSpeed, vPosition))
        
                
    # Mandatory method
    def get_action_space(self):
        if self.controlChoice ==7:
            return spaces.Box(low=np.array([0.0, 0.0]), high=np.array([1.0, 1.0]), dtype='float64')
        elif self.controlChoice ==6:
            return spaces.Box(low=np.array([0.0]), high=np.array([1.0]), dtype='float64')
        elif self.controlChoice ==2:
            return spaces.Box(low=np.array([0.0,-1.0]), high=np.array([1.0,1.0]), dtype='float64')
    
    # Mandatory method
    def get_default_action(self):
        if self.controlChoice ==7:
            return np.array([0.0,0.0], dtype='float64')
        elif self.controlChoice ==6:
            return np.array([0.0], dtype='float64')
        elif self.controlChoice ==2:
            return np.array([0.0 ,0.0], dtype='float64')
    
    
    def getObs(self, reset):
        rState, eClutch, eSpeed, eBoost, eGear, vSteer, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, display = self.getDataImage()
        if self.modelMode >= 1 and self.modelMode < 5:
            if not reset:          
                self.img_hist.append(display)
                displayHistory = np.array(list(self.img_hist), dtype='uint8')
            else:
                for _ in range(self.img_hist_len):
                    self.img_hist.append(display)
                displayHistory = np.array(list(self.img_hist), dtype='uint8')
            
        if self.modelMode == 1:
            obs = [rState, eClutch, eSpeed, eBoost, eGear, self.vSpeed, vSteer, self.vDir, self.vColl, displayHistory[0], displayHistory[1], displayHistory[2]]

        elif self.modelMode == 2:
            obs = [rState, eClutch, eSpeed, eBoost, eGear, self.vSpeed, vSteer, self.vColl, displayHistory[0], displayHistory[1], displayHistory[2]]

        elif self.modelMode == 3:    
            obs = [rState, eClutch, eSpeed, self.vSpeed, displayHistory[0], displayHistory[1], displayHistory[2]]
            
        elif self.modelMode == 3.5:    
            obs = [displayHistory[0], displayHistory[1], displayHistory[2]]
        
        elif self.modelMode == 5:  
            obs = [rState, eClutch, eSpeed, eBoost, eGear, self.vSpeed, vSteer, self.vDir, self.vColl, display]
        
        elif self.modelMode == 6:    
            obs = [rState, eClutch, eSpeed, eBoost, eGear, self.vSpeed, vSteer, self.vColl, display]
        
        elif self.modelMode == 7:      
            obs = [rState, eClutch, eSpeed, self.vSpeed, display]
                           
        elif self.modelMode == 10:      
            obs = [rState, eClutch, eSpeed, eBoost, eGear, self.vSpeed, self.vDir, self.vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel]     
        
        elif self.modelMode == 13:      
            obs = [rState, eClutch, eSpeed, self.vSpeed]     
        
        elif self.modelMode == 14:      
            obs = [rState, eClutch, eSpeed, self.vSpeed, self.vPosition]   

        elif self.modelMode == 99:    # debug
            obs = [rState, display]
        return obs    
    
    # Mandatory method
    def reset(self, seed=None, options=None):
        print("reset triggered")
        choiceA = 0
        choiceB = 0
        if self.carChoice == 1:
            choiceA = 16 # Supra
        if self.trackChoice == 1: # 1: Drag, 0: HS
            choiceB = 8 # HS
        if None: # set control modes that have Ds
            a = None
        if None: # set control modes that have Da
            b = None
        if None: # set CPU
            c = None
            
        choice = choiceA + choiceB + 64 # hack to avoid missed ping as a load
        self.rewardFunction.reset()         
        self.server.reloadSave(choice) # loads the save state
        obs = self.getObs(reset=True)
        
        return obs, {}
            
    # Mandatory method
    def get_obs_rew_terminated_info(self):       
        obs = self.getObs(reset=False)
        reward, terminated = self.rewardFunction.computeReward(pos=self.vPosition, vColl=self.vColl, vDir=self.vDir, vSpeed=self.vSpeed, mode=self.rewardMode)
        if self.modelMode < 10:
            reward = reward[0]
        
        info = {}

        if self.raceState == 3:
            terminated = True
            # reward = reward + 500 # a new idea
        return obs, reward, terminated, info
    
    # Mandatory method
    def send_control(self, control):
        controlGamepad(self.gamepad, control, self.controlChoice)

    # Optional method
    def wait(self):
        self.send_control(self.get_default_action())
        
    # Optional method
    def render(self):
        # uncomment for debug env
        if self.modelMode >= 1 and self.modelMode < 5:
            displayHistory = np.array(list(self.img_hist), dtype='uint8')
            cv2.imshow('Render Display1', displayHistory[0])
            cv2.imshow('Render Display2', displayHistory[1])
            cv2.imshow('Render Display3', displayHistory[2])
        elif self.modelMode >= 5 and self.modelMode < 10:
            cv2.imshow('Render Display', self.renderImage)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
        
        # for other methods
        return self.renderImage