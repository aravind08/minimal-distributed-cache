from gevent import socket
from gevent import monkey
monkey.patch_all()

host, port = ('localhost', 6600)
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((host, int(port), ))

conn.send(bytes("SET A 123", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.send(bytes("SET B ANACONDA", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.send(bytes("GET A", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.send(bytes("GET B", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.close()