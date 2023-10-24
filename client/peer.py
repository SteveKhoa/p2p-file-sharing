import socket
import threading

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        print(f"Successfully create peer {host} : {port}")
        #self.start()
        
    def ConnectWithPeer(self, otherPeerHost, otherPeerPort):
        try:
            connectionEdge = self.socket.connect((otherPeerHost,otherPeerPort))
            self.connections.append(connectionEdge)
            print(f"Successfully connected with {otherPeerHost} : {otherPeerPort}")
            print(f"Connection Edge = {connectionEdge}")
        except socket.error as connectionError:
            print(f"Error occur trying to connect with {otherPeerHost} : {otherPeerPort}")
            print(f"Error code: {connectionError}")
    
    def listeningToConnect(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        #*listen([backlog]) backlog here controls how many non-accept()-ed connections are allowed to be outstanding.
        #* should be set to 5
        #* more detail on stack overflow please read: https://stackoverflow.com/questions/2444459/python-sock-listen
        
        print(f"Listening for new connection to {self.host} : {self.port}")
        while True:
            connectionEdge, otherPeerAddress = self.socket.accept()
            self.connections.append(connectionEdge)
            (otherPeerHost, otherPeerPort) = socket.getnameinfo(otherPeerAddress, True)
            otherPeerPort = int(otherPeerPort)
            print(f"connection : {connectionEdge}")
            print(f"Allow connection from {otherPeerAddress}")
            #
            
    
    def sendMsg(self, data):
        for connection in self.connections:
            try:
                connection.sendall(data.encode())
            except socket.error as communicateError:
                print(f"False to communicate. Error: {communicateError}")
    def receiveMsg(self):
        (msg ,  otherPeerAddress) = self.socket.recvfrom(1024)
        # (otherPeerHost, otherPeerPort) = socket.getnameinfo(otherPeerAddress, True)
        print(f"Receive message from {otherPeerAddress} : {msg}")
    def start(self):
        listenThread = threading.Thread(target = self.listeningToConnect)
        listenThread.start()
    
    
    