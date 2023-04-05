from serverClass import server
from time import sleep

serverS = server(debug=True)
serverS.connect()
serverS.sendPong(2) # loads the save state
sleep(1)
serverS.receiveOneFrame() #Display first screenshot
serverS.receiveOneFrame() #Display second screenshot
serverS.receiveOneFrame()
serverS.receiveOneFrame() #Display fourth screenshot
serverS.receiveAllAlways()