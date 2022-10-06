import socket
import struct

SERVER_IP = ('', 9999)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(SERVER_IP)
sock.listen(5)
while True:
    cli_sock, cli_ip = sock.accept()
    print('connection connected...')
    databytes = cli_sock.recv(4)
    print(struct.unpack('>f', databytes)[0])
    cli_sock.send(databytes)
    sock.close()
    break
