# Echo client program
import socket
from tools.hexdump import hexdump

HOST = '192.168.1.15'  # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = (b'Hello, world')
    print('send %d byte to server' % (len(data)))
    hexdump(data)
    s.sendall(data)
    data = s.recv(1024)
    print('receive %d byte from server' % (len(data)))
    hexdump(data)
    print('Received data' ,data)
