import socket
from oldtrusty import *

args = parse_args()
client = TCPClient()
print(args)
print("")

if args.filename:
    filename = args.filename
    client.send_file(filename)
elif args.certificate:
    filename = args.certificate
    client.send_certificate(filename)
