import random
import socket
import threading
import os
from client import peer

# Get the host name of the machine
host_name = socket.gethostname()

random_port_number = random.randint(0, 1000)

host_last_8bit_ip = socket.gethostbyname(host_name)
print("Host name:", host_name, "IP address:", host_last_8bit_ip)

sender_port = 1000 + random_port_number
receiver_port = 2000 + random_port_number

this_file_path = os.path.dirname(os.path.realpath(__file__))       
repo_dir = this_file_path + "/user_repo_" + str(random_port_number) + "/"

os.makedirs(repo_dir, exist_ok=True)


receiver = peer.ReceiverPeer(host_last_8bit_ip, receiver_port, repo_dir)
sender = peer.SenderPeer(host_last_8bit_ip, sender_port, repo_dir)


while True:
    #print("command pattern")
    #print("Command: publish lname fname  | Usage: Publish file fname to server")
    #print("Not use lname yet, so put what ever")
    #print("Example: publish Test test.txt")
    #print("Command: stop fname  | Usage: stop publish file fname")
    #print("Example: stop test.txt")
    #print("Command: fetch fname  | Usage: fetch file fname from first sender peer that have fname")
    #print("Example: fetch test.txt")
    #print("Command: end | Usage: shutdown this client" )
    #print("Example: end")
    prompt = input()
    #print("Inputed prompt:|" + prompt + "|")
    #print("Executing...")

    arg = []
    arg = prompt.split(" ")
    if (arg[0] == 'publish'):
        sender.publish(lname= arg[1], fname= arg[2])
        print("publish.")
    elif (arg[0] == 'stop'):
        sender.stop_publish_specific_file(fname= arg[1])
        print("Stopped.")
    elif (arg[0] == 'fetch'):
        receiver.fetch(fname=arg[1])
        print("fetched")
    elif (arg[0] == 'end'):
        sender.stop_publish()
        receiver.stop_receive()
        print("End.")
        break

