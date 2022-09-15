import threading
import time

def func(*data):
    print(data)
    time.sleep(2)

t = threading.Thread(target=func, args=(1, 2, 3))
t.start()
t.join()
print("end of program")