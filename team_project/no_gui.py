import pyaudio
import cv2
import socket
import struct
import numpy as np
import tkinter
import threading
import time
# pip install opencv-python
# pip install pyaudio


pa = pyaudio.PyAudio()
connecting_event = threading.Event()


# 소켓 서버
def main_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(2)
    server_socket.bind((ip_entry.get(), 9999))
    server_socket.listen(1)
    while True:
        print('클라이언트 연결 시도중...')
        try:
            client_socket, address = server_socket.accept()
            break
        except TimeoutError:
            if (not connect_stopped_event.is_set()) or (not closed_event.is_set()):
                print('클라이언트 연결 시도 중단됨')
                server_socket.close()
                connect_stopped_event.set()
                closed_event.set()
                server_connect_button['state'] = tkinter.NORMAL
                client_connect_button['state'] = tkinter.NORMAL
                return
    print('클라이언트 연결됨')
    stop_connect_button['state'] = tkinter.DISABLED
    disconnect_button['state'] = tkinter.NORMAL
    send = threading.Thread(target=main_sender, args=(client_socket,))
    recv = threading.Thread(target=main_receiver, args=(client_socket,))
    send.start()
    recv.start()
    send.join()
    recv.join()
    print('클라이언트 연결 끊김')
    client_socket.close()
    server_socket.close()
    disconnected_event.set()
    closed_event.set()
    connecting_event.clear()
    server_connect_button['state'] = tkinter.NORMAL
    client_connect_button['state'] = tkinter.NORMAL
    disconnect_button['state'] = tkinter.DISABLED


# 소켓 클라이언트
def main_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        print('서버 연결 시도중...')
        try:
            sock.connect((ip_entry.get(), 9999))
            break
        except ConnectionRefusedError:
            if (not connect_stopped_event.is_set()) or (not closed_event.is_set()):
                print('서버 연결 시도 중단됨')
                sock.close()
                connect_stopped_event.set()
                closed_event.set()
                server_connect_button['state'] = tkinter.NORMAL
                client_connect_button['state'] = tkinter.NORMAL
                return
    print('서버 연결됨')
    stop_connect_button['state'] = tkinter.DISABLED
    disconnect_button['state'] = tkinter.NORMAL
    send = threading.Thread(target=main_sender, args=(sock,))
    recv = threading.Thread(target=main_receiver, args=(sock,))
    send.start()
    recv.start()
    send.join()
    recv.join()
    print('서버 연결 끊김')
    sock.close()
    disconnected_event.set()
    closed_event.set()
    connecting_event.clear()
    server_connect_button['state'] = tkinter.NORMAL
    client_connect_button['state'] = tkinter.NORMAL
    disconnect_button['state'] = tkinter.DISABLED



# sock.recv()로 size 크기의 바이트열을 받아오는 함수
def full_recv(sock,size):
    a = sock.recv(size)
    while len(a) != size:
        a += sock.recv(size-len(a))
    return a


# 소켓으로 데이터를 보내는 함수
def main_sender(sock):
    # 오디오 데이터 전송
    def audio_callback(in_data, frame_count, time_info, status):
        try:
            data_size = struct.pack('>I',len(in_data))
            sock.send(b'\x01'+data_size+in_data)
        except (ConnectionResetError, ConnectionAbortedError):
            pass
        return (None, pyaudio.paContinue)
    stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=8192, stream_callback=audio_callback)
    # 비디오 데이터 전송
    cap = cv2.VideoCapture(0)
    widthheight = struct.pack('>II',int(cap.get(3)),int(cap.get(4)))
    while disconnected_event.is_set() and closed_event.is_set():
        try:
            ret, frame = cap.read()
            if ret: sock.send(b'\x02'+widthheight+frame.tobytes())
        except (ConnectionResetError, ConnectionAbortedError):
            break
    # 통화 종료 시
    stream.close()
    cap.release()
    disconnected_event.clear()


