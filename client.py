import socket
from oldtrusty import *

# args = parse_args()
# print(args)

client = TCPClient()
client.send_file("meme.txt")
