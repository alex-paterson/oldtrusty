import socket

host = '127.0.0.1'
port = 3002

s = socket.socket()
s.connect((host,port))

message = raw_input("->")
while message != 'q':
	s.send(message)
	data = s.recv(1024)
	print "Received from server: " + str(data)
	message = raw_input("->")
s.close()
