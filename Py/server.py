import socket
import game_pb2 as Game
import numpy as np
from PIL import Image
import cv2

counter = 0

myData = Game.Screen()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 9999)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
print('Gran Turismo AI TCP Server')
checkNumberMessages = 0

def recvall(sock, expectedSize):
    # Helper function to recv expectedSize bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < expectedSize:
        packet = sock.recv(expectedSize - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def decode_img(screenData):
    size = (screenData.width, screenData.height)
    if screenData.bpp == 0:
        img = Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR;15', 0, 1)
        b, g, r = img.split()
        img = Image.merge("RGB", (r, g, b))
    elif screenData.bpp == 1:
        img = Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR;15', 0, 1)
    else:
        img = None
    return img

while True:
    # Wait for a connection
    print('waiting for a connection')
    sendData = 1
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        while True:
            ping = recvall(connection, 1)
            if ping is not None:
                ping = ping.decode()
            if ping == "P" :
                dataSize = recvall(connection, 4)
                dataSize = int.from_bytes(dataSize, 'little')
                myData.Clear()
                data = recvall(connection, dataSize)
                if data is not None:
                    myData.ParseFromString(data)
                    pic = decode_img(myData)
                    #print("pause")
                    #pic.show()
                    #print("pause")
                    
                # print(myData.bpp, myData.width, myData.height)
                # debug for checking if packets got lost
                # print(checkNumberMessages)
                # checkNumberMessages = checkNumberMessages + 1
            if not ping:
                break

    finally:
        # Clean up the connection
        connection.close()
        