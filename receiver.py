from client import peer_exp
import os

this_file_path = os.path.dirname(os.path.realpath(__file__))
receiver = peer_exp.ReceiverPeer('127.0.0.1', 8000, this_file_path + '/receiver/')

receiver.fetch('image.png')