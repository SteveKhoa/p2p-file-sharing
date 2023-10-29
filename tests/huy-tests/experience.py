import socket
import threading

import client.peer as client


hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
print(f"{host}")
port = 5252
newClient = client.Peer(host, port)
newClient.start()

while True:
    msg = input(">")
    newClient.sendMsg(msg)
    if msg == "stop":
        break

newClient._socket.close()
