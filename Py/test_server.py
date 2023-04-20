from serverClass import server
from time import sleep

serverS = server(debug=False)
serverS.connect()
serverS.reloadSave()
serverS.receiveOneFrame() #Display first screenshot
print(serverS.myData.VS.engSpeed)
print(serverS.myData.VS.engBoost)
print(serverS.myData.VS.engGear)
print(serverS.myData.VS.speed)
print(serverS.myData.VS.steer)
print(serverS.myData.VS.pos)
print(serverS.myData.VS.fLeftSlip)
print(serverS.myData.VS.fRighttSlip)
print(serverS.myData.VS.rLeftSlip)
print(serverS.myData.VS.rRightSlip)
print(serverS.myData.posVect)
print(serverS.pic.dtype)
serverS.receiveAllAlways()
