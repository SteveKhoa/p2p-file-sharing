import socket
import threading

import client.peer_deprecated as client

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
print(f"{host}")
port = 12236        
newClient = client.Peer(host, port)

newClient.ConnectWithPeer(host, 5252)

while True:
    newClient.receiveMsg()