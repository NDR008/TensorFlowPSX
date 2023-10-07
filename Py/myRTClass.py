"""
Environment class for a Real Time Gymnasium Environment for Gran Turismo
Written by NDR008
nadir.syedsammut@gmail.com
Development started in December 2022

Notes to self: RLLIB cannot use Boxes for actions, need MultiDiscrete:
(RolloutWorker pid=18956) ValueError: Box(..., `int`) action spaces are not supported. Use MultiDiscrete  or Box(..., `float`).
"""


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
    def __init__(self, debugFlag=False, discreteAccel=True, accelAndBrake=False, discSteer=True, contAccelOnly=False, discAccelOnly=False, modelMode=2, agent="PPO", imageHeight=240, imageWidth=320, trackChoice=1):
        """MyGranTurismoRTGYM returns an environment that contains a gym environment and a server session to receive data from PCSX Redux.
        Args:
            debugFlag (bool, optional): Makes the server do image rendinering (and not use the env.render()). Defaults to False.
            discreteAccel (bool, optional): Determines if the accelerator is discrete, otherwise continuous. Defaults to True.
            accelAndBrake (bool, optional): Determines if the accelerator can be pressed while braking (only for discrete). Defaults to False.
            discSteer (bool, optional): Determines if the steering is discrete, otherwise continuous. Defaults to True.
            contAccelOnly (bool, optional): Detrmines if ONLY accelerator exists in the control space as a continuous space (overwites other parameters). Defaults to False.
            discAccelOnly (bool, optional): Detrmines if ONLY accelerator exists in the control space as a discrete space (overwites other parameters). Defaults to False.
            modelMode (int, optional): Models 1 to 4 are using 3 image histories (greyscale), Mode 5 to 9 use single images, Mode 10 to 14 use parameters only. Defaults to 2.
            agent (str, optional): Note used. Defaults to "PPO".
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
        self.agent = agent
        self.imageSize = (imageWidth, imageHeight)
        self.colour = False
        self.trackChoice = trackChoice # 1 is HS, 2 is 0-400m
        self.inititalizeCommon() # starts the TCP server and waits for the emulator to connect
        self.lastPos = np.array([0,0])
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
        # eClutch = np.array([self.server.myData.VS.eClutch], dtype='int64')
        # eSpeed = np.array([self.server.myData.VS.engSpeed], dtype='int64')
        # eBoost = np.array([self.server.myData.VS.engBoost], dtype='int64')
        # eGear  = np.array([self.server.myData.VS.engGear], dtype='int64')
        # vSpeed = np.array([self.server.myData.VS.speed], dtype='int64')
        # vSteer = np.array([self.server.myData.VS.steer], dtype='int64')
        # vDir = np.array([self.server.myData.drivingDir], dtype='int64')
        fLeftSlip = np.array([self.server.myData.VS.fLeftSlip], dtype='int64')
        fRightSlip =np.array([self.server.myData.VS.fRightSlip], dtype='int64')
        rLeftSlip = np.array([self.server.myData.VS.rLeftSlip], dtype='int64')
        rRightSlip =np.array([self.server.myData.VS.rRightSlip], dtype='int64')
        vPosition = np.array([self.server.myData.posVect.x, self.server.myData.posVect.y], dtype='int64')
        fLWheel= np.array([self.server.myData.VS.fLWheel], dtype='int64')
        fRWheel= np.array([self.server.myData.VS.fRWheel], dtype='int64')
        rLWheel= np.array([self.server.myData.VS.rLWheel], dtype='int64')
        rRWheel= np.array([self.server.myData.VS.rRWheel], dtype='int64')
        # trackID = self.server.myData.trackID
        self.raceState = self.server.myData.GS.raceState    
        eClutch = np.int64(self.server.myData.VS.eClutch)
        eSpeed = np.int64(self.server.myData.VS.engSpeed)
        eBoost = np.int64(self.server.myData.VS.engBoost)
        eGear  = np.int64(self.server.myData.VS.engGear)
        vSpeed = np.int64(self.server.myData.VS.speed)
        vSteer = np.int64(self.server.myData.VS.steer)
        vDir = np.int64(self.server.myData.drivingDir)
        rState = np.int64(self.raceState)

        # resize to (imageWidth, imageHeight) passed through config
        # mode 1 to 15 resizes and
        if self.modelMode >= 1 and self.modelMode < 10:       
            tmp = cv2.resize(self.server.pic, (self.imageSize[0], self.imageSize[1]))
            #tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
            self.renderImage = tmp
            # print(tmp.shape)
        else:
            self.renderImage = self.server.pic
        return rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, self.renderImage

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
        if self.trackChoice == 1:
            self.rewardFunction = RewardFunction(filename='J:\git\TensorFlowPSX\Py\hsSpaced.csv')
                
        elif self.trackChoice == 2 or 3:
            self.rewardFunction = RewardFunction(filename='J:\git\TensorFlowPSX\Py\dragSpaced.csv')
        
    # Mandatory method        
    def get_observation_space(self):
        # eXXXX for engineXXXX
        # vXXX for vehicleXXX
        eClutch = spaces.Discrete(4)
        eSpeed = spaces.Discrete(10000)
        eBoost = spaces.Discrete(10000)
        eGear =  spaces.Discrete(6)
        vSpeed = spaces.Discrete(500)
        rState = spaces.Discrete(6)
        vDir = spaces.Discrete(4)
        vSteer = spaces.Discrete(1024*2+1, start=-1024)
        vPosition = spaces.Box(low=-3000000.0, high=3000000, shape=(2,), dtype='int64')
        vVel = spaces.Box(low=-300.0, high=300, dtype='uint8') # Given up idea (wanted local vedctor speed)
        # https://gymnasium.farama.org/api/spaces/fundamental/#multidiscrete says that it has a start function to offset a multidiscrete box but clearly not
            
        if self.modelMode == 1:
            images = spaces.Box(low=0.0, high=255.0, shape=(self.img_hist_len, self.imageSize[1], self.imageSize[0], 3), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, images))
        
        elif self.modelMode == 2:
            vSteer = spaces.Discrete(1024*2+1, start=-1024)
            images = spaces.Box(low=0, high=255, shape=(self.img_hist_len, self.imageSize[1], self.imageSize[0], 3), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, images))
        
        elif self.modelMode == 3:
            vSteer = spaces.Discrete(1024*2+1, start=-1024)
            images = spaces.Box(low=0, high=255, shape=(self.img_hist_len, self.imageSize[1], self.imageSize[0], 3), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSteer, images))
        
        # single image
        elif self.modelMode == 5:
            vSteer = spaces.Discrete(1024*2+1, start=-1024)    
            image = spaces.Box(low=0, high=255, shape=(self.imageSize[1], self.imageSize[0], 3), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, image))
        
        elif self.modelMode == 6:    
            image = spaces.Box(low=0, high=255, shape=(self.imageSize[1], self.imageSize[0], 3), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSteer, image))
        
        elif self.modelMode == 7:      
            image = spaces.Box(low=0, high=255, shape=(self.imageSize[1], self.imageSize[0], 3), dtype='uint8')
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, image))


        elif self.modelMode == 10:
            fLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            fRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            rLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            fLWheel= spaces.Box(low=0, high=4, shape=(1,))
            fRWheel= spaces.Box(low=0, high=4, shape=(1,))
            rLWheel= spaces.Box(low=0, high=4, shape=(1,))
            rRWheel= spaces.Box(low=0, high=4, shape=(1,))
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vDir, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel))

        elif self.modelMode == 11:
            fLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            fRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            rLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            fLWheel= spaces.Box(low=0, high=4, shape=(1,))
            fRWheel= spaces.Box(low=0, high=4, shape=(1,))
            rLWheel= spaces.Box(low=0, high=4, shape=(1,))
            rRWheel= spaces.Box(low=0, high=4, shape=(1,))
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip))       

        elif self.modelMode == 11:
            fLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            fRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            rLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            fLWheel= spaces.Box(low=0, high=4, shape=(1,))
            fRWheel= spaces.Box(low=0, high=4, shape=(1,))
            rLWheel= spaces.Box(low=0, high=4, shape=(1,))
            rRWheel= spaces.Box(low=0, high=4, shape=(1,))
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip))  
        
        elif self.modelMode == 12:
            fLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            fRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            rLeftSlip  = spaces.Box(low=0, high=256, shape=(1,))
            rRightSlip = spaces.Box(low=0, high=256, shape=(1,))
            fLWheel= spaces.Box(low=0, high=4, shape=(1,))
            fRWheel= spaces.Box(low=0, high=4, shape=(1,))
            rLWheel= spaces.Box(low=0, high=4, shape=(1,))
            rRWheel= spaces.Box(low=0, high=4, shape=(1,))
            return spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear))    
        
        elif self.modelMode == 99:
            image = spaces.Box(low=0.0, high=255.0, shape=(240, 320, 3), dtype='uint8')
            return spaces.Tuple((rState, image))
                
    # Mandatory method
    def get_action_space(self):
        if self.controlChoice ==7:
            return spaces.Box(low=np.array([0.0, 0.0]), high=np.array([1.0, 1.0]), dtype='float64')
        elif self.controlChoice ==6:
            return spaces.Box(low=np.array([0.0]), high=np.array([1.0]), dtype='float64')
        elif self.controlChoice ==2:
            return spaces.Box(low=np.array([0.0,-1.0]), high=np.array([1.0,1.0]), dtype='float64')
            #return spaces.Box(low=-1.0, high=1.0, shape=(3,))
        # if self.agent == "SAC" or "A3C":
        #     return spaces.Box(low=np.array([0.0, 0.0, -1.0]), high=np.array([1.0, 1.0, 1.0]), dtype='float64')
        # else:
        #     return spaces.MultiDiscrete([ 2, 2, 3 ])
    
    # Mandatory method
    def get_default_action(self):
        if self.controlChoice ==7:
            return np.array([0.0,0.0], dtype='float64')
        elif self.controlChoice ==6:
            return np.array([0.0,0.0], dtype='float64')
        elif self.controlChoice ==2:
            return np.array([0.0 ,0.0], dtype='float64')
        # if self.agent == "SAC" or "A3C":
        #     return np.array([0.0, 0.0, 0.0], dtype='float64')
        # else:
        #     return np.array([0, 0, 0])
    
    # Mandatory method
    def reset(self, seed=None, options=None):
        print("reset triggered")
        self.server.reloadSave(self.trackChoice+1) # loads the save state
        rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, display = self.getDataImage()       
        self.lastPos = vPosition
        vVel = np.array([0,0])
        
        if self.modelMode >= 1 and self.modelMode < 5:
            for _ in range(self.img_hist_len):
                self.img_hist.append(display)
            displayHistory = np.array(list(self.img_hist), dtype='uint8')

        if self.modelMode == 1:
            obs = [rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, displayHistory]

        elif self.modelMode == 2:
            obs = [rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, displayHistory]

        elif self.modelMode == 3:    
            obs = [rState, eClutch, eSpeed, eBoost, eGear, vSteer, displayHistory]
             
        elif self.modelMode == 7:    
            obs = [rState, eClutch, eSpeed, eBoost, eGear, display]           
             
        elif self.modelMode == 99:    # debug
            obs = [rState, display]
            print(np.shape(obs[1]))
             
        # elif self.modelMode == 4:
        #     obs = [rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vDir, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel] 
            
        # obs = [eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, display]
        # self.rewardFunction.reset() # reward_function not implemented yet
        return obs, {}
        
    # Mandatory method
    def get_obs_rew_terminated_info(self):
        rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vPosition, vDir, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, display = self.getDataImage()
        reward, terminated = self.rewardFunction.computeReward(vPosition)
        # vVel = (self.lastPos - vPosition)/10000
        
        if self.modelMode >= 1 and self.modelMode < 5:
            self.img_hist.append(display)
            displayHistory = np.array(list(self.img_hist), dtype='uint8')

        if self.modelMode == 1:
            obs = [rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, displayHistory]
            
        elif self.modelMode == 2:
            obs = [rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, displayHistory]

        elif self.modelMode == 3:    
            obs = [rState, eClutch, eSpeed, eBoost, eGear, vSteer, displayHistory]
             
        elif self.modelMode == 7:    
            obs = [rState, eClutch, eSpeed, eBoost, eGear, display]
             
        elif self.modelMode == 99:    # debug
            obs = [rState, display] 

        info = {}
        if self.raceState == 3:
            terminated = True
        #elif self.raceState == 1:
        #    terminated = False
        else:
            terminated = False
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
        if self.modelMode >= 5 and self.modelMode < 10:
            cv2.imshow('Render Display', self.renderImage)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
        
        # for other methods
        return self.renderImage