# 소켓으로부터 데이터를 받는 함수
def main_receiver(sock):
    stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, output=True, frames_per_buffer=8192)
    while disconnected_event.is_set() and closed_event.is_set():
        try:
            # 연결 오류             : b''
            # 오디오 데이터가 온 경우: b'\x01'
            # 비디오 데이터가 온 경우: b'\x02'
            rcvd_data = sock.recv(1)
            if rcvd_data == b'': break

            # 오디오 데이터가 왔다면 오디오로 출력
            elif rcvd_data == b'\x01':
                size = struct.unpack('>I',full_recv(sock,4))[0]
                volume = 8
                rcvd_data = np.frombuffer(full_recv(sock,size), dtype=np.int16) * volume
                stream.write(rcvd_data.tobytes())

            # 비디오 데이터가 왔다면 이미지로 출력
            elif rcvd_data == b'\x02':
                width, height = struct.unpack('>II',full_recv(sock,8))
                rcvd_data = full_recv(sock,width*height*3)
                cv2.imshow('hi', np.frombuffer(rcvd_data[:width*height*3],dtype='uint8').reshape((height,width,3)))
                cv2.waitKey(1)

        except (ConnectionResetError, ConnectionAbortedError):
            break
    # 통화 종료 시
    stream.close()
    cv2.destroyAllWindows()
    disconnected_event.clear()






# 테스트용 GUI
root = tkinter.Tk()


# IP 입력란, 기본값은 이 컴퓨터의 아이피
ip_entry = tkinter.Entry(root)
ip_entry.pack()
ip_entry.insert(0,socket.gethostbyname(socket.gethostname()))


# 서버로서 연결 시도하는 버튼
def server_connect_button_callback():
    print('server_connect_button_callback')
    server_connect_button['state'] = tkinter.DISABLED
    client_connect_button['state'] = tkinter.DISABLED
    stop_connect_button['state'] = tkinter.NORMAL
    connecting_event.set()
    threading.Thread(target=main_server).start()
server_connect_button = tkinter.Button(root, text='연결(server)', command=server_connect_button_callback)
server_connect_button.pack()


# 클라이언트로서 연결 시도하는 버튼
def client_connect_button_callback():
    print('client_connect_button_callback')
    server_connect_button['state'] = tkinter.DISABLED
    client_connect_button['state'] = tkinter.DISABLED
    stop_connect_button['state'] = tkinter.NORMAL
    connecting_event.set()
    threading.Thread(target=main_client).start()
client_connect_button = tkinter.Button(root, text='연결(client)', command=client_connect_button_callback)
client_connect_button.pack()


# 연결 시도를 중단하는 버튼
def stop_connect_button_callback():
    print('stop_connect_button_callback')
    stop_connect_button['state'] = tkinter.DISABLED
    connect_stopped_event.clear()
connect_stopped_event = threading.Event()
connect_stopped_event.set()
stop_connect_button = tkinter.Button(root, text='연결 시도 중단', command=stop_connect_button_callback)
stop_connect_button.pack()
stop_connect_button['state'] = tkinter.DISABLED


# 화상통화를 끊는 버튼
def disconnect_button_callback():
    print('disconnect_button_callback')
    disconnect_button['state'] = tkinter.DISABLED
    disconnected_event.clear()
disconnected_event = threading.Event()
disconnected_event.set()
disconnect_button = tkinter.Button(root, text='통화 종료', command=disconnect_button_callback)
disconnect_button.pack()
disconnect_button['state'] = tkinter.DISABLED


# 닫기 버튼
def close_button_callback():
    print('close_button_callback')
    if connecting_event.is_set():
        closed_event.clear()
        closed_event.wait()
    root.destroy()
    exit()
closed_event = threading.Event()
closed_event.set()
root.protocol("WM_DELETE_WINDOW", close_button_callback)



root.mainloop()