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
        
    def connect_with_peer(self, other_peer_host, other_peer_port):
        '''
        Connect this peer with another peer with given host and port
        '''
        try:
            connection_edge = self.socket.connect((other_peer_host,other_peer_port))
            self.connections.append(connection_edge)
            print(f"Successfully connected with {other_peer_host} : {other_peer_port}")
            print(f"Connection Edge = {connection_edge}")
        except socket.error as connection_error:
            print(f"Error occur trying to connect with {other_peer_host} : {other_peer_port}")
            print(f"Error code: {connection_error}")
    
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
            connection_edge, other_peer_address = self.socket.accept()
            self.connections.append(connection_edge)
            (other_peer_host, other_peer_port) = socket.getnameinfo(other_peer_address, True)
            other_peer_port = int(other_peer_port)
            print(f"connection : {connection_edge}")
            print(f"Allow connection from {other_peer_address}")

    def send_msg(self, data):
        '''
        Send data to all connections in connections list
        '''
        for connection in self.connections:
            try:
                connection.sendall(data.encode())
            except socket.error as communicate_error:
                print(f"False to communicate. Error: {communicate_error}")
                
    def receive_msg(self):
        '''
        Receive msg from sender
        '''
        (msg ,  other_peer_address) = self.socket.recvfrom(1024)
        if msg == "stop":
            self.socket.close();
            return
        # (other_peer_host, other_peer_port) = socket.getnameinfo(other_peer_address, True)
        print(f"Receive message from {other_peer_address} : {msg}")
        
    def start(self):
        '''
        Create a new thread to start listening to others listen thread parallel with sending msg
        '''
        self.listenThread = threading.Thread(target = self.listening_to_connect)
        self.listenThread.start()
        
    def stop_listening_for_connection(self):
        '''
        Stop listening for another connection, clear all connections
        '''
        print(self.listenThread)
        self.listenThread.join()
        print("Clear all connection")
        self.connections.clear()
        
    