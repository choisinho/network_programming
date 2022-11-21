import pyaudio
import cv2
import socket
import struct
import numpy as np
# pip install opencv-python
# pip install pyaudio


try:
    # 서버에 연결
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((socket.gethostbyname(socket.gethostname()), 9999))


    # 스피커 연결
    pa = pyaudio.PyAudio()
    stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, output=True, frames_per_buffer=8192)


    # 서버 소켓으로부터 size 크기의 바이트열을 받아오는 함수
    def full_recv(sock,size):
        a = sock.recv(size)
        while len(a) != size:
            a += sock.recv(size-len(a))
        return a


    # 실시간 통신 시작
    while True:
        # 오디오 데이터가 온 경우: b'\x01'
        # 카메라 데이터가 온 경우: b'\x02'
        rcvd_data = full_recv(sock,1)

        # 오디오 데이터가 왔다면 오디오로 출력
        if rcvd_data == b'\x01':
            size = struct.unpack('>I',full_recv(sock,4))[0]
            rcvd_data = full_recv(sock,size)
            stream.write(rcvd_data[:size])

        # 카메라 데이터가 왔다면 이미지로 출력
        elif rcvd_data == b'\x02':
            width, height = struct.unpack('>II',full_recv(sock,8))
            rcvd_data = full_recv(sock,width*height*3)
            cv2.imshow('hi', np.frombuffer(rcvd_data[:width*height*3],dtype='uint8').reshape((height,width,3)))
            if cv2.waitKey(1) == ord('q'):
                break
except KeyboardInterrupt:
    pass

sock.close()
cv2.destroyAllWindows()
stream.close()