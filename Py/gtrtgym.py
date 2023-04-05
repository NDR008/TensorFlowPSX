from myRTClass import MyRealTimeInterface
from threading import Thread
        
agent = MyRealTimeInterface()
agent.init_control()

import time, random

while False:
    agent.send_control([random.randint(0,5),random.randint(-5,1),random.randint(-1,1)])
    time.sleep(0.005)
