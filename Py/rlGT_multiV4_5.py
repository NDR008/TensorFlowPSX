import numpy as np  
# Training parameters:

CRC_DEBUG = False
worker_device = "cpu"
trainer_device = "cuda"
imgSize = 64 #assuming 64 x 64
imgHist = 4
LEARN_ENTROPY_COEF = True
ENTROPCOEFF = 0.2 #0.2
LR_ACT1 = 1e-3
LR_CRIT = 1e-3
LR_ENTR = 1e-3

MEMORY_SIZE = 1e6 #1e6
ACT_BUF_LEN = 2
maxEpLength = 3500
BATCH_SIZE = 1024 * 2
EPOCHS = np.inf # maximum number of epochs, usually set this to np.inf
rounds = 10  # number of rounds per epoch (to print stuff)
steps = 1000  # number of training steps per round 1000
update_buffer_interval = 500 # 2000 #steps 1000
update_model_interval = 500  # 2000 #steps 1000
max_training_steps_per_env_step = 1.0
start_training = 0 #2e5 # waits for... 1000
device = trainer_device
MODEL_MODE = 3
CONTROL_MODE = 2
CARCHOICE = 0

if CARCHOICE == 1:
    car = "Supra_mode_"
else:
    car = "MR2_mode_"

RUN_NAME = car + str(MODEL_MODE) + "_cont_" + str(CONTROL_MODE) + "4.5_AutoStart"
#RUN_NAME = _MR2_mode_3_cont_0_3W_Rew4.3_(start_past_weights)
#RUN_NAME = "DEBUG3" 

LOG_STD_MAX = 2
LOG_STD_MIN = -20

import gymnasium.spaces as spaces
import torch
from torch.optim import Adam
from copy import deepcopy

from tmrl.networking import Server, RolloutWorker, Trainer
from tmrl.util import partial, cached_property
from tmrl.envs import GenericGymEnv
from tmrl.actor import TorchActorModule
import tmrl.config.config_constants as cfg
from tmrl.training_offline import TorchTrainingOffline
from tmrl.training import TrainingAgent
from tmrl.custom.utils.nn import copy_shared, no_grad
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions.normal import Normal
from math import floor, sqrt
from torch.nn import Conv2d, Module
from tmrl.memory import TorchMemory
import random

rState = spaces.Box(low=0, high=5, shape=(1,), dtype='uint8')
eClutch = spaces.Box(low=0, high=3, shape=(1,), dtype='uint8')
eSpeed = spaces.Box(low=0, high=10000, shape=(1,), dtype='int32') # 10000
eBoost = spaces.Box(low=0, high=10000, shape=(1,), dtype='int32') # 10000
eGear =  spaces.Box(low=0, high=6, shape=(1,), dtype='uint8') #6
vSpeed = spaces.Box(low=0, high=500, shape=(1,), dtype='int32') #500
vSteer = spaces.Box(low=-1024, high=1024, shape=(1,), dtype='int32')        
vDir = spaces.Box(low=0, high=1, shape=(1,), dtype='uint8')
vColl = spaces.Box(low=0, high=12, shape=(1,), dtype='uint8')
vPosition = spaces.Box(low=-3000000.0, high=3000000.0, shape=(2,), dtype='int32') 
fLeftSlip  = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8') 
fRightSlip = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8')
rLeftSlip  = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8')
rRightSlip = spaces.Box(low=0, high=255, shape=(1,), dtype='uint8')         
fLWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')
fRWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')
rLWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')
rRWheel= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')

coll1= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')
coll2= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')
coll3= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')
coll4= spaces.Box(low=0, high=4, shape=(1,), dtype='uint8')


images = spaces.Box(low=0, high=255, shape=(4, imgSize, imgSize), dtype='uint8') #255`

if MODEL_MODE == 0:
    obs_space = spaces.Tuple((images,))
    NUMBER_1D_PARAMS = 0

elif MODEL_MODE == 1:
    obs_space = spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, #9
                              images))
    NUMBER_1D_PARAMS = 9
    
elif MODEL_MODE == 1.5:
    obs_space = spaces.Tuple((eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, #9
                              images))
    NUMBER_1D_PARAMS = 7   
    
elif MODEL_MODE == 2:
    obs_space =spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, #9
                             rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, #4
                             fLWheel, fRWheel, rLWheel, rRWheel, #4
                             images))
    NUMBER_1D_PARAMS = 17
elif MODEL_MODE == 3:
    obs_space =spaces.Tuple((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, #8
                             coll1, coll2, coll3, coll4, #4
                             rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, #4
                             fLWheel, fRWheel, rLWheel, rRWheel, #4
                             images))
    NUMBER_1D_PARAMS = 20

if CONTROL_MODE == 0:
    act_space = spaces.Box(low=-1.0, high=1.0, shape=(3, ))
    NUMBER_ACTION_DIMS = 3
else:
    act_space = spaces.Box(low=-1.0, high=1.0, shape=(2, ))
    NUMBER_ACTION_DIMS = 2

print(f"action space: {act_space}")
print(f"observation space: {obs_space}")


# === Worker ===========================================================================================================

import torch.nn.functional as F

def mlp(sizes, activation, output_activation=torch.nn.Identity):
    layers = []
    for j in range(len(sizes) - 1):
        act = activation if j < len(sizes) - 2 else output_activation
        layers += [torch.nn.Linear(sizes[j], sizes[j + 1]), act()]
    return torch.nn.Sequential(*layers)


def num_flat_features(x):
    size = x.size()[1:]
    num_features = 1
    for s in size:
        num_features *= s
    return num_features


def conv2d_out_dims(conv_layer, h_in, w_in):
    h_out = floor((h_in + 2 * conv_layer.padding[0] - conv_layer.dilation[0] * (conv_layer.kernel_size[0] - 1) - 1) / conv_layer.stride[0] + 1)
    w_out = floor((w_in + 2 * conv_layer.padding[1] - conv_layer.dilation[1] * (conv_layer.kernel_size[1] - 1) - 1) / conv_layer.stride[1] + 1)
    return h_out, w_out


