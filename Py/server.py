import socket
import game_pb2 as Game

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

while True:
    # Wait for a connection
    print('waiting for a connection')
    sendData = 1
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        while True:
            dataPing = connection.recv(1).decode()
            print(dataPing)
            if dataPing == "P" :
                print("get")
                dataSize = connection.recv(6).decode()
                print("oh")
                dataSize = int(dataSize)
                print(dataSize)
                data = connection.recv(dataSize)
            if not dataPing:
                break

    finally:
        # Clean up the connection
        connection.close()
