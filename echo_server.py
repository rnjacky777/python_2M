# Echo server program
import socket
from tools.hexdump import hexdump

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data: break
            print('receive %d byte from %s' % (len(data),str(addr)))
            hexdump(data)
            print('send %d byte to %s' % (len(data),str(addr)))
            hexdump(data)
            conn.sendall(data)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

