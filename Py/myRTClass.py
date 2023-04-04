from pygamepad import controlGamepad
from rtgym import RealTimeGymInterface
from serverClass import server 

class MyRealTimeInterface(RealTimeGymInterface):
    def __init__(self):
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