class VanillaCNN(Module):
    def __init__(self, q_net):
        super(VanillaCNN, self).__init__()
        self.q_net = q_net
        self.h_out, self.w_out = imgSize, imgSize
        hist = imgHist

        self.conv1 = Conv2d(hist, 64, 8, stride=2)
        self.h_out, self.w_out = conv2d_out_dims(self.conv1, self.h_out, self.w_out)
        self.conv2 = Conv2d(64, 64, 4, stride=2)
        self.h_out, self.w_out = conv2d_out_dims(self.conv2, self.h_out, self.w_out)
        self.conv3 = Conv2d(64, 128, 4, stride=2)
        self.h_out, self.w_out = conv2d_out_dims(self.conv3, self.h_out, self.w_out)
        self.conv4 = Conv2d(128, 128, 4, stride=2)
        self.h_out, self.w_out = conv2d_out_dims(self.conv4, self.h_out, self.w_out)
        self.out_channels = self.conv4.out_channels
        self.flat_features = self.out_channels * self.h_out * self.w_out
        # act, # 9 + 4

        # generalised
        self.mlp_input_features = self.flat_features + NUMBER_1D_PARAMS + NUMBER_ACTION_DIMS * 3 if self.q_net else self.flat_features + NUMBER_1D_PARAMS + NUMBER_ACTION_DIMS * 2

        self.mlp_layers = [256, 256, 1] if self.q_net else [256, 256]
        self.mlp = mlp([self.mlp_input_features] + self.mlp_layers, nn.ReLU)

    def forward(self, x):
        #print("inQ", self.q_net, x)
        if MODEL_MODE == 0:
            if self.q_net:    
                images, act1, act2, act = x
            else:
                images, act1, act2 = x         
        
        elif MODEL_MODE == 1:
            if self.q_net:    
                rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, images, act1, act2, act = x
            else:
                rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, images, act1, act2 = x         
            rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl = rState/5, eClutch/3.0, eSpeed/10000.0, eBoost/10000.0, eGear/6.0, vSpeed/500.0, vSteer/1024.0, vDir, vColl/12.0

        elif MODEL_MODE == 1.5:
            if self.q_net:    
                eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, images, act1, act2, act = x
            else:
                eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, images, act1, act2 = x         
            eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl = eSpeed/10000.0, eBoost/10000.0, eGear/6.0, vSpeed/500.0, vSteer/1024.0, vDir, vColl/12.0
            
        elif MODEL_MODE == 2:
            if self.q_net:    
                rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, images, act1, act2, act = x
            else:
                rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, images, act1, act2 = x           
            
            # "Normalise" parameters [0,1]
            rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel = rState/5, eClutch/3.0, eSpeed/10000.0, eBoost/10000.0, eGear/6.0, vSpeed/500.0, vSteer/1024.0, vDir, vColl/12.0, rLeftSlip/255.0, rRightSlip/255.0, fLeftSlip/255.0, fRightSlip/255.0, fLWheel/4.0, fRWheel/4.0, rLWheel/4.0, rRWheel/4.0
            
        elif MODEL_MODE == 3:
            if self.q_net:    
                rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, fLColl, fRColl, rRColl, rLColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, images, act1, act2, act = x
            else:
                rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, fLColl, fRColl, rRColl, rLColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, images, act1, act2 = x           
            
            # "Normalise" parameters [0,1]
            rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, fLColl, fRColl, rRColl, rLColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel = rState/5, eClutch/3.0, eSpeed/10000.0, eBoost/10000.0, eGear/6.0, vSpeed/500.0, vSteer/1024.0, vDir, fLColl, fRColl, rRColl, rLColl, rLeftSlip/255.0, rRightSlip/255.0, fLeftSlip/255.0, fRightSlip/255.0, fLWheel/4.0, fRWheel/4.0, rLWheel/4.0, rRWheel/4.0
        
        #print(">>>>>>>>>>>>>>>>>>>>", images.shape)    
        images = images.to(torch.float32)/255.0


        x = F.relu(self.conv1(images))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        flat_features = num_flat_features(x)
        assert flat_features == self.flat_features, f"x.shape:{x.shape}, flat_features:{flat_features}, self.out_channels:{self.out_channels}, self.h_out:{self.h_out}, self.w_out:{self.w_out}"
        x = x.view(-1, flat_features) #flatten out of the CNN


        if MODEL_MODE == 0:
            if self.q_net:
                x = torch.cat((x, act1, act2, act), -1) # c
            else:
                x = torch.cat((x, act1, act2), -1) # concat
        
        elif MODEL_MODE == 1:
            if self.q_net:
                x = torch.cat((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, x, act1, act2, act), -1) # concat
            else:
                x = torch.cat((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, x, act1, act2), -1) # concat
        elif MODEL_MODE == 1.5:
            if self.q_net:
                x = torch.cat((eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, x, act1, act2, act), -1) # concat
            else:
                x = torch.cat((eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, x, act1, act2), -1) # concat                
        elif MODEL_MODE == 2:
            if self.q_net:
                x = torch.cat((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, x, act1, act2, act), -1) # concat
            else:
                x = torch.cat((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, x, act1, act2), -1) # concat               
        elif MODEL_MODE == 3:
            if self.q_net:
                x = torch.cat((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, fLColl, fRColl, rRColl, rLColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, x, act1, act2, act), -1) # concat
            else:
                x = torch.cat((rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, fLColl, fRColl, rRColl, rLColl, rLeftSlip, rRightSlip, fLeftSlip, fRightSlip, fLWheel, fRWheel, rLWheel, rRWheel, x, act1, act2), -1) # concat               
                
        x = self.mlp(x)
        return x

