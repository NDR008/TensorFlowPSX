import socket
import game_pb2 as Game
import numpy as np
from PIL import Image
import cv2
from time import process_time_ns, time # for benchmarking
import os

counter = 0

myScreen = Game.Screen()
myGS = Game.GameState()
myVS = Game.Vehicle()

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

def to_numpy(im):
    im.load()
    # unpack data
    e = Image._getencoder(im.mode, 'raw', im.mode)
    e.setimage(im.im)

    # NumPy buffer for the result
    shape, typestr = Image._conv_type_shape(im)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        l, s, d = e.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise RuntimeError("encoder error %d in tobytes" % s)
    return data

def decode_img(screenData):
    size = (screenData.width, screenData.height)
    if screenData.bpp == 0:
        # not actually 16bpp... BGR555
        # return np.asarray(Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR;15', 0, 1))
        return to_numpy(Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR;15', 0, 1))
    elif screenData.bpp == 1:
        # return np.asarray(Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR', 0, 1)) 
        return to_numpy(Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR', 0, 1))
    else:
        return None

while True:
    # Wait for a connection
    print('waiting for a connection')
    sendData = 1
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        start_time = time()
        a = 0
        while True:
            ping = recvall(connection, 1)
            if ping is not None:
                ping = ping.decode()
            if ping == "P" :
                dataSize = recvall(connection, 4)
                dataSize = int.from_bytes(dataSize, 'little')
                myScreen.Clear()
                screenData = recvall(connection, dataSize)
                if screenData is not None:
                    myScreen.ParseFromString(screenData)
                    pic = decode_img(myScreen)
                    if True:
                        cv2.imshow('window', pic)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            break
                
                dataSize = recvall(connection, 4)
                dataSize = int.from_bytes(dataSize, 'little')
                myGS.Clear()
                gsData = recvall(connection, dataSize)
                if screenData is not None:
                    myGS.ParseFromString(gsData)

                
                ping = recvall(connection, 1)
                if ping is not None:
                    ping = ping.decode()
                if ping == "R" :
                    dataSize = recvall(connection, 4)
                    dataSize = int.from_bytes(dataSize, 'little')
                    myVS.Clear()
                    vsData = recvall(connection, dataSize)
                    if screenData is not None:
                        myVS.ParseFromString(vsData)
                        os.system('cls')
                        print(myVS)
                
                if True and a == 500:
                    end_time = time()
                    print (500/(end_time - start_time))
                a += 1    
            if not ping:
                break

    finally:
        # Clean up the connection
        connection.close()
        