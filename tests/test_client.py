import socket, ssl

host = '127.0.0.1'
port = 3002
#
s = socket.socket()
ssl_soc = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED)
ssl_soc.connect((host,port))



name = "alex"
for i in range(len(name),32):
    name += chr(0)

print(name)
print(len(name))

message = "030" + chr(0) + chr(1) + name + "meme.txt"
# message = raw_input("->")
while message != 'q':
	ssl_soc.send(message)
	data = ssl_soc.recv(1024)
	print "Received from server: " + str(data)
	message = raw_input("->")
s.close()
