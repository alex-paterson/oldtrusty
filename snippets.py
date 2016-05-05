# SERRVER

# host = '127.0.0.1'
# port = 3002
#
# s = socket.socket()
# s.bind((host, port))
# s.listen(1)
# print("Listening on {}:{}".format(host, port))
#
# while True:
#     c, addr = s.accept()
#     print("Connection from {} accepted.".format(addr))
#     while True:
#         data = c.recv(1024)
#         if not data:
#             break
#         print("From {}: {}".format(addr, data))
#         data = str(data).upper()
#         c.send(data)
#         print("To {}: {}".format(addr, data))
#     c.close()
#     print("Connection from {} closed.".format(addr))



# client


s = socket.socket()
s.connect(('127.0.0.1', 3002))
message = raw_input("-> ")
while message != 'q':
    s.send(message)
    data = s.recv(1024)
    print(data)
    message = raw_input("-> ")
s.close()
