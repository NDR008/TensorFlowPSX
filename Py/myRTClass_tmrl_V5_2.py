"""
For CNN (tmrl)
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
#from rewardGT import RewardFunction
#from rewardGTV4_2 import RewardFunction
#from rewardGTV4_5 import RewardFunction
from rewardGTV5_2 import RewardFunction
from time import sleep

class MyGranTurismoRTGYM(RealTimeGymInterface):
    def __init__(self, debugFlag=False, controlMode=2, modelMode=1, imageHeight=64, imageWidth=64, trackChoice=1, carChoice=1, rewardMode="complex", testMode=False):
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
        self.img_hist_len = 4
        self.img_hist = None
        self.raceState = None
        self.rewardFunction = None 
        self.imageSize = (imageWidth, imageHeight)
        self.colour = False
        self.trackChoice = trackChoice # 0 is HS, 1 is 400m, 2 is Route5
        self.carChoice = carChoice # 0 is MR2, 1 is Supra, 2 is Civic
        self.rewardMode = rewardMode
        self.testMode = testMode
        self.inititalizeCommon() # starts the TCP server and waits for the emulator to connect
        
        self.vPosition = None # used to track wherever the vehicle is and for calculating rewards
        self.vColl = None # used to track the vehicle contact and for calculating rewards
        self.vSpeed = None
        self.vDir = None
        self.controlChoice = controlMode
        self.debugCounter = 0
        self.reward = 0
        self.terminated = False
        
    # Maybe needed (at least as a helper) wrong place?
    def getDataImage(self):  
        import cv2
        self.server.receiveOneFrame()
        self.raceState = np.int64(self.server.myData.GS.raceState)  

        rState = np.array([self.server.myData.GS.raceState], dtype='uint8')
        eClutch = np.array([self.server.myData.VS.eClutch], dtype='uint8')
        eSpeed = np.array([self.server.myData.VS.engSpeed], dtype='int32')
        eBoost = np.array([self.server.myData.VS.engBoost], dtype='int32')
        eGear  = np.array([self.server.myData.VS.engGear], dtype='uint8')
        self.vSpeed = np.array([self.server.myData.VS.speed], dtype='int32')
        vSteer = np.array([self.server.myData.VS.steer], dtype='int32')
        self.vDir = np.array([self.server.myData.drivingDir], dtype='uint8')
        self.vColl = np.array([self.server.myData.VS.vColl], dtype='uint8') 
        
        fLeftSlip = np.array([self.server.myData.VS.fLeftSlip], dtype='uint8')
        fRightSlip =np.array([self.server.myData.VS.fRightSlip], dtype='uint8')
        rLeftSlip = np.array([self.server.myData.VS.rLeftSlip], dtype='uint8')
        rRightSlip =np.array([self.server.myData.VS.rRightSlip], dtype='uint8')
        deltaPos = np.array([self.server.myData.deltaVect.x, self.server.myData.deltaVect.y], dtype='int32')
        self.vPosition = np.array([self.server.myData.posVect.x, self.server.myData.posVect.y], dtype='int32')
        
        fLWheel= np.array([self.server.myData.VS.fLWheel], dtype='uint8')
        fRWheel= np.array([self.server.myData.VS.fRWheel], dtype='uint8')
        rLWheel= np.array([self.server.myData.VS.rLWheel], dtype='uint8')
        rRWheel= np.array([self.server.myData.VS.rRWheel], dtype='uint8')
        #vAccel = np.array([self.server.myData.VS.vAccel], dtype='int32')

        # mode 1 to 15 resizes and
        tmp = cv2.resize(self.server.pic, (self.imageSize[0], self.imageSize[1]))
        tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        #tmp = tmp[:,:,np.newaxis]
        self.renderImage = tmp
        # print(tmp.shape)
        return eClutch, eSpeed, eBoost, eGear, vSteer, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, deltaPos

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

        elif self.trackChoice == 2:
            self.rewardFunction = RewardFunction(
                filename='J:\git\TensorFlowPSX\Py\\route5Spaced.csv')
            
        elif self.trackChoice == 2.5:
            print("mode2.5")
            self.rewardFunction = RewardFunction(
                filename='J:\git\TensorFlowPSX\Py\\route5Spaced.csv', start=10800)
        
    # Mandatory method        
    def get_observation_space(self):
        eBoost = spaces.Box(low=0, high=10000, shape=(1,), dtype='int32') # 10000
        eGear =  spaces.Box(low=0, high=6, shape=(1,), dtype='uint8') #6
        vSpeed = spaces.Box(low=0, high=500, shape=(1,), dtype='int32') #500
        vSteer = spaces.Box(low=-1024, high=1024, shape=(1,), dtype='int32')        
        vDir = spaces.Box(low=0, high=1, shape=(1,), dtype='uint8')
        deltaPos = spaces.Box(low=-5000.0, high=5000.0,  shape=(1,), dtype='int32')
        vPosition = spaces.Box(low=-3000000.0, high=3000000.0, shape=(1,), dtype='int32') 
        fPosition1 = spaces.Box(low=-3000000.0, high=3000000.0, shape=(1,), dtype='int32')
        fPosition2 = spaces.Box(low=-3000000.0, high=3000000.0, shape=(1,), dtype='int32')
        fLeftSlip  = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8') 
        fRightSlip = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8')
        rLeftSlip  = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8')
        rRightSlip = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8')
        
        fRColl = spaces.Box(low=0, high=1, shape=(1,), dtype='uint8')
        fLColl = spaces.Box(low=0, high=1, shape=(1,), dtype='uint8')
        rRColl = spaces.Box(low=0, high=1, shape=(1,), dtype='uint8')
        rLColl = spaces.Box(low=0, high=1, shape=(1,), dtype='uint8')

        
        images = spaces.Box(low=0, high=255, shape=(self.img_hist_len, self.imageSize[1], self.imageSize[0]), dtype='uint8') #255`

        return spaces.Tuple((eBoost, eGear, vSpeed, vSteer, vDir,  # eBoost, eGear, self.vSpeed, vSteer, self.vDir,
                                fLColl, fRColl, rRColl, rLColl,    # pars[0], pars[1], pars[2], pars[3], 
                                rLeftSlip, rRightSlip, fLeftSlip, fRightSlip,  # rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, 
                                deltaPos, deltaPos, 
                                vPosition, vPosition, 
                                fPosition1, fPosition1,
                                fPosition2, fPosition2,  # vAccel, self.vPosition,
                                images))

    # Mandatory method
    def get_action_space(self):
        if self.controlChoice == 0:
            return spaces.Box(low=-1.0, high=1.0, shape=(3, ))
        elif self.controlChoice >=1:
            return spaces.Box(low=-1.0, high=1.0, shape=(2, ))
    
    # Mandatory method
    def get_default_action(self):
        if self.controlChoice == 0:
            return np.array([1.0 ,0.0, 0.0], dtype='float32')
        elif self.controlChoice >= 1:
            return np.array([1.0 ,0.0], dtype='float32')
    
    
    def getObs(self, reset):
        eClutch, eSpeed, eBoost, eGear, vSteer, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, deltaPos = self.getDataImage()

        if not reset:          
            self.img_hist.append(self.renderImage)
            displayHistory = np.array(list(self.img_hist), dtype='uint8')
        else:
            for _ in range(self.img_hist_len):
                self.img_hist.append(self.renderImage)
            displayHistory = np.array(list(self.img_hist), dtype='uint8')
            
        #print(displayHistory.shape)
        # Extra work to convert back the collision int into 4 bits
        tmpColl = bin(self.vColl[0])
        tmpColl = tmpColl[2:]
        # 1s, 2s, 4s, 8s
        zero = np.array([0], dtype='uint8')
        pars = np.array([zero,zero,zero,zero], dtype='uint8')
        for i in range(len(tmpColl)):
            pars[i] = np.array(int(tmpColl[-(i+1)]), dtype='uint8')
            
        if (fLWheel + fRWheel + rLWheel + rRWheel) > 4:
            wheelOff = 1
        else:
            wheelOff = 0
        
        reward, self.terminated, future1, future2 = self.rewardFunction.computeReward(pos=self.vPosition, vColl=self.vColl, vDir=self.vDir, vSpeed=self.vSpeed, wheelOff=wheelOff, mode=self.rewardMode)     
        self.reward=np.float32(reward)
        obs = [eBoost, eGear, self.vSpeed, vSteer, self.vDir,
                pars[0], pars[1], pars[2], pars[3], 
                rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, 
                np.array([deltaPos[0]], dtype='int32'),np.array([deltaPos[1]], dtype='int32'),  
                np.array([self.vPosition[0]]),         np.array([self.vPosition[1]], dtype='int32'),  
                np.array([future1[0]], dtype='int32'), np.array([future1[1]], dtype='int32'),  
                np.array([future2[0]], dtype='int32'), np.array([future2[1]], dtype='int32'),  
                displayHistory]       
            
        return obs    
    
    # Mandatory method
    def reset(self, seed=None, options=None):
        self.send_control(self.get_default_action())
        print("reset triggered")
        choiceA = 0
        choiceB = 0
        if self.carChoice == 1:
            choiceA = 16 # Supra
        elif self.carChoice == 2:
            choiceA = 0 + 128
        if self.trackChoice == 1: # 1: Drag, 0: HS
            choiceB = 8 # HS
        elif self.trackChoice == 2:
            choiceB = 9
        elif self.trackChoice == 2.5:
            choiceB = 22
            
        choice = choiceA + choiceB + 64 # hack to avoid missed ping as a load
        print("self.controlChoice", self.controlChoice)
        print("self.carChoice", self.carChoice)
        print("self.trackChoice", self.trackChoice)
        if self.controlChoice > 1 and self.controlChoice < 2:
            choice = choice + 10
        self.rewardFunction.reset()         
        if self.testMode:
            choice = choice + 100
        print("total choice", choice)
        self.server.reloadSave(choice) # loads the save state
        obs = self.getObs(reset=True)

        return obs, {}
            
    # Mandatory method
    def get_obs_rew_terminated_info(self):       
        obs = self.getObs(reset=False)
        info = {}

        if self.raceState == 3:
            self.terminated = True
        
        
        return obs, self.reward, self.terminated, info
    
    # Mandatory method
    def send_control(self, control):
        controlGamepad(self.gamepad, control, self.controlChoice)

    # Optional method
    def wait(self):
        sleep(10)
        self.send_control(self.get_default_action())
        
    # Optional method
    def render(self):
        # uncomment for debug env
        #displayHistory = np.array(list(self.img_hist), dtype='uint8')
        for index, img in enumerate(list(self.img_hist)): #list to avoid mutation whilst rendering
            display = "display " + str(index)
            cv2.imshow(display, img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
        
        # for other methods
        return self.renderImage