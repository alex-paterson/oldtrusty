import socket
from server import TCPServer

server = TCPServer()
server.serve_forever()
