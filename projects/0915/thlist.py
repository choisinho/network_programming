import threading
import time

def thcode():
    print(threading.currentThread().getName())
    time.sleep(3)
    print(threading.currentThread().getName(), "end..")

thread_list = []
for _ in range(5):
    thread_list.append(threading.Thread(target=thcode))
    thread_list[-1].start() #가장 마지막 원소

for o in thread_list:
    o.join()

print('end of program')