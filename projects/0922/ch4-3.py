import ipaddress
import struct

ip32 = struct.pack('>4B', 192, 168, 0, 1)
print(ip32)
ipa = struct.unpack('>I', ip32)[0] #첫번째 것만 불러옴
print(ipa)
ipaddr = ipaddress.ip_address(ipa)
print(ipaddr)