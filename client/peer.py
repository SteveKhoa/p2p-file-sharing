import socket
import threading
import time

"""
For socket.listen(MAX_NONACCEPTED_CONN).

socket.listen([backlog]) backlog here controls how many 
non-accept()-ed connections are allowed to be outstanding.
Should be set to 5

https://stackoverflow.com/questions/2444459/python-sock-listen
"""
MAX_NONACCEPTED_CONN = 5

BUFF_SIZE = 1024

"""
Server Host address and Port 
Any peer should have a connection to server
To be able to request any action regarding it type (senderPeer or receiverPeer)
"""
#SERVER_HOST = '127.0.0.1'

BROADCAST_IP = '0.0.0.0'
SERVER_PORT = 12345  

BROADCAST_START_PORT = 13000
BROADCAST_END_PORT = 13010
class Peer:
    def __init__(self, host, port, repo_dir):
        self._host = host
        self._port = port
        self._socket_for_server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._repo_dir = repo_dir
        self._connections = []
        self._published_file = []
        self._server_ip = None
    
        threading.Thread(target=self._handle_server_address_broadcast, args=()).start()
    
   
    def _handle_server_address_broadcast(self):
        while True:
            try:
                broadcast_socket = self._get_broadcast_socket()
                
                data, addr = broadcast_socket.recvfrom(1024)
                message = data.decode()
                if message.startswith("SERVER_ADDRESS"):
                    _, server_address = message.split()
                    server_ip, server_port = server_address.split(':')
                    print(f"Received server IP: {server_ip}, server broadcast port: {server_port}")
                    self._server_ip = server_ip

                    self._connect_to_server()

                    broadcast_socket.close()
                    break
            except Exception as e:
                print(f"Error handling server address broadcast: {e}")

    def _get_broadcast_socket(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for port in range(BROADCAST_START_PORT, BROADCAST_END_PORT):
            try:
                broadcast_socket.bind((BROADCAST_IP, port))
                broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                break
            except Exception as e:
                continue
        return broadcast_socket


    def _connect_to_server(self):
        """
        Connect to existing server
        If we can not have a connection, This peer consider doing nothing
        We should close the socket and terminate this peer object 
        (Python have a garbage collector so i think manual termination is not necessary in this case)
        """
        try:
            self._server_connection_edge = self._socket_for_server_connection.connect((self._server_ip, SERVER_PORT))
            print(f"Connected to server with edge {self._server_connection_edge}")
            threading.Thread(target=self._listen_to_server).start()
        except socket.error as connection_error:
            print(f"Error code: {connection_error}")
            self._socket_for_server_connection.close()

    
    def _handle_send_request_to_server(self, request, file_list = ""):
        # Assuming every request is send like this:
        # REQUEST/HOST:PORT:FILELIST (except _get_peer which only send a filename)
        # FILELIST is comma-seperated
        # example: "_post/123.123.123.2:8888:text.txt"; "_get_peer/img.png"
        
        _host_string = str(self._host)
        _port_string = str(self._port)
        _file_name_string = str(file_list)
        
        #Handle command data packet to send to server
        _send_packet = request + "/" + _host_string + ":" + _port_string + ":" + _file_name_string
        _send_packet = _send_packet.encode("utf-8")
        print(_send_packet)
        try:
            print(self._socket_for_server_connection.sendto(_send_packet, (self._server_ip, SERVER_PORT)))
        except socket.error as error:
            print(f"Error occur trying to send request to server. Error code: {error}") 

    def _listen_to_server(self):
        raise NotImplementedError("Subclass must implement this method")
    
    
    
    def _post_all_published_file(self):
        all_published_file = ""        
        
        for fname in self._published_file:
            all_published_file += fname + ","
        
        all_published_file = all_published_file.rstrip(',') # Remove the last comma

        if all_published_file != "":
            self._handle_send_request_to_server("_post", all_published_file)


class SenderPeer(Peer):
    def __init__(self, host, port, repo_dir):
        super().__init__(host, port, repo_dir)
        
        # Create a separate thread for listening to other peers
        #*nvhuy: should only create 1 thread for 1 peer lifetime, so i put itt at init
        self._thread_listening = threading.Thread(
            target=self._listening_to_connect
        ).start()

    def _listen_to_server(self):
        while True:
            message = self._socket_for_server_connection.recv(1024).decode('utf-8')
            request, data = message.split('/')
            if request == '_ping':
                print("Received ping from server")
                self._handle_send_request_to_server("_pong")
            elif request == '_discover':
                self._post_all_published_file()
            elif request == '_peer':
                _peers = self._handle_receive_peers_string(data)
                if len(_peers) > 0:
                    self._post_all_published_file(_peers)
                else:
                    print("No peer has this file")

    def _listening_to_connect(self):
        """
        Continuously looping to listen to any peer peer connection.
        """
        print(f"{self._host} and {self._port}")
        self._socket_for_peer_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_for_peer_connection.bind((self._host, self._port))
        self._socket_for_peer_connection.listen(MAX_NONACCEPTED_CONN)

        # print(f"Listening for new connection to {self._host} : {self._port}")
        while True:
            connectionEdge, otherPeerAddress = self._socket_for_peer_connection.accept()
            with connectionEdge:
                print('Connected by', otherPeerAddress, connectionEdge)
                self._connections.append(connectionEdge)
                #*Assume package send from receiver:
                #*FNAME
                fname = connectionEdge.recv(BUFF_SIZE)
                fname = fname.decode('utf-8')
                self.share(fname)
                self._connections.remove(connectionEdge)
                connectionEdge.close()
            # (otherPeerHost, otherPeerPort) = socket.getnameinfo(otherPeerAddress, True)
            # otherPeerPort = int(otherPeerPort)
            # print(f"connection : {connectionEdge}")
            # print(f"Allow connection from {otherPeerAddress}")
    
    def _post(self, fname):
        """
        Request the server to add this peer to list of active peers who has 'fname'.
        """
        # This method does nothing for now since we dont have a server yet
        _file_list = fname
        _request = "_post"
        self._handle_send_request_to_server(_request, _file_list)
        # ? QUESTION: Nkhoa, I'm not sure why we need lname to be sent to server.
        # I think its not neccessary for the server to know that information.   
        # Thats why I dont pass lname as param into this function

    def _request_end(self, fname):
        """
        Request the server to remove this peer from list of active peers who has 'fname'.
        """
        # This method does nothing for now since we dont have a server yet
        #* nvhuy: _request_end should only request server to remove 
        #* this peer list of active peers of 1 specific 'fname, thus it should have fname as a argument.
        #* This should be necessary when we want to only remove publishment of 1 file in our repo dir only
        
        #* For remove all files publishment, we should have another method
        
        _file_list = fname
        _request = "_request_end"
        self._handle_send_request_to_server(_request, _file_list)

    def publish(self, lname: str = "", fname: str = "text.txt"):
        """
        Post file information to the server and start listening for any connection
        from other peers to start sharing.
        """
        
        if fname in self._published_file:
            print(f"Already published {fname}")
            #return # Published file should only be check at server side
        

        #Add file to published list
        self._published_file.append(fname)
        # Post file information to the server
        self._post(fname)
        #? QUESTION: nvhuy, Why did we want to recreate a new thread for every time we publish here?
        
        #? QUESTION: nvhuy, should we have a list of pair (lname, fname) store in sender peer so that
        #? Went the receiver send a fetch request with lname, 
        #? we can find the fname file directory and send this file to receiver
        #* This would match well with nkhoa solution proposal in receiverPeer._connect_with_peer
        
    def stop_publish_specific_file(self, fname):
        """
        Request the server to remove this peer from list of active peers of a specific and close the temporary socket
        connection itself.
        """
        if fname not in self._published_file:
            print(f"Can find published file name {fname}")
            return
        
        self._request_end(fname)
        self._published_file.remove(fname)
        
    def stop_publish(self):
        """
        Request the server to remove this peer from list of active peers and close the socket
        connection itself.
        """

        while len(self._published_file) != 0:
            fname = self._published_file[0]
            self.stop_publish_specific_file(fname=fname)
            print(len(self._published_file))
            
        self._socket_for_server_connection.close()

    def share(self, fname: str):
        """
        Start broadcasting file 'fname' too all of its connections.
        """

        # ! ISSUE: share could only share one fname. In fact, one SenderPeer
        # should be able to send multiple files to multiple peers differently.
        # $ PROPOSAL: NKhoa, see _connect_with_peer() for more details
        with open(self._repo_dir + fname, "rb") as infile:
            
            #*nvhuy: I found this easier way to send file
            for conn in self._connections:
                        print(f"{conn}")
                        conn.sendfile(infile)
                        
                        
            #*nvhuy: Still want to keep the other way for reference later if needed
            # while True:
            #     data_chunk = infile.read(BUFF_SIZE)
            #     if not data_chunk:
            #         print(f"share {fname} completed")
            #         break

            #     if len(self._connections) > 0:
                    
            #         for conn in self._connections:
            #             print(f"{conn}")
            #             conn.sendall(data_chunk)
            #     else:
            #         print("No peer connection was established.")
            #         print("Waiting for more peers...")
            #         break


class ReceiverPeer(Peer):
    def __init__(self, host, port, repo_dir):
        super().__init__(host, port, repo_dir)
        self._getting_file = None
        

    def _connect_with_peer(self, other_peer_host, other_peer_port, fname) -> bool:
        """
        Get connected to other_peer.

        Returns True on successful connection, False on failed connection.
        """
        try:
            self._socket_for_peer_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket_for_peer_connection.bind((self._host, self._port))
            connectionEdge = self._socket_for_peer_connection.connect((other_peer_host, other_peer_port))

            print(self._socket_for_peer_connection.sendto(fname.encode('utf-8'),(other_peer_host, other_peer_port)))
            # ! ISSUE: A Peer connection should also come with the FILENAME that connection
            # is requesting, since one sender could send different files to different receivers
            # at the same time.
            
            # $ PROPOSAL: NKhoa: Perhaps right after connection, we should send some kind of 
            # meta information (such as REQUESTED_FILENAME) to the SenderPeer to make our request explicit
            # about what file this peer is requesting specifically

            return True
        except socket.error as connection_error:
            print(f"Error code: {connection_error}")
            return False
    

    def _listen_to_server(self):
        while True:
            try:

                message = self._socket_for_server_connection.recv(1024).decode('utf-8')
                request, data = message.split('/')
                if request == '_ping':
                    print("Received ping from server")
                    self._handle_send_request_to_server("_pong")
                elif request == '_discover':
                    self._post_all_published_file()
                elif request == '_peer':
                    _peers = self._handle_receive_peers_string(data)
                    if len(_peers) > 0:
                        self._contact_peer_and_fetch(_peers)
                    else:
                        print("No peer has this file")

            except socket.error as e:
                print(f"An error occurred: {e}")
                break    
    

    def _handle_receive_peers_string(self, receiver_peers) -> [(str, int)]:
        """
        This function handle received data from server about peers who have fname
        Return the list of peer (host, port) 
        """
        _peers = []
    
        _peers = receiver_peers.split(',')
        _return_peers = []
        for peer in _peers:
            host, port = peer.split(':')
            port = int(port)
            peer = (host, port)
            _return_peers.append(peer)
        return _return_peers

    def _get_peers(self, fname: str) -> [(str, int)]:
        """
        This function get the peer list who currently has file 'fname'
        from the remote server.
        """

        # This function needs server to operate.
        # For testing and simplicity, NKhoa put an example of
        # fetched array down here as a retval
        _file_list = fname
        _request = "_get_peer"
        self._handle_send_request_to_server(_request,_file_list)
        

    def fetch(self, fname: str) -> bool:
        """
        API for fetching file 'fname' from another peer. The fetched file will be 
        automatically written into this peer's repository.

        Returns True on successful fetch, False otherwise.
        """
        self._getting_file = fname
        self._get_peers(fname)  # Get the list of IP addresses from server
        
        
    
    def _contact_peer_and_fetch(self, peers_arr):
        (sender_host, sender_port) = peers_arr[0]
        fname = self._getting_file

        connect_status = self._connect_with_peer(sender_host, sender_port, fname)
        
        if (connect_status):
            
            with open(self._repo_dir + fname, "wb") as outfile:
                while True:
                    print("receive: ")
                    data_chunk = self._socket_for_peer_connection.recv(BUFF_SIZE)
                    if not data_chunk:
                        break

                    outfile.write(data_chunk)

            print("Receiving file completed.")
            return True
        else:
            return False

    def stop_receive(self):
        '''
        Terminate socket connected with server 
        '''
        self._socket_for_server_connection.close()