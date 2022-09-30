import socket
import time

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))
print('connected....')
time.sleep(2)
sock.send('good morning'.encode())
sock.close()