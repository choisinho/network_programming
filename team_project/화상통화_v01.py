import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
from tkinter import *
from tkinter.messagebox import askyesno
import socket
import pyaudio
import struct
import numpy as np
import threading
DEBUG = True
pa = pyaudio.PyAudio()



class App:

    def __init__(self, window, window_title, video_source=0):
        self.window=window
        self.window.title=(window_title)
        self.video_source=video_source

        self.vid= MyVideoCapture(self.video_source)
        self.canvas=tkinter.Canvas(window, width=self.vid.width, height =  self.vid.height)
        self.canvas.pack()


        btn_frame=tkinter.Frame(window, background=self.from_rgb((117, 123, 129)))
        btn_frame.place(x=0,y=0, anchor="nw", width=self.vid.width+4)

        self.btn_input=tkinter.Entry(btn_frame, width=15,bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_input.pack(side="left", padx=10, pady=10)
  
        self.btn_myip=tkinter.Button(btn_frame, text=socket.gethostbyname(socket.gethostname()),width=10, command=None, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_myip.pack(side="left", padx=10, pady=10)
        self.btn_myip['state'] = tkinter.DISABLED


        # 서버로서 연결 시도하는 버튼
        def btn_server_callback():
            if DEBUG==True: print('btn_server_callback')
            if self.check_ip(self.btn_input.get()):
                self.btn_server['state'] = tkinter.DISABLED # 연결버튼 비활성화
                self.btn_client['state'] = tkinter.DISABLED # 연결버튼 비활성화
                self.btn_kill['state'] = tkinter.NORMAL # 연결시도 중단 버튼 활성화
                self.waiting_or_connected_event.set()
                threading.Thread(target=self.main_server).start() # main_server 함수로
        self.btn_server=tkinter.Button(btn_frame, text="server연결", width=10, command=btn_server_callback, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_server.pack(side="left", padx=10, pady=10)


        # 클라이언트로서 연결 시도하는 버튼
        def btn_client_callback():
            if DEBUG==True: print('btn_client_callback')
            if self.check_ip(self.btn_input.get()):
                self.btn_server['state'] = tkinter.DISABLED # 연결버튼 비활성화
                self.btn_client['state'] = tkinter.DISABLED # 연결버튼 비활성화
                self.btn_kill['state'] = tkinter.NORMAL # 연결시도 중단 버튼 활성화
                self.waiting_or_connected_event.set()
                threading.Thread(target=self.main_client).start() # main_client 함수로
        self.btn_client=tkinter.Button(btn_frame, text="client연결", width=10, command=btn_client_callback, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_client.pack(side="left", padx=10, pady=10)
  
  
        # 연결 시도를 중단하는 버튼
        def btn_kill_callback():
            if DEBUG==True: print('btn_kill_callback')
            self.btn_kill['state'] = tkinter.DISABLED # 연결시도 중단 버튼 비활성화
            self.connect_stopped_event.clear()
        self.connect_stopped_event = threading.Event()
        self.connect_stopped_event.set()
        self.btn_kill=tkinter.Button(btn_frame, text="연결 시도 중단", width=10, command=btn_kill_callback, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_kill.pack(side="left", padx=10, pady=10)
        self.btn_kill['state'] = tkinter.DISABLED
  

        # 화상통화를 끊는 버튼
        def btn_exit_callback():
            if DEBUG==True: print('btn_exit_callback')
            self.btn_exit['state'] = tkinter.DISABLED # 통화종료 버튼 비활성화
            self.disconnected_event.clear()
        self.disconnected_event = threading.Event()
        self.disconnected_event.set()
        self.btn_exit=tkinter.Button(btn_frame, text="통화 종료", width=10, command=btn_exit_callback, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_exit.pack(side="right", padx=10, pady=10)
        self.btn_exit['state'] = tkinter.DISABLED


        # 닫기 버튼
        def window_close_callback():
            if DEBUG==True: print('window_close_callback')
            if self.waiting_or_connected_event.is_set():
                self.window_close_event.clear()
                self.window_close_event.wait()
            self.window.destroy()
            exit()
        self.waiting_or_connected_event = threading.Event()
        self.window_close_event = threading.Event()
        self.window_close_event.set()
        self.window.protocol("WM_DELETE_WINDOW", window_close_callback)

        self.show_other_video = False

        self.delay=15
        self.update()

        self.window.mainloop()




    def update(self):
        if self.show_other_video == False:
            ret, frame=self.vid.get_frame()
            if ret:
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0,0, image=self.photo, anchor=tkinter.NW)
        self.window.after(self.delay,self.update)

    def from_rgb(self,rgb):
        return "#%02x%02x%02x" % rgb
    def confirm():
        in_text = "입력 내용 : " + input_text.get()
        label.configure(text=in_text)

    def check_ip(self,ip):
        # 자기 자신에게 연결하려는 경우 확인
        if ip == socket.gethostbyname(socket.gethostname()):
            answer = askyesno('','자기 자신에게 연결할 수 없습니다. 그래도 강제로 연결합니까?')
            return answer
        # 아니면 True
        else:
            return True
    # sock.recv()로 size 크기의 바이트열을 받아오는 함수
    def full_recv(self,sock,size):
        a = sock.recv(size)
        while len(a) != size:
            a += sock.recv(size-len(a))
        return a


    # 소켓 서버
    def main_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(2)
        server_socket.bind((self.btn_input.get(), 9999))
        server_socket.listen(1)
        while True:
            if DEBUG==True: print('클라이언트 연결 시도중...')
            try:
                client_socket, address = server_socket.accept()
                break # 연결 성공시 while문 바깥으로
            except TimeoutError:
                # 연결시도 중단 버튼 또는 닫기버튼 눌렀으면 중단
                if (not self.connect_stopped_event.is_set()) or (not self.window_close_event.is_set()):
                    if DEBUG==True: print('클라이언트 연결 시도 중단됨')
                    server_socket.close()
                    self.connect_stopped_event.set()
                    self.window_close_event.set()
                    self.waiting_or_connected_event.clear()
                    self.btn_server['state'] = tkinter.NORMAL # 연결버튼 활성화
                    self.btn_client['state'] = tkinter.NORMAL # 연결버튼 활성화
                    return
            # 올바르지 않은 IP 입력 시 
            except OSError:
                if DEBUG==True: print('올바르지 않은 IP:',self.btn_input.get())
                sock.close()
                self.waiting_or_connected_event.clear()
                self.btn_server['state'] = tkinter.NORMAL # 연결버튼 활성화
                self.btn_client['state'] = tkinter.NORMAL # 연결버튼 활성화
                self.btn_kill['state'] = tkinter.DISABLED # 연결시도 중단 버튼 비활성화
                return
        if DEBUG==True: print('클라이언트 연결됨')
        self.btn_kill['state'] = tkinter.DISABLED # 연결시도 중단 버튼 비활성화
        self.btn_exit['state'] = tkinter.NORMAL # 통화종료 버튼 활성화
        # main_sender 함수와 main_receiver 함수 호출
        send = threading.Thread(target=self.main_sender, args=(client_socket,))
        recv = threading.Thread(target=self.main_receiver, args=(client_socket,))
        send.start()
        recv.start()
        send.join()
        recv.join()
        # main_sender 함수와 main_receiver 함수가 종료된 후
        if DEBUG==True: print('클라이언트 연결 끊김')
        client_socket.close()
        server_socket.close()
        self.disconnected_event.set()
        self.window_close_event.set()
        self.waiting_or_connected_event.clear()
        self.btn_server['state'] = tkinter.NORMAL # 연결버튼 활성화
        self.btn_client['state'] = tkinter.NORMAL # 연결버튼 활성화
        self.btn_exit['state'] = tkinter.DISABLED # 통화종료 버튼 비활성화


    # 소켓 클라이언트
    def main_client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            if DEBUG==True: print('서버 연결 시도중...')
            try:
                sock.connect((self.btn_input.get(), 9999))
                break # 연결 성공시 while문 바깥으로
            except ConnectionRefusedError:
                # 연결 시도 중단 버튼 또는 닫기버튼 눌렀으면 중단
                if (not self.connect_stopped_event.is_set()) or (not self.window_close_event.is_set()):
                    if DEBUG==True: print('서버 연결 시도 중단됨')
                    sock.close()
                    self.connect_stopped_event.set()
                    self.window_close_event.set()
                    self.waiting_or_connected_event.clear()
                    self.btn_server['state'] = tkinter.NORMAL # 연결버튼 활성화
                    self.btn_client['state'] = tkinter.NORMAL # 연결버튼 활성화
                    return
            # 올바르지 않은 IP 입력 시 
            except OSError:
                if DEBUG==True: print('올바르지 않은 IP:',self.btn_input.get())
                sock.close()
                self.waiting_or_connected_event.clear()
                self.btn_server['state'] = tkinter.NORMAL # 연결버튼 활성화
                self.btn_client['state'] = tkinter.NORMAL # 연결버튼 활성화
                self.btn_kill['state'] = tkinter.DISABLED # 연결시도 중단 버튼 비활성화
                return
        if DEBUG==True: print('서버 연결됨')
        self.btn_kill['state'] = tkinter.DISABLED # 연결시도 중단 버튼 비활성화
        self.btn_exit['state'] = tkinter.NORMAL # 통화종료 버튼 활성화
        # main_sender 함수와 main_receiver 함수 호출
        send = threading.Thread(target=self.main_sender, args=(sock,))
        recv = threading.Thread(target=self.main_receiver, args=(sock,))
        send.start()
        recv.start()
        send.join()
        recv.join()
        # main_sender 함수와 main_receiver 함수가 종료된 후
        if DEBUG==True: print('서버 연결 끊김')
        sock.close()
        self.disconnected_event.set()
        self.window_close_event.set()
        self.waiting_or_connected_event.clear()
        self.btn_server['state'] = tkinter.NORMAL # 연결버튼 활성화
        self.btn_client['state'] = tkinter.NORMAL # 연결버튼 활성화
        self.btn_exit['state'] = tkinter.DISABLED # 통화종료 버튼 비활성화


    # 소켓으로 데이터를 보내는 함수
    def main_sender(self,sock):


        # 오디오 데이터 전송
        def audio_callback(in_data, frame_count, time_info, status):
            try:
                data_size = struct.pack('>I',len(in_data))
                sock.send(b'\x01'+data_size+in_data)
            # 상대방이 통화를 종료했을 경우 중단
            except (ConnectionResetError, ConnectionAbortedError):
                pass
            return (None, pyaudio.paContinue)
        stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=8192, stream_callback=audio_callback)


        # 비디오 데이터 전송
        widthheight = struct.pack('>II',int(self.vid.width),int(self.vid.height))
        # 통화종료 버튼 또는 닫기버튼을 누르면 중단
        while self.disconnected_event.is_set() and self.window_close_event.is_set():
            try:
                ret, frame = self.vid.get_frame()
                if ret:
                    sock.send(b'\x02'+widthheight+frame.tobytes())
            # 상대방이 통화를 종료했을 경우 중단
            except (ConnectionResetError, ConnectionAbortedError):
                break
        stream.close()
        self.disconnected_event.clear()


    # 소켓으로부터 데이터를 받는 함수
    def main_receiver(self,sock):
        stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, output=True, frames_per_buffer=8192)
        # 통화종료 버튼 또는 닫기버튼을 누르면 중단
        while self.disconnected_event.is_set() and self.window_close_event.is_set():
            try:
                # 연결 오류             : b''
                # 오디오 데이터가 온 경우: b'\x01'
                # 비디오 데이터가 온 경우: b'\x02'
                rcvd_data = sock.recv(1)
                if rcvd_data == b'': break

                # 오디오 데이터가 왔다면 오디오로 출력
                elif rcvd_data == b'\x01':
                    size = struct.unpack('>I',self.full_recv(sock,4))[0]
                    volume = 4
                    rcvd_data = np.frombuffer(self.full_recv(sock,size), dtype=np.int16) * volume
                    stream.write(rcvd_data.tobytes())

                # 비디오 데이터가 왔다면 이미지로 출력
                elif rcvd_data == b'\x02':
                    width, height = struct.unpack('>II',self.full_recv(sock,8))
                    rcvd_data = self.full_recv(sock,width*height*3)
                    # GUI에 비디오 띄우는 코드를 여기에
                    self.show_other_video = True
                    frame = np.frombuffer(rcvd_data[:width*height*3],dtype='uint8').reshape((height,width,3))
                    self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                    self.canvas.create_image(0,0, image=self.photo, anchor=tkinter.NW)

            # 상대방이 통화를 종료했을 경우 중단
            except (ConnectionResetError, ConnectionAbortedError):
                break
        stream.close()
        cv2.destroyAllWindows()
        self.disconnected_event.clear()


class  MyVideoCapture:
    """docstring for  MyVideoCapture"""
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("unable open video source", video_source)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret,None)       
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()




App(tkinter.Tk(),"tkinter ad OpenCV")