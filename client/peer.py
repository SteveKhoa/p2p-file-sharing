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
        
    def connect_with_peer(self, otherPeerHost, otherPeerPort):
        '''
        Connect this peer with another peer with given host and port
        '''
        try:
            connectionEdge = self.socket.connect((otherPeerHost,otherPeerPort))
            self.connections.append(connectionEdge)
            print(f"Successfully connected with {otherPeerHost} : {otherPeerPort}")
            print(f"Connection Edge = {connectionEdge}")
        except socket.error as connectionError:
            print(f"Error occur trying to connect with {otherPeerHost} : {otherPeerPort}")
            print(f"Error code: {connectionError}")
    
    def listening_to_connect(self):
        '''
        Bind this peer socket to start listening to incoming connection continuously 
        '''
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

            
    
    def send_msg(self, data):
        '''
        Send data to all connections in connections list
        '''
        for connection in self.connections:
            try:
                connection.sendall(data.encode())
            except socket.error as communicateError:
                print(f"False to communicate. Error: {communicateError}")
    def receive_msg(self):
        '''
        Receive msg from sender
        '''
        (msg ,  otherPeerAddress) = self.socket.recvfrom(1024)
        if msg == "stop":
            self.socket.close();
            return
        # (otherPeerHost, otherPeerPort) = socket.getnameinfo(otherPeerAddress, True)
        print(f"Receive message from {otherPeerAddress} : {msg}")
    def start(self):
        '''
        Create a new thread to start listening to others listen thread parallel with sending msg
        '''
        self.listenThread = threading.Thread(target = self.listeningToConnect)
        self.listenThread.start()
    def stop_listening_for_connection(self):
        '''
        Stop listening for another connection, clear all connections
        '''
        print(self.listenThread)
        self.listenThread.join()
        print("Clear all connection")
        self.connections.clear()
        
    