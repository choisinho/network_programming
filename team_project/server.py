import pyaudio
import cv2
import socket
import struct
# pip install opencv-python
# pip install pyaudio


try:
    # 클라이언트에 연결
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(10)
    server_socket.bind(('', 9999))
    server_socket.listen(1)
    client_socket, address = server_socket.accept()


    # 마이크 연결
    pa = pyaudio.PyAudio()
    def callback(in_data, frame_count, time_info, status):
        data_size = struct.pack('>I',len(in_data))
        # 음성 데이터를 클라이언트로 전송
        client_socket.send(b'\x01'+data_size+in_data)
        return (None, pyaudio.paContinue)
    stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=8192, stream_callback=callback)


    # 카메라 연결
    cap = cv2.VideoCapture(0)
    width, height = int(cap.get(3)), int(cap.get(4))
    while(True):
        ret, frame = cap.read()
        if ret:
            # 카메라 데이터를 클라이언트로 전송
            client_socket.send(b'\x02'+struct.pack('>II',width,height)+frame.tobytes())
except KeyboardInterrupt:
    pass

cap.release()
stream.close()
client_socket.close()
server_socket.close()