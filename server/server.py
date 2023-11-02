import socket
import threading

MAX_CONNECTIONS = 5
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345  

class Server:
    def __init__(self):
        self._peers = {}  # A dictionary to store peer information (address, port, available files)
        self._lock = threading.Lock()
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((SERVER_HOST, SERVER_PORT))
        self._server_socket.listen(MAX_CONNECTIONS)

        # Receive commands from clients (POST, REQUEST_END, GET_PEER) 
        # Update the self._peers dictionary as needed
        # Return a list of peer with requested file to the cilent

    def _handle_client(self, client_socket):

        # Assuming every request is send like this:
        # REQUEST/HOST:PORT:FILELIST (except _get_peer which only send a filename)
        # FILELIST is comma-seperated
        # example: "_post/123.123.123.2:8888:text.txt"; "_get_peer/img.png"

        # Seperate request and data from the package
        package = client_socket.recv(1024).decode("utf-8").strip()
        request, data = pack.split("/")
        #print(pack)

        try:
            if request == "_post":  
            # Process a POST request from a peer to announce its available files
                
                host, port, files = data.split(":")
                available_files = files.split(",")
                with self._lock:
                    if (host, int(port)) in self._peers:
                        self._peers[(host, int(port))].extend(available_files)
                    else:
                        self._peers[(host, int(port))] = available_files

            elif(request == "_request_end"):
            # Process a REQUEST_END request from a peer to remove a file from its list
            # or remove itself from the server
                host, port, removed_file = data.split(":")
                if not removed_file:
                    with self._lock:
                        del self._peer[(host, int(port))]
                else:
                    with self._lock:
                        if (host, int(port)) in self._peers:
                            # Remove the specified file from the peer's list of available files
                            if removed_file in self._peers[(host, int(port))]:
                                self._peers[(host, int(port))].remove(removed_file)


            elif request == "_get_peer":
            # Process a GET_PEER request from a peer looking for a file
                filename = data
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
            else: 
                print("Unknown request")
        
        except Exception as e:
            print("Error: {str(e)}")

        finally:
            client_socket.close()

    def start(self):
        print("listening...")
        while True:
            client_socket, client_address = self._server_socket.accept()
            client_handler = threading.Thread(target=self._handle_client, args=(client_socket,))
            client_handler.start()

    def stop(self):
        self._server_socket.close()

if __name__ == '__main__':
    server = Server()
    server.start()