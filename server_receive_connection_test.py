import socket
import threading
import os
from client import peer

this_file_path = os.path.dirname(os.path.realpath(__file__))

host = '127.0.0.6'
port = 2415        
repo_dir = this_file_path + "/receiver_repo_test/"

receiver = peer.ReceiverPeer(host, port, repo_dir)

while True:
    prompt = input()
    print("Inputed prompt:|" + prompt + "|")
    print("Executing...")

    arg = []
    arg = prompt.split(" ")
    if (arg[0] == 'fetch'):
        receiver.fetch(fname=arg[1])
        print("fetched")
    elif (arg[0] == 'stop'):
        receiver.stop_receive()
        print("Stopped.")
        break