from rtgym import RealTimeGymInterface
from pygamepad import controlGamepad

class MyRealTimeInterface(RealTimeGymInterface):
    def __init__(self):
        from serverClass import server 
        self.server = server()
        self.display = None
        self.gamepad = None

    def startSession(self):
        self.server.connect()
        
    def init_control(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()
    
    def send_control(self, control):
        controlGamepad(self.gamepad, control)
        
agent = MyRealTimeInterface()
agent.init_control()

print("woop")

# agent.server.startReceiving()
import time, random
from serverClass import server 
while True:
    agent.send_control([random.randint(0,5),random.randint(-5,1),random.randint(-1,1)])
    time.sleep(0.005)
agent.send_control([1,0,1])