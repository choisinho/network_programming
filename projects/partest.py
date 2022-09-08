import struct

def readDatafile(filename):
    lst = []
    fd = open(filename, 'rb')
    while True:
        raw = fd.read(4)
        if len(raw) < 4:
            break
        lst.append(struct.unpack('>i', raw)[0])
    fd.close()
    return lst

data = readDatafile('data1000.bin')
print(len(data))
print(data[0:10])

# def foo(a, b, c=0, d=0):
#     print(a, b, c, d)
#
# foo(1, 2)
# foo(1, 2, 3)
# foo(1, 2, 3, 4)