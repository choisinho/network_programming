import socket
import threading

def filesave(*arg):
    done = False
    cli_sock = arg[0]
    fd = open('file.dat', 'wb')
    while not done:
        buf = cli_sock.recv(2048)
        fd.write(buf)
        if len(buf) < 2048:
            done = True
            fd.close()
            cli_sock.close()

SERVER_PORT = 9889
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', SERVER_PORT))
sock.listen(5)
cli_sock, _ = sock.accept()
th = threading.Thread(target=filesave, args=(cli_sock,))
th.start()
sock.close()
print('connection closed')