#####################################

class MyActorModule(TorchActorModule):
    def __init__(self, observation_space, action_space):
        super().__init__(observation_space, action_space)
        dim_act = action_space.shape[0]
        act_limit = action_space.high[0]
        self.net = VanillaCNN(q_net=False)
        self.mu_layer = nn.Linear(256, dim_act)
        self.log_std_layer = nn.Linear(256, dim_act)
        self.act_limit = act_limit

    def forward(self, obs, test=False, with_logprob=True):
        net_out = self.net(obs)
        mu = self.mu_layer(net_out)
        log_std = self.log_std_layer(net_out)
        log_std = torch.clamp(log_std, LOG_STD_MIN, LOG_STD_MAX)
        std = torch.exp(log_std)

        pi_distribution = Normal(mu, std)
        if test:
            pi_action = mu  # mean of the gauss --> deterministic policy 
        else:
            pi_action = pi_distribution.rsample()

        if with_logprob:
            logp_pi = pi_distribution.log_prob(pi_action).sum(axis=-1)
            # NB: this is from Spinup:
            logp_pi -= (2 * (np.log(2) - pi_action - F.softplus(-2 * pi_action))).sum(axis=1)  # FIXME: this formula is mathematically wrong, no idea why it seems to work
            # Whereas SB3 does this:
            # logp_pi -= torch.sum(torch.log(1 - torch.tanh(pi_action) ** 2 + EPSILON), dim=1)  # TODO: double check
            # # log_prob -= th.sum(th.log(1 - actions**2 + self.epsilon), dim=1)
        else:
            logp_pi = None

        pi_action = torch.tanh(pi_action) # squashing to -1,1
        pi_action = self.act_limit * pi_action # scale it back up to whatever was needed (if not -1,1)

        pi_action = pi_action.squeeze() #removes dimensions [[[[1]]]] --> 1

        return pi_action, logp_pi

    def act(self, obs, test=False):
        with torch.no_grad():
            #print(obs)
            a, _ = self.forward(obs, test, False)
            return a.cpu().numpy()


class MyCriticModule(nn.Module):
    def __init__(self, observation_space, action_space):
        super().__init__()
        self.net = VanillaCNN(q_net=True)

    def forward(self, obs, act):
        x = (*obs, act)
        q = self.net(x)
        return torch.squeeze(q, -1)  # Critical to ensure q has right shape.


class MyActorCriticModule(nn.Module):
    def __init__(self, observation_space, action_space):
        super().__init__()

        # build policy and value functions
        self.actor = MyActorModule(observation_space, action_space)
        self.q1 = MyCriticModule(observation_space, action_space)
        self.q2 = MyCriticModule(observation_space, action_space)

    def act(self, obs, test=False):
        with torch.no_grad():
            a, _ = self.actor(obs, test, False)
            return a.cpu().numpy()


def get_local_buffer_sample_imgs(prev_act, obs, rew, terminated, truncated, info):
    """
    Sample compressor for MemoryTMFull
    Input:
        prev_act: action computed from a previous observation and applied to yield obs in the transition
        obs, rew, terminated, truncated, info: outcome of the transition
    this function creates the object that will actually be stored in local buffers for networking
    this is to compress the sample before sending it over the Internet/local network
    buffers of such samples will be given as input to the append() method of the memory
    the user must define both this function and the append() method of the memory
    CAUTION: prev_act is the action that comes BEFORE obs (i.e. prev_obs, prev_act(prev_obs), obs(prev_act))
    """
    prev_act_mod = prev_act
    if MODEL_MODE == 0: #images[latest]
        obs_mod = ((obs[0][-1]).astype(np.uint8))    
       
    elif MODEL_MODE == 1: #rState0, eClutch1, eSpeed2, eBoost3, eGear4, vSpeed5, vSteer6, vDir7, vColl8, images[latest]
        obs_mod = (obs[0], obs[1], obs[2], obs[3], obs[4], obs[5], obs[6], obs[7], obs[8], (obs[9][-1]).astype(np.uint8))
    
    elif MODEL_MODE == 1.5: #eSpeed0, eBoost1, eGear2, vSpeed3, vSteer4, vDir5, vColl6, images[latest]
        obs_mod = (obs[0], obs[1], obs[2], obs[3], obs[4], obs[5], obs[6], (obs[7][-1]).astype(np.uint8))
    
    elif MODEL_MODE == 2:  #rState0, eClutch1, eSpeed2, eBoost3, eGear4, vSpeed5, vSteer6, vDir7, vColl8, rLeftSlip9, rRightSlip10, fLeftSlip11, fRightSlip12, fLWheel13, fRWheel14, rLWheel15, rRWheel16, images[latest] 
        obs_mod = (obs[0], obs[1], obs[2], obs[3], obs[4], obs[5], obs[6], obs[7], obs[8], obs[9], obs[10], obs[11], obs[12], obs[13], obs[14], obs[15], obs[16], (obs[17][-1]).astype(np.uint8))
    
    elif MODEL_MODE == 3:# rState0, eClutch1, eSpeed2, eBoost3, eGear4, vSpeed5, vSteer6, vDir7, cola8, colb9, colc10, cold11, rLeftSlip12, rRightSlip13, fLeftSlip14, fRightSlip15, fLWheel16, fRWheel17, rLWheel18, rRWheel19, images[latest]
        obs_mod = (obs[0], obs[1], obs[2], obs[3], obs[4], obs[5], obs[6], obs[7], obs[8], obs[9], obs[10], obs[11], obs[12], obs[13], obs[14], obs[15], obs[16], obs[17], obs[18], obs[19], (obs[20][-1]).astype(np.uint8))           
                  

    rew_mod = rew
    terminated_mod = terminated
    truncated_mod = truncated
    info_mod = info
    return prev_act_mod, obs_mod, rew_mod, terminated_mod, truncated_mod, info_mod

