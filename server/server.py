import socket
import threading
import time

MAX_CONNECTIONS = 5
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345  
UPDATE_ACTIVE_CLIENT_TIME = 5  # seconds

class Server:
    def __init__(self):
        self._peers = {}  # A dictionary to store peer information [(address, port)] = list of available files
        self._lock = threading.Lock()
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((SERVER_HOST, SERVER_PORT))
        self._server_socket.listen(MAX_CONNECTIONS)
        self._client_sockets = [] # For storing list of connected client

        # Receive commands from clients (POST, REQUEST_END, GET_PEER) 
        # Update the self._peers dictionary as needed
        # Return a list of peer with requested file to the cilent

    def _handle_client(self, client_socket):

        # Assuming every request is send like this:
        # REQUEST/HOST:PORT:FILELIST (except _get_peer which only send a filename)
        # FILELIST is comma-seperated
        # example: "_post/123.123.123.2:8888:text.txt"; "_get_peer/img.png"

        
        #*nvhuy: a while loop should ensure the server keep receive request from a client until the client is terminated
        while True:
            # Seperate request and data from the package
            package = client_socket.recv(1024).decode("utf-8").strip()
            request, data = package.split("/")
            #print(pack)

            print(package)
            try:
                if request == "_post":  
                # Process a POST request from a peer to announce its available files
                    
                    host, port, files = data.split(":")
                    available_files = files.split(",")
                    self._post(host, port, available_files)
                    
                elif(request == "_request_end"):
                # Process a REQUEST_END request from a peer to remove a file from its list
                # or remove itself from the server
                    host, port, removed_file = data.split(":")
                    self._request_end(host, port, removed_file)


                elif request == "_get_peer":
                # Process a GET_PEER request from a peer looking for a file
                # Return a list of peers with the requested file
                # in the form of a string (comma seperated between each)
                    host, port, files = data.split(":")
                    self._get_peer(client_socket, files)

                else: 
                    print("Unknown request")
            
            except Exception as e:
                print("Error: {str(e)}")

            #*nvhuy: We do not want to close the socket here
            # finally:
            #     client_socket.close()

    def _post(self, host, port, available_files):
        # Add the peer to the self._peers dictionary
        # with the list of available files
        # or update the list of available files if the peer is already in the dictionary

        with self._lock:
            if (host, int(port)) in self._peers:
                self._peers[(host, int(port))].extend(available_files)
            else:
                self._peers[(host, int(port))] = available_files

    def _request_end(self, host, port, removed_file):
        # Remove the specified file from the peer's list of available files
        # or remove the peer from the self._peers dictionary if no file is specified

        print("removed ", removed_file)
        with self._lock:
            if not removed_file:
                del self._peer[(host, int(port))]
            else:
                if (host, int(port)) in self._peers:
                    if removed_file in self._peers[(host, int(port))]:
                        self._peers[(host, int(port))].remove(removed_file)
            
    def _get_peer(self, client_socket, filename):
        # Return a list of peers with the requested file
        # in the form of a string (comma seperated between each)
        # Should looks like this:

        matching_peers = []

        with self._lock:
            for peer, files in self._peers.items():
                if filename in files:
                    matching_peers.append(f"{peer[0]}:{peer[1]}")

        if matching_peers:
            # Send a list of peers with the requested file to the client
            # in the form of a string (comma seperated between each)
            # Should looks like this: 127.0.0.1:1234,222.222.3.4:3456
            client_socket.send(",".join(matching_peers).encode("utf-8"))
        else:
            # No peer with the requested file
            client_socket.send("No peers with the requested file.".encode("utf-8"))

    def _ping_client(self, client_socket):
        try:
            # Send a small data packet
            client_socket.send(b'PING')
            return True
        except socket.error:
            return False

    def start_listen_to_new_client(self):
        print("start listening...")
        while True:
            client_socket, client_address = self._server_socket.accept()
            self._client_sockets.append(client_socket)
            if client_address: 
                print(f"Accepted socket with address {client_address}")
            client_handler = threading.Thread(target=self._handle_client, args=(client_socket,))
            client_handler.start()

    def start_ping_active_clients(self):
        # Remove dead peers from the self._peers dictionary
        # A peer is considered dead if it does not respond to a ping
        print("start pinging...")

        while True:
            time.sleep(UPDATE_ACTIVE_CLIENT_TIME)

            print("Pinging...")

            with self._lock:
                for client in self._client_sockets:
                    # Create a copy of keys to iterate over
                    if not self._ping_client(client):
                        self._client_sockets.remove(client)
                for peer in list(self._peers.keys()):
                    print(f"client {peer} with fname {self._peers[peer]}")


    def stop(self):
        self._server_socket.close()



if __name__ == '__main__':
    server = Server()
    start_thread = threading.Thread(target=server.start_listen_to_new_client)
    update_thread = threading.Thread(target=server.start_ping_active_clients)
    start_thread.start()
    update_thread.start()

