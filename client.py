import socket
from oldtrusty import *

args = parse_args()
# print(args)
# print("")

if args.host:
    host_port = args.host.split(":")
    host = host_port[0]
    port = host_port[1]
    client = TCPClient(host, int(port))
else:
    client = TCPClient()


if args.filename:
    filename = args.filename
    client.send_file(filename)
elif args.fetch:
    filename = args.fetch
    client.request_file(filename)
elif args.certificate:
    filename = args.certificate
    client.send_certificate(filename)
else:
    print("run with -h for help")
