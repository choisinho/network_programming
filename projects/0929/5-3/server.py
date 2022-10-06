import socket
import struct

SERVER_IP = ('', 9999)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(SERVER_IP)
sock.listen(5)
while True:
    cli_sock, cli_ip = sock.accept()
    print('connection connected...')
    while True:
        msg = cli_sock.recv(1024)
        print(msg.decode())
        if msg.decode() == 'exit':
            break
        cli_sock.send(msg)
    sock.close()
    break
