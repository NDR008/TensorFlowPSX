from serverClass import server
from time import sleep

serverS = server()
serverS.connect()
serverS.sendPong(2)
#serverS.receiveAllAlways()
serverS.receiveOneFrame()
serverS.receiveOneFrame()
serverS.receiveOneFrame()
serverS.receiveOneFrame()