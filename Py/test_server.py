from serverClass import server
from time import sleep

serverS = server()
serverS.connect()
serverS.sendPong(2) # loads the save state
serverS.receiveOneFrame() #Display first screenshot
serverS.receiveOneFrame() #Display second screenshot
serverS.receiveOneFrame()
serverS.receiveOneFrame() #Display fourth screenshot
serverS.receiveAllAlways()