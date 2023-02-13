import os
str = "protoc ./Py/game.proto --python_out=."
stream = os.popen(str)
output = stream.read()
output
