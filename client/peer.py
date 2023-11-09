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

BUFF_SIZE = 1024

"""
Server Host address and Port 
Any peer should have a connection to server
To be able to request any action regarding it type (senderPeer or receiverPeer)
"""
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345  

class Peer:
    def __init__(self, host, port, repo_dir):
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._repo_dir = repo_dir
        self._connections = []
        self._connect_to_server()
        
    def _connect_to_server(self):
        """
        Connect to existing server
        If we can not have a connection, This peer consider doing nothing
        We should close the socket and terminate this peer object 
        (Python have a garbage collector so i think manual termination is not necessary in this case)
        """
        try:
            self._server_connection_edge = self._socket.connect((SERVER_HOST, SERVER_PORT))
            print("Connected to server")
        except socket.error as connection_error:
            print(f"Error code: {connection_error}")
            self.socket.close()
            

class SenderPeer(Peer):
    def _listening_to_connect(self):
        """
        Continuously looping to listen to any peer peer connection.
        """
        self._socket.bind((self._host, self._port))
        self._socket.listen(MAX_NONACCEPTED_CONN)

        # print(f"Listening for new connection to {self._host} : {self._port}")
        while True:
            connectionEdge, otherPeerAddress = self._socket.accept()
            self._connections.append(connectionEdge)

            # (otherPeerHost, otherPeerPort) = socket.getnameinfo(otherPeerAddress, True)
            # otherPeerPort = int(otherPeerPort)
            # print(f"connection : {connectionEdge}")
            # print(f"Allow connection from {otherPeerAddress}")

    def _handle_send_request_to_server(self, request, file_list):
        # Assuming every request is send like this:
        # REQUEST/HOST:PORT:FILELIST (except _get_peer which only send a filename)
        # FILELIST is comma-seperated
        # example: "_post/123.123.123.2:8888:text.txt"; "_get_peer/img.png"
        
        _server_host_string = str(SERVER_HOST)
        _server_port_string = str(SERVER_PORT)
        _file_name_string = str(file_list)
        
        #Handle post command data packet to send to server
        _send_packet = request + str(SERVER_HOST) + ":" + str(SERVER_PORT) + ":" + _file_name_string
        try:
            self._socket.sendto(_send_packet, (SERVER_HOST, SERVER_PORT))
        except socket.error as error:
            print(f"Error occur trying to send request to server. Error code: {error}") 
    
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

    def _request_end(self):
        """
        Request the server to remove this peer from list of active peers who has 'fname'.
        """
        # This method does nothing for now since we dont have a server yet
        pass

    def publish(self, lname: str = "", fname: str = "text.txt"):
        """
        Post file information to the server and start listening for any connection
        from other peers to start sharing.
        """
        # Post file information to the server
        self._post(fname)
        #? QUESTION: nvhuy, Why did we want to recreate a new thread for every time we publish here?
        
        #? QUESTION: nvhuy, should we have a list of pair (lname, fname) store in sender peer so that
        #? Went the receiver send a fetch request with lname, 
        #? we can find the fname file directory and send this file to receiver
        #* This would match well with nkhoa solution proposal in receiverPeer._connect_with_peer
        
        # Create a separate thread for listening to other peers
        self._thread_listening = threading.Thread(
            target=self._listening_to_connect
        ).start()

    def stop_publish(self):
        """
        Request the server to remove this peer from list of active peers and close the socket
        connection itself.
        """
        self._request_end()
        self._socket.close()

    def share(self, fname: str):
        """
        Start broadcasting file 'fname' too all of its connections.
        """

        # ! ISSUE: share could only share one fname. In fact, one SenderPeer
        # should be able to send multiple files to multiple peers differently.
        # $ PROPOSAL: NKhoa, see _connect_with_peer() for more details
        with open(self._repo_dir + fname, "rb") as infile:
            while True:
                data_chunk = infile.read(BUFF_SIZE)
                if not data_chunk:
                    break

                if len(self._connections) > 0:
                    for conn in self._connections:
                        conn.sendall(data_chunk)
                else:
                    print("No peer connection was established.")
                    print("Waiting for more peers...")
                    break


class ReceiverPeer(Peer):
    def _connect_with_peer(self, other_peer_host, other_peer_port) -> bool:
        """
        Get connected to other_peer.

        Returns True on successful connection, False on failed connection.
        """
        try:
            connectionEdge = self._socket.connect((other_peer_host, other_peer_port))

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

    def _get_peers(self, fname: str) -> [(str, int)]:
        """
        This function get the peer list who currently has file 'fname'
        from the remote server.
        """

        # This function needs server to operate.
        # For testing and simplicity, NKhoa put an example of
        # fetched array down here as a retval
        return [("127.0.0.1", 1234)]

    def fetch(self, fname: str) -> bool:
        """
        API for fetching file 'fname' from another peer. The fetched file will be 
        automatically written into this peer's repository.

        Returns True on successful fetch, False otherwise.
        """
        peers_arr = self._get_peers(fname)  # Get the list of IP addresses from server
        (sender_host, sender_port) = peers_arr[0]

        connect_status = self._connect_with_peer(sender_host, sender_port)

        if (connect_status):
            with open(self._repo_dir + fname, "wb") as outfile:
                while True:
                    data_chunk = self._socket.recv(BUFF_SIZE)
                    if not data_chunk:
                        break

                    outfile.write(data_chunk)

            print("Receiving file completed.")
            return True
        else:
            return False