sample_compressor = get_local_buffer_sample_imgs
max_samples_per_episode = 10000000000

# Model files

my_run_name = "gt_stuff"
weights_folder = cfg.WEIGHTS_FOLDER

model_path = str(weights_folder / (my_run_name + ".tmod"))
model_path_history = str(weights_folder / (my_run_name + "_"))
model_history = -1 # save every n_th model


# --- Networking and files ---
weights_folder = cfg.WEIGHTS_FOLDER  # path to the weights folder
checkpoints_folder = cfg.CHECKPOINTS_FOLDER

model_path = str(weights_folder / (my_run_name + "_t.tmod"))
checkpoints_path = str(checkpoints_folder / (my_run_name + "_t.tcpt"))


# Memory:

from tmrl.memory import TorchMemory

def last_true_in_list(li):
    for i in reversed(range(len(li))):
        if li[i]:
            return i
    return None


def replace_hist_before_eoe(hist, eoe_idx_in_hist):
    """
    Pads the history hist before the End Of Episode (EOE) index.

    Previous entries in hist are padded with copies of the first element occurring after EOE.
    """
    last_idx = len(hist) - 1
    assert eoe_idx_in_hist <= last_idx, f"replace_hist_before_eoe: eoe_idx_in_hist:{eoe_idx_in_hist}, last_idx:{last_idx}"
    if 0 <= eoe_idx_in_hist < last_idx:
        for i in reversed(range(len(hist))):
            if i <= eoe_idx_in_hist:
                hist[i] = hist[i + 1]


