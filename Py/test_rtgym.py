from myRTClass import MyGranTurismoRTGYM
import numpy as np
import pprint

granTurismo = MyGranTurismoRTGYM(debugFlag=True)
granTurismo.init_control()
granTurismo.server.connect()
print(granTurismo.get_observation_space())
granTurismo.reset()
granTurismo.wait()
granTurismo.server.receiveOneFrame()