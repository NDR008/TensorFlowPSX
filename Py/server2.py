import socket
import game_pb2 as Game
import numpy as np
from PIL import Image
import cv2
from time import time # for benchmarking
from enum import Enum

class messageState(Enum):
    mPing = 1 # expect a simple "P"
    mRecvHeader = 2 # header (which contains the size)
    mRecvSize = 3 # size of the data
    mRecvData = 4 # actual raw data

class server:
    def __init__(self, ip='localhost', port=9999):
        self.ip = ip
        self.port = port
        self.mState = messageState.mPing.name
        self.header = bytearray()
        self.mSize = bytearray()
        self.message = bytearray()
        self.part = bytearray()
        self.pic = None
        self.myData = Game.Observation()
        self.fullData = False
        self.connection = None
        self.clientAddress =  None
        self.excpt = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress =(self.ip, self.port)
        # self.sock.setblocking(False)
        self.sock.bind(serverAddress)
        self.sock.listen(1)
        print('starting up on {} port {}'.format(*serverAddress))
    
    def recvall(self, expectedSize):
        # Helper function to recv expectedSize bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < expectedSize:
            packet = self.connection.recv(expectedSize - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    
    def toNumpy(self, im):
        im.load()
        # unpack data
        tmpImage = Image._getencoder(im.mode, 'raw', im.mode)
        tmpImage.setimage(im.im)

        # NumPy buffer for the result
        shape, typestr = Image._conv_type_shape(im)
        data = np.empty(shape, dtype=np.dtype(typestr))
        mem = data.data.cast('B', (data.data.nbytes,))
        bufsize, s, offset = 65536, 0, 0
        while not s:
            l, s, d = tmpImage.encode(bufsize)
            mem[offset:offset + len(d)] = d
            offset += len(d)
        if s < 0:
            raise RuntimeError("encoder error %d in tobytes" % s)
        return data
    
    def decodeImg(self):
        size = (self.myData.SS.width, self.myData.SS.height)
        if self.myData.SS.bpp == 0:
            # not actually 16bpp... BGR555
            self.pic = self.toNumpy(Image.frombuffer("RGB", size, self.myData.SS.data, 'raw', 'BGR;15', 0, 1))
        elif self.myData.SS.bpp == 1:
            self.pic = self.toNumpy(Image.frombuffer("RGB", size, self.myData.SS.data, 'raw', 'BGR', 0, 1))
        else:
            print("no clue")
        
    def receive(self):
        #print((self.mState == messageState.mPing.name))
        try:
            if self.mState == messageState.mPing.name:
                self.buffer = self.recvall(1) # can be removed later
                self.mState = messageState.mRecvHeader.name     

            if self.mState == messageState.mRecvHeader.name:
                self.part = bytearray()
                if len(self.header) < 4:
                    self.part = self.connection.recv(4 - len(self.header))
                    self.header.extend(self.part)
                else:
                    self.mSize = int.from_bytes(self.header, 'little')
                    self.mState = messageState.mRecvData.name
                    
            if self.mState == messageState.mRecvData.name:
                self.part = bytearray()
                if len(self.message) < self.mSize:
                    self.part = self.connection.recv(self.mSize - len(self.message))
                    self.message.extend(self.part)
                else:
                    self.fullData = True
                    self.mState = messageState.mPing.name
                    self.myData.ParseFromString(self.message)
                    self.header = bytearray()
                    self.mSize = bytearray()
                    self.message = bytearray()
        except socket.error as e:
            self.excpt = True            


serverSession = server()
serverSession.connect()
print("wait for connection")
while True:
    serverSession.connection, serverSession.clientAddress = serverSession.sock.accept()
    serverSession.connection.setblocking(False)
    print('connection from', serverSession.clientAddress)
    while True:
        serverSession.receive()
        #print('GRRRRRRRRRR', self.mState, e)
        if serverSession.excpt and serverSession.fullData:
            serverSession.excpt = False
            serverSession.decodeImg()
            cv2.imshow('window', serverSession.pic)
            if cv2.waitKey(1) & 0xFF == ord('q'):
               cv2.destroyAllWindows()
                