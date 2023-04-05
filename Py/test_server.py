from serverClass import server
from time import sleep

serverS = server()
serverS.connect()
serverS.sendPong(2)
sleep(1)
serverS.receiveOneFrame() #1
serverS.receiveOneFrame()
serverS.receiveOneFrame()
serverS.receiveOneFrame() #4