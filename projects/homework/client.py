import socket
import sys

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9889
done = False

filename = sys.argv[1]
fd = open(filename, 'rb')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))

while not done:
    buf = fd.read(2048)
    if len(buf) > 0:
        sock.send(buf)
    if len(buf) > 0 or len(buf) < 2048:
        done = True

fd.close()
sock.close()