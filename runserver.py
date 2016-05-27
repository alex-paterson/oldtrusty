import socket
from server import TCPServer

# server = TCPServer('192.168.206.138', 3002)
server = TCPServer('127.0.0.1', 3002)
server.serve_forever()
