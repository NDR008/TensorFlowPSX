from myRTClass import MyGranTurismoRTGYM
import numpy as np
import pprint

granTurismo = MyGranTurismoRTGYM(debugFlag=True)
granTurismo.inititalizeCommon()
print(granTurismo.get_observation_space())
granTurismo.reset()
granTurismo.wait()
granTurismo.server.receiveOneFrame()