import socket

DEBUG = 500
counter = 0

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 9999)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

print('Trying to do Server Stuff!')

while True:
    # Wait for a connection
    print('waiting for a connection')
    counter = 0
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(2)
            if counter < DEBUG:
                sendData = 1
            else:
                sendData = 2
            counter += 1
            sendData = sendData.to_bytes(1, 'little')
            connection.send(sendData)
            # print('received {!r}'.format(data))
            print('received {!r}'.format(data))
            if not data:
                break

    finally:
        # Clean up the connection
        connection.close()
