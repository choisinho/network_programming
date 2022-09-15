# lst = [1, 2, 3]
# s = 'good_morning'
# print(type(lst))
# print(type(s))

# class Score:
#     pass
# lst = list()
# mine = Score()
# lst.append(1)
# print(mine)
#
class String:
    def __init__(self, str='Unnamed'):
        self.str = str
    def toBytes(self, str):
        self.str = str.encode()
    def fromBytes(self, bytes):
        self.str = bytes.decode()
    def get(self):
        return self.str

s = String()
s.toBytes("이순신")
print(s.get(), len(s.get()))
s.fromBytes("이순신".encode())
print(s.get())

# class String:
#     def __init__(self, text="Unnamed"):
#         self.text = text
#     def toBytes(self):
#         return self.text.encode()
#     def fromBytes(self)