import socket
import argparse
from server import TCPServer

parser = argparse.ArgumentParser(description='OldTrusty Server')
parser.add_argument('-ip', '--ip', nargs=1, help='Optional, IP')
args = parser.parse_args()

if(args.ip is not None):
    host=''.join(args.ip)
else:
    host='127.0.0.1'

server = TCPServer(host, 3002)
server.serve_forever()
