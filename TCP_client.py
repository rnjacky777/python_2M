import socket

target_host = "111.250.179.100"
target_port = 9999

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# send some data
client.send("Hello world".encode())

# receive some data
response = client.recv(4096).decode()

print (response)