import socket
import game_pb2 as Game
import numpy as np
from PIL import Image
import cv2
from time import sleep, time # for benchmarking
from enum import Enum
from threading import Thread

class messageState(Enum):
    mPing = 1 # expect a simple "P"
    mRecvHeader = 2 # header (which contains the size)
    mRecvSize = 3 # size of the data
    mRecvData = 4 # actual raw data

class server(Thread):
    def __init__(self, ip='localhost', port=9999):
        """Returns a GT AI server object
        Parameters:
        ip is a hostname as string (default localhost)
        port as int (default 9999)
        benchmark true / false (default false) * checks fps
        """
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.mState = messageState.mPing.name
        self.header = bytearray()
        self.mSize = bytearray()
        self.message = bytearray()
        self.pic = None
        self.myData = Game.Observation()
        self.fullData = False
        self.connection = None
        self.clientAddress =  None
        self.excpt = False
        self.lostComms = 0
        self.buffer = None
        self.lastFrame = 0
        print("GT AI Server instantiated for rtgym")

    def receiveClient(self):
        print("Waiting for a connection")
        self.connection, self.clientAddress = self.sock.accept()
        self.connection.setblocking(False)

    def startServer(self):
        """Starts up the server ready for a single connection
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress =(self.ip, self.port)
        # self.sock.setblocking(False)
        self.sock.bind(serverAddress)
        self.sock.listen(1)
        print('starting up on {} port {}'.format(*serverAddress))

    
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
        """Protobuf decoding of the screen shot and converts into an numpy array
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
        try:
            if self.mState == messageState.mPing.name:
                self.buffer = self.recvall(1) # can be removed later           
                if self.buffer is not None and self.buffer.decode() == 'P':
                    self.lostComms = False
                    self.mState = messageState.mRecvHeader.name
                else:
                    self.lostComms = True

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
                    pong = 1
                    self.connection.send(pong.to_bytes(4,'little'))
        except socket.error as e:
            self.excpt = True            

    # rename startReceiving to run for threading
    def run(self):
        self.startServer()
        self.receiveClient()
        # while True:
        if not (self.excpt and self.fullData):
            try:
                print('Connection from', self.clientAddress)
                while not self.fullData:
                    self.receive()
                    if self.lostComms:
                        break

                    if self.excpt and self.fullData:
                        self.decodeImg()
                        size = self.pic.shape
                        self.pic = cv2.resize(self.pic, (size[1]*2,size[0]*2))
                        cv2.imshow('window', self.pic)
                        if self.lastFrame != self.myData.frame:
                            self.lastFrame = self.myData.frame
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                cv2.destroyAllWindows()
                                print('Forced Exit')
                                self.connection.close()  
                                break
            finally:
                # Clean up the connection
                self.excpt = False
                #print('Connection closed')
                #cv2.destroyAllWindows()
                self.connection.close()            
                self.lostComms = False
                

#serverSession = server(benchmark=True)
#serverSession.startReceiving()
serverSession = server()
serverSession.run()