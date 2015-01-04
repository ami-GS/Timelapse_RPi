import socket

WIDTH = 480 #2592 # max
HEIGHT = 360 #1944 # max
ZFILL = 7
ENCODEFPS = 25
PORT = 8080 # here should be change dynamically
HOST = socket.gethostname() # here also
if not HOST.count('.local'):
    HOST += '.local' # for my environment (local)
