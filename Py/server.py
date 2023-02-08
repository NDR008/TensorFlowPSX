import socket
import game_pb2 as Game
import numpy as np
from PIL import Image
import cv2
from time import time # for benchmarking
import os


def recvall(sock, expectedSize):
    # Helper function to recv expectedSize bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < expectedSize:
        packet = sock.recv(expectedSize - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

global ReceiveState # 0 = init, 1 = receiving header, 2 = receiving data, 3 = all data is there
global Header
global MessageSize
global Message

def recv_partial(sock, ReceiveState, Header, MessageSize, Message):
    if ReceiveState == 0:
        ping = recvall(sock, 1) # can be removed later
        ReceiveState = 1
        Header = bytearray()
        Message = bytearray()

    elif ReceiveState == 1:
        stream = bytearray()
        if len(Header) < 4:
            stream = sock.recv(4 - len(Header))
            Header.extend(stream)
        else:
            MessageSize = int.from_bytes(Header, 'little')
            Header = bytearray()
            ReceiveState = 2
    elif ReceiveState == 2:
        stream = bytearray()
        if len(Message) < MessageSize:
            stream = sock.recv(MessageSize - len(Message))
            Message.extend(stream)
        else:
            ReceiveState = 3
            
    return sock, ReceiveState, Header, MessageSize, Message
            
    # Helper function to recv expectedSize bytes or return None if EOF is hit


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
        return to_numpy(Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR;15', 0, 1))
    elif screenData.bpp == 1:
        return to_numpy(Image.frombuffer("RGB", size, screenData.data, 'raw', 'BGR', 0, 1))
    else:
        return None

def sock_init():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 9999)
    print('starting up on {} port {}'.format(*server_address))
    # Listen for incoming connections
    sock.setblocking(0)
    sock.settimeout(5) 
    sock.bind(server_address)
    sock.listen(1)
    return sock

counter = 0

myScreen = Game.Screen()
myGS = Game.GameState()
myVS = Game.Vehicle()
myData = Game.Observation()

pic = None

# Create a TCP/IP socket

print('Gran Turismo AI TCP Server')
sock = sock_init()
checkNumberMessages = 0

ReceiveState = 0 # 1: receiving size, 2: receiving data
Header = bytearray()
MessageSize = 0
Message = bytearray()
    
while True:
    # Wait for a connection
    print('waiting for a connection for 5s')
    sendData = 1
    try:
        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)
            start_time = time()
            a = 0
            while True:
                sock, ReceiveState, Header, MessageSize, Message = recv_partial(connection, ReceiveState, Header, MessageSize, Message)
                if ReceiveState == 3:
                    myData.ParseFromString(Message)
                    pic = decode_img(myData.SS)
                    ReceiveState = 0
                if pic is not None: 
                    cv2.imshow('window', pic)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()

        finally:
            # Clean up the connection
            connection.close()
    except socket.timeout:
        print("Nobody loves me")
        break
