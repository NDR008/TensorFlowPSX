from serverClass import server
from time import sleep

# serverSession.startReceiving()
serverSession = server()
serverSession.connect()
serverSession.sendPong(2)
serverSession.receiveAllAlways()
# while True:
sleep(2)
for i in range(1,5):
    sleep(1)
    print(i)
    serverSession.receiveOneFrame()