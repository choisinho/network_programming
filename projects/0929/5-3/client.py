import socket
import struct
import time
import threading

comm_done = False

def transfer(*arg):
    global comm_done
    sock = arg[0]
    while not comm_done:
        msg = input('message : ')
        sock.send(msg.encode())
        if msg == 'exit':
            comm_done = True

def receiver(*arg):
    sock = arg[0]
    while not comm_done:
        bytesdata = sock.recv(1024)
        print(struct.unpack('>I', bytesdata)[0])

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))
print('connected....')
time.sleep(2)

while True:
    msg = input('message : ')
    sock.send(msg.encode())
    if msg == 'exit':
        break
    data = sock.recv(1024)
    print(data.decode())

snd_th = threading.Thread(target=transfer, args=(sock))
rcv_th = threading.Thread(target=receiver, args=(sock))

snd_th.join()
rcv_th.join()

sock.close()