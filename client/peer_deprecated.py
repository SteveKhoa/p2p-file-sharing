import socket
import threading

"""
For socket.listen(MAX_NONACCEPTED_CONN).

socket.listen([backlog]) backlog here controls how many 
non-accept()-ed connections are allowed to be outstanding.
Should be set to 5

https://stackoverflow.com/questions/2444459/python-sock-listen
"""
MAX_NONACCEPTED_CONN = 5


class Peer:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connections = []
        print(f"Successfully create peer {host} : {port}")

    def ConnectWithPeer(self, otherPeerHost, otherPeerPort):
        try:
            connectionEdge = self._socket.connect((otherPeerHost, otherPeerPort))
            self._connections.append(connectionEdge)
            print(f"Successfully connected with {otherPeerHost} : {otherPeerPort}")
            print(f"Connection Edge = {connectionEdge}")
        except socket.error as connectionError:
            print(
                f"Error occur trying to connect with {otherPeerHost} : {otherPeerPort}"
            )
            print(f"Error code: {connectionError}")

    def listeningToConnect(self):
        self._socket.bind((self._host, self._port))
        self._socket.listen(MAX_NONACCEPTED_CONN)

        print(f"Listening for new connection to {self._host} : {self._port}")
        while True:
            connectionEdge, otherPeerAddress = self._socket.accept()
            self._connections.append(connectionEdge)
            (otherPeerHost, otherPeerPort) = socket.getnameinfo(otherPeerAddress, True)
            otherPeerPort = int(otherPeerPort)
            print(f"connection : {connectionEdge}")
            print(f"Allow connection from {otherPeerAddress}")
            #

    def sendMsg(self, data):
        for connection in self._connections:
            try:
                connection.sendall(data.encode())
            except socket.error as communicateError:
                print(f"False to communicate. Error: {communicateError}")

    def receiveMsg(self):
        (msg, otherPeerAddress) = self._socket.recvfrom(1024)
        # (otherPeerHost, otherPeerPort) = socket.getnameinfo(otherPeerAddress, True)
        print(f"Receive message from {otherPeerAddress} : {msg}")

    def start(self):
        listenThread = threading.Thread(target=self.listeningToConnect)
        listenThread.start()
        # question?  Only two threads here? Not very generic!

    def publish(lname: str, fname: str):
        pass

    def fetch(fname: str):
        pass
