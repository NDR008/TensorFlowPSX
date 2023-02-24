from rtgym import RealTimeGymInterface
import server
from pygamepad import controlGamepad

class MyRealTimeInterface(RealTimeGymInterface):
    
    def __init__(self, img_hist_len: int = 4,
                 gamepad: bool = False,
                 min_nb_steps_before_failure: int = int(3.5 * 20),
                 display: bool = False,
                 grayscale: bool = False,
                 resize_to=(64, 64),
                 finish_reward=200,
                 constant_penalty=0):
        self.last_time = None
        self.img_hist_len = img_hist_len
        self.img_hist = None
        self.img = None
        self.reward_function = None
        self.server = None
        self.display = display
        self.gamepad = gamepad
        self.j = None
        self.window_interface = None
        self.small_window = None
        self.min_nb_steps_before_failure = min_nb_steps_before_failure
        self.grayscale = grayscale
        self.resize_to = resize_to
        self.finish_reward = finish_reward
        self.constant_penalty = constant_penalty

    def startSession(self, server):
        self.server = server
        self.server.connect()
    
    def send_control(self, control):
        controlGamepad(control)
        
agent = MyRealTimeInterface()
thisServer = server()
agent.startSession(server)