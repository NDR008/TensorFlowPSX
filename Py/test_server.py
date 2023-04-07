from serverClass import server
from time import sleep

serverS = server(debug=True)
serverS.connect()
serverS.reloadSave()
serverS.receiveOneFrame() #Display first screenshot
serverS.receiveOneFrame() #Display second screenshot
serverS.receiveOneFrame()
serverS.receiveOneFrame() #Display fourth screenshot
serverS.receiveAllAlways()