class MyMemory(TorchMemory):
    def __init__(self,
                 memory_size=MEMORY_SIZE,
                 batch_size=BATCH_SIZE,
                 dataset_path="",
                 imgs_obs=4,
                 act_buf_len=ACT_BUF_LEN,
                 nb_steps=1,
                 sample_preprocessor: callable = None,
                 crc_debug=CRC_DEBUG,
                 device="cpu"):
        
        self.imgs_obs = imgs_obs
        self.act_buf_len = act_buf_len
        self.min_samples = max(self.imgs_obs, self.act_buf_len)
        self.start_imgs_offset = max(0, self.min_samples - self.imgs_obs)
        self.start_acts_offset = max(0, self.min_samples - self.act_buf_len)
        
        super().__init__(memory_size=memory_size,
                         batch_size=batch_size,
                         dataset_path=dataset_path,
                         nb_steps=nb_steps,
                         sample_preprocessor=sample_preprocessor,
                         crc_debug=crc_debug,
                         device=device)

    # def append_buffer(self, buffer):
    #     raise NotImplementedError

    def __len__(self):
        if len(self.data) == 0:
            return 0
        res = len(self.data[0]) - self.min_samples - 1
        if res < 0:
            return 0
        else:
            return res

    # def get_transition(self, item):
    #     raise NotImplementedError
    
    def get_transition(self, item):
        """
        CAUTION: item is the first index of the 4 images in the images history of the OLD observation
        CAUTION: in the buffer, a sample is (act, obs(act)) and NOT (obs, act(obs))
            i.e. in a sample, the observation is what step returned after being fed act (and preprocessed)
            therefore, in the RTRL setting, act is appended to obs
        So we load 5 images from here...
        Don't forget the info dict for CRC debugging
        """
        
        if self.data[4][item + self.min_samples - 1]:
            if item == 0:  # if fist item of the buffer
                item += 1
            elif item == self.__len__() - 1:  # if last item of the buffer
                item -= 1
            elif random.random() < 0.5:  # otherwise, sample randomly
                item += 1
            else:
                item -= 1
        
        idx_last = item + self.min_samples - 1
        idx_now = item + self.min_samples

        acts = self.load_acts(item)
        last_act_buf = acts[:-1]
        new_act_buf = acts[1:]

        imgs = self.load_imgs(item)
        imgs_last_obs = imgs[:-1]
        imgs_new_obs = imgs[1:]

        # if a reset transition has influenced the observation, special care must be taken
        if MODEL_MODE == 0:
            last_eoes = self.data[4][idx_now - self.min_samples:idx_now]  # self.min_samples values
        elif MODEL_MODE == 1:
            last_eoes = self.data[13][idx_now - self.min_samples:idx_now]  # self.min_samples values
        elif MODEL_MODE == 1.5:
            last_eoes = self.data[11][idx_now - self.min_samples:idx_now]  # self.min_samples values
        elif MODEL_MODE == 2:
            last_eoes = self.data[21][idx_now - self.min_samples:idx_now]  # self.min_samples values
        elif MODEL_MODE == 3:
            last_eoes = self.data[24][idx_now - self.min_samples:idx_now]  # self.min_samples values
        last_eoe_idx = last_true_in_list(last_eoes)  # last occurrence of True

        assert last_eoe_idx is None or last_eoes[last_eoe_idx], f"last_eoe_idx:{last_eoe_idx}"

        if last_eoe_idx is not None:
            replace_hist_before_eoe(hist=new_act_buf, eoe_idx_in_hist=last_eoe_idx - self.start_acts_offset - 1)
            replace_hist_before_eoe(hist=last_act_buf, eoe_idx_in_hist=last_eoe_idx - self.start_acts_offset)
            replace_hist_before_eoe(hist=imgs_new_obs, eoe_idx_in_hist=last_eoe_idx - self.start_imgs_offset - 1)
            replace_hist_before_eoe(hist=imgs_last_obs, eoe_idx_in_hist=last_eoe_idx - self.start_imgs_offset)

        if MODEL_MODE == 0:
            last_obs = (imgs_last_obs, *last_act_buf)
            new_act = self.data[1][idx_now]
            rew = np.float32(self.data[3][idx_now])
            new_obs = (imgs_new_obs, *new_act_buf)
            terminated = self.data[5][idx_now]
            truncated = self.data[6][idx_now]
            info = self.data[7][idx_now]     

        elif MODEL_MODE == 1:
            last_obs = (self.data[2][idx_last], self.data[3][idx_last], self.data[4][idx_last], 
                        self.data[5][idx_last], self.data[6][idx_last], self.data[7][idx_last], 
                        self.data[8][idx_last], self.data[9][idx_last], self.data[10][idx_last], 
                        imgs_last_obs, *last_act_buf)
            
            new_act = self.data[1][idx_now]
            rew = np.float32(self.data[12][idx_now])
            
            new_obs = (self.data[2][idx_now], self.data[3][idx_now], self.data[4][idx_now], 
                        self.data[5][idx_now], self.data[6][idx_now], self.data[7][idx_now], 
                        self.data[8][idx_now], self.data[9][idx_now], self.data[10][idx_now], 
                        imgs_new_obs, *new_act_buf)
            
            terminated = self.data[14][idx_now]
            truncated = self.data[15][idx_now]
            info = self.data[16][idx_now]
            
        elif MODEL_MODE == 1.5:
            last_obs = (self.data[2][idx_last], self.data[3][idx_last], self.data[4][idx_last], 
                        self.data[5][idx_last], self.data[6][idx_last], self.data[7][idx_last], 
                        self.data[8][idx_last],
                        imgs_last_obs, *last_act_buf)
            
            new_act = self.data[1][idx_now]
            rew = np.float32(self.data[11][idx_now])
            
            new_obs = (self.data[2][idx_now], self.data[3][idx_now], self.data[4][idx_now], 
                        self.data[5][idx_now], self.data[6][idx_now], self.data[7][idx_now], 
                        self.data[8][idx_now], 
                        imgs_new_obs, *new_act_buf)
            
            terminated = self.data[12][idx_now]
            truncated = self.data[13][idx_now]
            info = self.data[14][idx_now]                      
        
        elif MODEL_MODE == 2:
            last_obs = (self.data[2][idx_last], self.data[3][idx_last], self.data[4][idx_last], 
                        self.data[5][idx_last], self.data[6][idx_last], self.data[7][idx_last], 
                        self.data[8][idx_last], self.data[9][idx_last], self.data[10][idx_last],
                        self.data[11][idx_last], self.data[12][idx_last], self.data[13][idx_last], 
                        self.data[14][idx_last], self.data[15][idx_last], self.data[16][idx_last], 
                        self.data[17][idx_last], self.data[18][idx_last],  
                        imgs_last_obs, *last_act_buf)
            
            new_act = self.data[1][idx_now]
            rew = np.float32(self.data[20][idx_now])
            
            new_obs = (self.data[2][idx_now], self.data[3][idx_now], self.data[4][idx_now], 
                        self.data[5][idx_now], self.data[6][idx_now], self.data[7][idx_now], 
                        self.data[8][idx_now], self.data[9][idx_now], self.data[10][idx_now], 
                        self.data[11][idx_now], self.data[12][idx_now], self.data[13][idx_now], 
                        self.data[14][idx_now], self.data[15][idx_now], self.data[16][idx_now], 
                        self.data[17][idx_now], self.data[18][idx_now],  
                        imgs_new_obs, *new_act_buf)
            
            terminated = self.data[22][idx_now]
            truncated = self.data[23][idx_now]
            info = self.data[24][idx_now]        
            
        elif MODEL_MODE == 3:
            last_obs = (self.data[2][idx_last], self.data[3][idx_last], self.data[4][idx_last], 
                        self.data[5][idx_last], self.data[6][idx_last], self.data[7][idx_last], 
                        self.data[8][idx_last], self.data[9][idx_last], self.data[10][idx_last],
                        self.data[11][idx_last], self.data[12][idx_last], self.data[13][idx_last], 
                        self.data[14][idx_last], self.data[15][idx_last], self.data[16][idx_last], 
                        self.data[17][idx_last], self.data[18][idx_last], self.data[19][idx_last], 
                        self.data[20][idx_last], self.data[21][idx_last],
                        imgs_last_obs, *last_act_buf)
            
            new_act = self.data[1][idx_now]
            rew = np.float32(self.data[23][idx_now])
            
            new_obs = (self.data[2][idx_now], self.data[3][idx_now], self.data[4][idx_now], 
                        self.data[5][idx_now], self.data[6][idx_now], self.data[7][idx_now], 
                        self.data[8][idx_now], self.data[9][idx_now], self.data[10][idx_now], 
                        self.data[11][idx_now], self.data[12][idx_now], self.data[13][idx_now], 
                        self.data[14][idx_now], self.data[15][idx_now], self.data[16][idx_now], 
                        self.data[17][idx_now], self.data[18][idx_now], self.data[19][idx_now], 
                        self.data[20][idx_now], self.data[21][idx_now],
                        imgs_new_obs, *new_act_buf)
            
            terminated = self.data[25][idx_now]
            truncated = self.data[26][idx_now]
            info = self.data[27][idx_now]        
            
        return last_obs, new_act, rew, new_obs, terminated, truncated, info

    def load_imgs(self, item):
        if MODEL_MODE == 0:
            res = self.data[2][(item + self.start_imgs_offset):(item + self.start_imgs_offset + self.imgs_obs + 1)]
        elif MODEL_MODE == 1:
            res = self.data[11][(item + self.start_imgs_offset):(item + self.start_imgs_offset + self.imgs_obs + 1)]
        elif MODEL_MODE == 1.5:
            res = self.data[9][(item + self.start_imgs_offset):(item + self.start_imgs_offset + self.imgs_obs + 1)]
        elif MODEL_MODE == 2:
            res = self.data[19][(item + self.start_imgs_offset):(item + self.start_imgs_offset + self.imgs_obs + 1)]
        elif MODEL_MODE == 3:
            res = self.data[22][(item + self.start_imgs_offset):(item + self.start_imgs_offset + self.imgs_obs + 1)]
        return np.stack(res).astype(np.uint8)

    def load_acts(self, item):
        res = self.data[1][(item + self.start_acts_offset):(item + self.start_acts_offset + self.act_buf_len + 1)]
        return res
    
    def trim(self, to_trim, qty):
        print("to trim is..........", qty)
        for i in range(qty):
            self.data[i] = self.data[i][to_trim:]

    def append_buffer(self, buffer):
        """
        buffer is a list of samples ( act, obs, rew, terminated, truncated, info)
        don't forget to keep the info dictionary in the sample for CRC debugging
        """
        first_data_idx = self.data[0][-1] + 1 if self.__len__() > 0 else 0
        #rState, eClutch, eSpeed, eBoost, eGear, vSpeed, vSteer, vDir, vColl, images
        #0: action
        if MODEL_MODE==0:
            d0 = [first_data_idx + i for i,_ in enumerate(buffer.memory)]  # indexes
            d1 = [b[0] for b in buffer.memory]  # actions
            d2 = [b[1] for b in buffer.memory]  # image
            d3 = [b[2] for b in buffer.memory]  # rewards
            d4 = [b[3] or b[4] for b in buffer.memory]  # done
            d5 = [b[3] for b in buffer.memory]  # terminated
            d6 = [b[4] for b in buffer.memory]  # truncated
            d7 = [b[5] for b in buffer.memory]  # infos
            
            d_values = [d0, d1, d2, d3, d4, d5, d6, d7]
            if self.__len__() > 0:
                for i in range(len(d_values)):
                    self.data[i] += d_values[i]
            else:
                for d in d_values:
                    self.data.append(d)         

            to_trim = int(self.__len__() - self.memory_size)
            if to_trim > 0:
                self.trim(to_trim, len(d_values))
                
        elif MODEL_MODE==1.5:
            d0  = [first_data_idx + i for i, _ in enumerate(buffer.memory)]  # indexes
            d1  = [b[0] for b in buffer.memory]  # actions
            d2  = [b[1][0] for b in buffer.memory]  # eSpeed
            d3  = [b[1][1] for b in buffer.memory]  # eBoost
            d4  = [b[1][2] for b in buffer.memory]  # eGear
            d5  = [b[1][3] for b in buffer.memory]  # vSpeed
            d6  = [b[1][4] for b in buffer.memory]  # vSteer
            d7  = [b[1][5] for b in buffer.memory]  # vDir
            d8  = [b[1][6] for b in buffer.memory]  # vColl
            d9  = [b[1][7] for b in buffer.memory]  # image
            d10 = [b[2] for b in buffer.memory]  # rewards
            d11 = [b[3] or b[4] for b in buffer.memory]  # done
            d12 = [b[3] for b in buffer.memory]  # terminated
            d13 = [b[4] for b in buffer.memory]  # truncated
            d14 = [b[5] for b in buffer.memory]  # infos
            
            d_values = [d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14]
            if self.__len__() > 0:
                for i in range(len(d_values)):
                    self.data[i] += d_values[i]
            else:
                for d in d_values:
                    self.data.append(d)         
                    
            to_trim = int(self.__len__() - self.memory_size)
            if to_trim > 0:
                self.trim(to_trim, len(d_values))
            
        else: 
            d0 = [first_data_idx + i for i, _ in enumerate(buffer.memory)]  # indexes
            d1 = [b[0] for b in buffer.memory]  # actions
            d2 = [b[1][0] for b in buffer.memory]  # rState
            d3 = [b[1][1] for b in buffer.memory]  # eClutch
            d4 = [b[1][2] for b in buffer.memory]  # eSpeed
            d5 = [b[1][3] for b in buffer.memory]  # eBoost
            d6 = [b[1][4] for b in buffer.memory]  # eGear
            d7 = [b[1][5] for b in buffer.memory]  # vSpeed
            d8 = [b[1][6] for b in buffer.memory]  # vSteer
            d9 = [b[1][7] for b in buffer.memory]  # vDir
        
            if MODEL_MODE == 1:
                d10 = [b[1][8] for b in buffer.memory]  # vColl
                d11 = [b[1][9] for b in buffer.memory]  # image
                d12 = [b[2] for b in buffer.memory]  # rewards
                d13 = [b[3] or b[4] for b in buffer.memory]  # done
                d14 = [b[3] for b in buffer.memory]  # terminated
                d15 = [b[4] for b in buffer.memory]  # truncated
                d16 = [b[5] for b in buffer.memory]  # infos
                
                d_values = [d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16]
                if self.__len__() > 0:
                    for i in range(len(d_values)):
                        self.data[i] += d_values[i]
                else:
                    for d in d_values:
                        self.data.append(d)         

                to_trim = int(self.__len__() - self.memory_size)
                if to_trim > 0:
                    self.trim(to_trim, len(d_values))
                
            elif MODEL_MODE == 2:
                d10 = [b[1][8] for b in buffer.memory]  # vColl
                d11 = [b[1][9] for b in buffer.memory]  # Slip1
                d12 = [b[1][10] for b in buffer.memory]  # Slip2
                d13 = [b[1][11] for b in buffer.memory]  # Slip3
                d14 = [b[1][12] for b in buffer.memory]  # Slip4
                d15 = [b[1][13] for b in buffer.memory]  # contact
                d16 = [b[1][14] for b in buffer.memory]  # contact
                d17 = [b[1][15] for b in buffer.memory]  # contact
                d18 = [b[1][16] for b in buffer.memory]  # contact
                d19 = [b[1][17] for b in buffer.memory]  # image
                d20 = [b[2] for b in buffer.memory]  # rewards
                d21 = [b[3] or b[4] for b in buffer.memory]  # done
                d22 = [b[3] for b in buffer.memory]  # terminated
                d23 = [b[4] for b in buffer.memory]  # truncated
                d24 = [b[5] for b in buffer.memory]  # infos

                d_values = [d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16, d17, d18, d19, d20, d21, d22, d23, d24]
                if self.__len__() > 0:
                    for i in range(len(d_values)):
                        self.data[i] += d_values[i]
                    
                else:
                    for d in d_values:
                        self.data.append(d) 
    
                to_trim = int(self.__len__() - self.memory_size)
                if to_trim > 0:
                    self.trim(to_trim, len(d_values))
                
            elif MODEL_MODE == 3:
                d10 = [b[1][8] for b in buffer.memory]  # coll1
                d11 = [b[1][9] for b in buffer.memory]  # coll2
                d12 = [b[1][10] for b in buffer.memory]  # coll3
                d13 = [b[1][11] for b in buffer.memory]  # coll4
                d14 = [b[1][12] for b in buffer.memory]  # Slip1
                d15 = [b[1][13] for b in buffer.memory]  # Slip2
                d16 = [b[1][14] for b in buffer.memory]  # Slip3
                d17 = [b[1][15] for b in buffer.memory]  # Slip4
                d18 = [b[1][16] for b in buffer.memory]  # contact
                d19 = [b[1][17] for b in buffer.memory]  # contact
                d20 = [b[1][18] for b in buffer.memory]  # contact
                d21 = [b[1][19] for b in buffer.memory]  # contact
                d22 = [b[1][20] for b in buffer.memory]  # image <--- something wrong
                d23 = [b[2] for b in buffer.memory]  # rewards
                d24 = [b[3] or b[4] for b in buffer.memory]  # done
                d25 = [b[3] for b in buffer.memory]  # terminated
                d26 = [b[4] for b in buffer.memory]  # truncated
                d27 = [b[5] for b in buffer.memory]  # infos

                d_values = [d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16, d17, d18, d19, d20, d21, d22, d23, d24, d25, d26, d27]
                if self.__len__() > 0:
                    for i in range(len(d_values)):
                        self.data[i] += d_values[i]
                    
                else:
                    for d in d_values:
                        self.data.append(d) 
    
                to_trim = int(self.__len__() - self.memory_size)
                if to_trim > 0:
                    self.trim(to_trim, len(d_values))        

        return self


