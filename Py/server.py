import socket

counter = 0

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 9999)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
print('Gran Turismo AI TCP Server')

while True:
    # Wait for a connection
    print('waiting for a connection')
    sendData = 1
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        while True:
            recvDataTick = connection.recv(2).decode()
            if recvDataTick == "Ti":
                recvChunks = int(connection.recv(1).decode())
                print(recvChunks)
                
                for i in range(0,recvChunks):
                    recvDataType = connection.recv(1).decode()
                    if recvDataType == "I":
                        recvDataSize = int(connection.recv(1).decode())
                        recvData = connection.recv(recvDataSize)
                        print("Int", recvDataTick, recvDataType, recvDataSize, recvData.decode())
                    elif recvDataType == "A":
                        recvDataSize = int(connection.recv(1).decode())
                        recvData = connection.recv(recvDataSize)
                        recvData = recvData.decode()

                        print(recvData)
                        # for row in range (0, recvDataHeight):
                        #     recvDataSize = int(connection.recv(1).decode())
                        #     recvDataHeight = connection.recv(recvDataSize)
                        #     recvDataHeight = recvDataHeight.decode()
                        #     recvDataHeight = int(recvDataHeight)
                        print("Array", recvDataTick, recvDataType, recvData)
                connection.send(sendData.to_bytes(1, 'little'))
                counter = counter + 1
            if not recvDataTick:
                break

    finally:
        # Clean up the connection
        print(counter)
        connection.close()
