import socket
import game_pb2 as Game
import numpy as np
from PIL import Image
import cv2
from time import sleep, time
from enum import Enum


class messageState(Enum):
    mPing = 1  # expect a simple "P"
    mRecvHeader = 2  # header (which contains the size)
    mRecvSize = 3  # size of the data
    mRecvData = 4  # actual raw data


class server():
    def __init__(self, ip='localhost', port=9999, debug=False):
        """Returns a GT AI server object
        Parameters:
        ip is a hostname as string (default localhost)
        port as int (default 9999)
        benchmark true / false (default false) * checks fps
        """
        self.debug = debug
        self.ip = ip
        self.port = port
        self.mState = messageState.mPing.name
        self.header = bytearray()
        self.mSize = 0
        self.message = bytearray()
        self.pic = None
        self.myData = Game.Observation()
        self.fullData = False
        self.connection = None
        self.clientAddress = None
        self.excpt = False
        self.lostPing = 0
        self.buffer = None
        self.lastFrame = 0
        self.sock = None
        print("GT AI Server instantiated for rtgym")

    def connect(self):
        """Starts up the server ready for a single connection
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (self.ip, self.port)
        self.sock.setblocking(True)
        self.sock.bind(serverAddress)
        self.sock.listen(1)
        print('starting up on {} port {}'.format(*serverAddress))
        self.receiveClient()
        # self.lostPing = False

    def recvall(self, expectedSize):
        """Returns an expected number of bytes from the socket connection
        This function will not return until all the data has been received
        """
        data = bytearray()
        while len(data) < expectedSize:
            packet = self.connection.recv(expectedSize - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def toNumpy(self, im):
        """This function converts a PIL image into a a numpy array
        """
        im.load()
        # unpack data
        tmpImage = Image._getencoder(im.mode, 'raw', im.mode)
        tmpImage.setimage(im.im)

        # NumPy buffer for the result
        shape, typestr = Image._conv_type_shape(im)
        #data = np.empty(shape, dtype=np.dtype(typestr))
        data = np.empty(shape, dtype='uint8')
        mem = data.data.cast('B', (data.data.nbytes,))
        buffSize, s, offset = 65536, 0, 0
        while not s:
            l, s, d = tmpImage.encode(buffSize)
            mem[offset:offset + len(d)] = d
            offset += len(d)
        if s < 0:
            raise RuntimeError("encoder error %d in tobytes" % s)
        return data

    def decodeImg(self):
        """Protobuf decoding of the screenshot and converts into an numpy array
        """
        size = (self.myData.SS.width, self.myData.SS.height)
        if self.myData.SS.bpp == 0:
            # not actually 16bpp... BGR555
            self.pic = self.toNumpy(Image.frombuffer("RGB", size, self.myData.SS.data, 'raw', 'BGR;15', 0, 1))
        elif self.myData.SS.bpp == 1:
            self.pic = self.toNumpy(Image.frombuffer("RGB", size, self.myData.SS.data, 'raw', 'BGR', 0, 1))
        else:
            print("no clue what to do with this image")

    def receive(self):
        """this function will receive as much data as possible
        and if possible decode it
        """
        self.part = bytearray()
        try:
            if self.mState == messageState.mPing.name:
                self.buffer = self.recvall(1)  # can be removed later
                if self.buffer is not None and self.buffer.decode() == 'P':
                    self.lostPing = False
                    self.mState = messageState.mRecvHeader.name
                else:
                    self.lostPing = True

            if self.mState == messageState.mRecvHeader.name:
                self.part.clear()
                if len(self.header) < 4:
                    self.part = self.connection.recv(4 - len(self.header))
                    self.header.extend(self.part)
                else:
                    self.mSize = int.from_bytes(self.header, 'little')
                    self.mState = messageState.mRecvData.name

            if self.mState == messageState.mRecvData.name:
                self.part.clear()
                if len(self.message) < self.mSize:
                    self.part = self.connection.recv(self.mSize - len(self.message))
                    self.message.extend(self.part)
                else:
                    self.buffer = self.recvall(1)  # can be removed later
                    if self.buffer is not None and self.buffer.decode() == 'D':
                        self.fullData = True
                        self.mState = messageState.mPing.name
                        self.myData.ParseFromString(self.message)
                        self.header.clear()
                        self.message.clear()
        except socket.error as e:
            self.excpt = True

    def sendPong(self, pong):
        self.connection.send(pong.to_bytes(4, 'little'))

    def receiveClient(self):
        print("Waiting for a connection")
        self.connection, self.clientAddress = self.sock.accept()
        self.connection.setblocking(False)
        print('Connection from', self.clientAddress)

    # rename startReceiving to run for threading
    def receiveAllAlways(self):
        while True:
            try:
                self.sendPong(1)
                self.receive()
                if self.excpt and self.fullData:
                    self.excpt = False
                    self.fullData = False
                    self.decodeImg()
                    if self.debug:
                        #size = self.pic.shape
                        #self.pic = cv2.resize(self.pic, (size[1] * 2, size[0] * 2), interpolation=cv2.INTER_NEAREST)
                        cv2.imshow('Preview Display', self.pic)
                        self.lastFrame = self.myData.frame
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            print('Forced Exit')
                            return
            except:
                print("lost")
                return
            
    def receiveOneFrame(self):
        self.sendPong(1)
        while True:
            try:
                self.receive()
                if self.excpt and self.fullData:
                    self.excpt = False
                    self.fullData = False
                    self.decodeImg()
                    
                    self.lastFrame = self.myData.frame
                    #size = self.pic.shape
                    #self.pic = cv2.resize(self.pic, (size[1] * 2, size[0] * 2), interpolation=cv2.INTER_NEAREST)
                    if self.debug:
                        cv2.imshow('Preview Display', self.pic)                   
                        if cv2.waitKey(0) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            print('Forced Exit')
                            return
                    else:
                        return
            except:
                print("Exception on single frame")
                return
            
    def reloadSave(self, trackChoice):
        print("reload save for track :", trackChoice)
        self.sendPong(trackChoice) # loads the save state
        sleep(0.5)        