# Training agent:
import itertools

class MyTrainingAgent(TrainingAgent):
    model_nograd = cached_property(lambda self: no_grad(copy_shared(self.model)))

    def __init__(self,
                 observation_space=None,
                 action_space=None,
                 device=None,
                 model_cls=MyActorCriticModule,  # an actor-critic module, encapsulating our ActorModule
                 gamma=0.99,  # discount factor
                 polyak=0.995,  # exponential averaging factor for the target critic
                 alpha=ENTROPCOEFF,  # fixed (SAC v1) or initial (SAC v2) value of the entropy coefficient
                 lr_actor=  LR_ACT,  # learning rate for the actor
                 lr_critic= LR_CRIT,  # learning rate for the critic
                 lr_entropy=LR_ENTR,  # entropy autotuning coefficient (SAC v2)
                 learn_entropy_coef=LEARN_ENTROPY_COEF,  # if True, SAC v2 is used, else, SAC v1 is used
                 target_entropy=None):  # if None, the target entropy for SAC v2 is set automatically
        super().__init__(observation_space=observation_space,
                         action_space=action_space,
                         device=device)
        model = model_cls(observation_space, action_space)
        self.model = model.to(device)
        self.model_target = no_grad(deepcopy(self.model))
        self.gamma = gamma
        self.polyak = polyak
        self.alpha = alpha
        self.lr_actor = lr_actor
        self.lr_critic = lr_critic
        self.lr_entropy = lr_entropy
        self.learn_entropy_coef=learn_entropy_coef
        self.target_entropy = target_entropy
        self.q_params = itertools.chain(self.model.q1.parameters(), self.model.q2.parameters())
        self.pi_optimizer = Adam(self.model.actor.parameters(), lr=self.lr_actor)
        self.q_optimizer = Adam(self.q_params, lr=self.lr_critic)
        if self.target_entropy is None:
            self.target_entropy = -np.prod(action_space.shape).astype(np.float32)
        else:
            self.target_entropy = float(self.target_entropy)
        if self.learn_entropy_coef:
            self.log_alpha = torch.log(torch.ones(1, device=self.device) * self.alpha).requires_grad_(True)
            self.alpha_optimizer = torch.optim.Adam([self.log_alpha], lr=self.lr_entropy)
        else:
            self.alpha_t = torch.tensor(float(self.alpha)).to(self.device)

    def get_actor(self):
        return self.model_nograd.actor

    def train(self, batch):
        o, a, r, o2, d, _ = batch  # ignore the truncated signal
        pi, logp_pi = self.model.actor(o)
        loss_alpha = None
        if self.learn_entropy_coef:
            alpha_t = torch.exp(self.log_alpha.detach())
            loss_alpha = -(self.log_alpha * (logp_pi + self.target_entropy).detach()).mean()
        else:
            alpha_t = self.alpha_t
        if loss_alpha is not None:
            self.alpha_optimizer.zero_grad()
            loss_alpha.backward()
            self.alpha_optimizer.step()
        q1 = self.model.q1(o, a)
        q2 = self.model.q2(o, a)
        with torch.no_grad():
            a2, logp_a2 = self.model.actor(o2)
            q1_pi_targ = self.model_target.q1(o2, a2)
            q2_pi_targ = self.model_target.q2(o2, a2)
            q_pi_targ = torch.min(q1_pi_targ, q2_pi_targ)
            backup = r + self.gamma * (1 - d) * (q_pi_targ - alpha_t * logp_a2)
        loss_q1 = ((q1 - backup)**2).mean()
        loss_q2 = ((q2 - backup)**2).mean()
        loss_q = loss_q1 + loss_q2
        self.q_optimizer.zero_grad()
        loss_q.backward()
        self.q_optimizer.step()
        for p in self.q_params:
            p.requires_grad = False
        q1_pi = self.model.q1(o, pi)
        q2_pi = self.model.q2(o, pi)
        q_pi = torch.min(q1_pi, q2_pi)
        loss_pi = (alpha_t * logp_pi - q_pi).mean()
        self.pi_optimizer.zero_grad()
        loss_pi.backward()
        self.pi_optimizer.step()
        for p in self.q_params:
            p.requires_grad = True
        with torch.no_grad():
            for p, p_targ in zip(self.model.parameters(), self.model_target.parameters()):
                p_targ.data.mul_(self.polyak)
                p_targ.data.add_((1 - self.polyak) * p.data)
        ret_dict = dict(
            loss_actor=loss_pi.detach().item(),
            loss_critic=loss_q.detach().item(),
        )
        if self.learn_entropy_coef:
            ret_dict["loss_entropy_coef"] = loss_alpha.detach().item()
            ret_dict["entropy_coef"] = alpha_t.item()
        return ret_dict




