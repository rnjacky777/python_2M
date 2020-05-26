# Echo client program
import socket
import time
from tools.hexdump import hexdump
from tools.netdata import *
def encode_data(data):
    t0,b0 = pack_number(data[0])
    t1,b1 = pack_number(data[1])
    t2,b2 = pack_number(data[2])
    t0 = t0.encode('utf-8')
    t1 = t1.encode('utf-8')
    t2 = t2.encode('utf-8')
    return (t0 + b0) +  (t1 + b1) + (t2 + b2)
def decode_data(b):
    result = []
    while b:
        tag,b  = b[:1].decode('utf-8'),b[1:]
        size = num_size_map.get(tag)
        data , b = b[:size] , b[size:]
        n = unpack_number(tag,data)
        result.append(n)
    return result
HOST = 'localhost'  # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = encode_data([5201314,1234,-19910101])
    print('send %d byte to server' % (len(data)))
    hexdump(data)
    s.sendall(data)
    data = s.recv(1024)
    data1 = decode_data(data)
    print('receive %d byte from server' % (len(data)))
    hexdump(data)
    print('Received data' ,data1)
