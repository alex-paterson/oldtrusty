import socket

host = '127.0.0.1'
port = 3002
#
s = socket.socket()
s.connect((host,port))



name = "alex"
for i in range(len(name),32):
    name += chr(0)

print(name)
print(len(name))

message = "030" + chr(0) + chr(1) + name + "meme.txt"
# message = raw_input("->")
while message != 'q':
	s.send(message)
	data = s.recv(1024)
	print "Received from server: " + str(data)
	message = raw_input("->")
s.close()