from argparse import ArgumentParser, ArgumentTypeError
import logging
def main(args):
    # === Networking parameters ============================================================================================
    security = None
    password = cfg.PASSWORD

    server_ip = "192.168.188.86"
    server_port = 6666
    
    
    sample_compressor = get_local_buffer_sample_imgs
    max_samples_per_episode = 10000000000
    # RTGYM Env
    from myRTClass_tmrl_V4_5 import MyGranTurismoRTGYM, DEFAULT_CONFIG_DICT
    
    my_config = DEFAULT_CONFIG_DICT
    my_config["interface"] = MyGranTurismoRTGYM
    my_config["time_step_duration"] = 0.05
    my_config["start_obs_capture"] = 0.05
    my_config["time_step_timeout_factor"] = 1.0
    my_config["ep_max_length"] = maxEpLength
    my_config["act_buf_len"] = ACT_BUF_LEN  
    my_config["reset_act_buf"] = True
    my_config["benchmark"] = False
    my_config["benchmark_polyak"] = 0.2
    my_config["wait_on_done"]=False

    my_config["interface_kwargs"] = {
        'debugFlag': False, # do not use render() while True
        'controlMode' : CONTROL_MODE,
        'modelMode': MODEL_MODE,
        'imageWidth' : imgSize,
        'imageHeight' : imgSize,
        'carChoice' : CARCHOICE, # 0 is MR2, 1 is Supra, 2 is Civic
        'trackChoice' : 0, # 0 is HS, 1 is 400m
        'rewardMode' : 'complex'
    }
    
    if args.worker or args.test:
        if args.test:
            my_config["wait_on_done"]=True
            my_config["ep_max_length"]=np.inf

        # === Env Class
        env_cls = partial(GenericGymEnv, id="real-time-gym-v1", gym_kwargs={"config": my_config})
        actor_module_cls = partial(MyActorModule)
        # === Rollout Worker
        
        my_worker = RolloutWorker(
            env_cls=env_cls,
            actor_module_cls=actor_module_cls,
            sample_compressor=sample_compressor,
            device=worker_device,
            server_ip=server_ip,
            server_port=server_port,
            password=password,
            max_samples_per_episode=max_samples_per_episode,
            model_path=model_path,
            model_path_history=model_path_history,
            model_history=model_history,
            crc_debug=CRC_DEBUG,
            local_port=6666+args.worker_port,
            standalone=args.test)
        my_worker.run() 
        
    elif args.trainer:
        # === Server 
        my_server = Server(security=security, password=password, port=server_port)
        
        # === Trainer
        training_agent_cls = partial(MyTrainingAgent,
                             model_cls=MyActorCriticModule,
                             gamma=0.995,
                             polyak=0.995, 
                             #slow down for stability by stable Q(S2,a2*) [Target network]
                             alpha=0.01, #entropy coeff / exploration/random
                             lr_actor=1e-5,
                             lr_critic=5e-5,
                             lr_entropy=3e-4, # only for learn_entrop_coef is True
                             learn_entropy_coef=False,
                             target_entropy=-0.5) # only for learn_entrop_coef is True
        
        memory_cls = partial(MyMemory,
                            act_buf_len=ACT_BUF_LEN,
                            memory_size=MEMORY_SIZE,
                            batch_size=BATCH_SIZE,
                            )
        
        training_cls = partial(
            TorchTrainingOffline,
            env_cls=(obs_space, act_space), # to avoid instantiating an real env
            memory_cls=memory_cls,
            training_agent_cls=training_agent_cls,
            epochs=EPOCHS,
            rounds=rounds,
            steps=steps,
            update_buffer_interval=update_buffer_interval,
            update_model_interval=update_model_interval,
            max_training_steps_per_env_step=max_training_steps_per_env_step,
            start_training=start_training,
            device=device)

        my_trainer = Trainer(
            training_cls=training_cls,
            server_ip=server_ip,
            server_port=server_port,
            password=password,
            model_path=model_path,
            checkpoint_path=checkpoints_path) 
        
        if args.local:            
            my_trainer.run()
        else:
            my_trainer.run_with_wandb(entity=cfg.WANDB_ENTITY, project=cfg.WANDB_PROJECT, run_id=RUN_NAME, key=cfg.WANDB_KEY)
            
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--trainer', action='store_true', help='launches the trainer and server')
    parser.add_argument('--worker', action='store_true', help='launches a rollout worker')
    parser.add_argument('--worker_port', type=int, default=0, help='port for rollout worker')
    parser.add_argument('--local', action='store_true', help='trainer will not use wandb')
    parser.add_argument('--test', action='store_true', help='trainer in test mode')
    arguments = parser.parse_args()
    logging.info(arguments)
    main(arguments)            