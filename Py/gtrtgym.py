from rtgym import RealTimeGymInterface
from serverClass import server
from pygamepad import controlGamepad

class MyRealTimeInterface(RealTimeGymInterface):
    def __init__(self):
        from serverClass import server 
        self.server = server()
        self.display = None
        self.gamepad = None
        self.server = server()

    def startSession(self):
        self.server.connect()
        
    def init_control(self):
        import vgamepad as vg
        self.gamepad = vg.VDS4Gamepad()
    
    def send_control(self, control):
        controlGamepad(self.gamepad, control)
        
agent = MyRealTimeInterface()
agent.init_control()
agent.startSession()
print("woop")
# agent.server.startReceiving()
agent.send_control([1,0,1])
import time
time.sleep(0.15)
agent.send_control([1,0,1])