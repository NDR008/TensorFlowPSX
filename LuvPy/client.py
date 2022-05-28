import socket

# Note that the server may listen on a specific address or any address
# (signified by the empty string), but the client must specify an address to
# connect to. Here, we're connecting to the server on the same machine
# (127.0.0.1 is the "loopback" address).
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 10100

# Create the socket
c = socket.socket()

# Connect to the server. A port for the client is automatically allocated
# and bound by the operating system
c.connect((SERVER_ADDRESS, SERVER_PORT))

# Compatibility hack. In python3, input receives data from standard input. In
# python2, raw_input does exactly that, whereas input receives data, then
# "evaluates" the result; we don't want to do that. So on python2, overwrite
# the input symbol with a reference to raw_input. On python3, trap the
# exception and do nothing.
# try:
#     input = raw_input
# except NameError:
#     pass

print("Connected to " + str((SERVER_ADDRESS, SERVER_PORT)))
while True:
    try:
        data = input("Enter some data: ")
    except EOFError:
        print("\nOkay. Leaving. Bye")
        break

    if not data:
        print("Can't send empty string!")
        print("Ctrl-D [or Ctrl-Z on Windows] to exit")
        continue

    # Convert string to bytes. (No-op for python2)
    data = data.encode()

    # Send data to server
    c.send(data)

    # Receive response from server
    data = c.recv(2048)
    if not data:
        print("Server abended. Exiting")
        break

    # Convert back to string for python3
    data = data.decode()

    print("Got this string from server:")
    print(data + '\n')

c.close()
