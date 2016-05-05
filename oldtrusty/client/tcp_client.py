import os, socket


class Packet:
    READY_TO_RECEIVE_FILE = '001'
    FILE = '101'
    CERTIFICATE = '102'
    SUCCESSFULLY_SAVED_FILE = '201'
    SUCCESSFULLY_SAVED_CERTIFICATE = '202'
    FILE_ALREADY_EXISTS = '401'
    UNRECOGNIZED_HEADER = '999'


class TCPClient:

    def __init__(self, host='127.0.0.1', port=3002):
        self.__host = host
        self.__port = port
        self.__s = socket.socket()
        self.__certificate_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certificates/')
        self.__files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files/')


    # Public methods

    def enter_loop(self):
        self.__connect()
        message = raw_input("-> ")
        while message != 'q':
            self.__s.send(message)
            self.__receive_packet()
            message = raw_input("-> ")
        self.__s.close()

    def send_file(self, filename):
        self.__connect()
        contents = self.__read_file(filename)
        self.__send_packet(Packet.FILE, contents)

    def send_certificate(self, filename):
        self.__connect()
        contents = self.__read_certificate(filename)
        self.__send_packet(Packet.CERTIFICATE, contents)


    # Connections and basic communication

    def __connect(self):
        self.__s.connect((self.__host, self.__port))

    def __send_packet(self, packet_type, message):
        self.__s.send(self.__add_header(packet_type, message))
        self.__receive_packet()

    def __receive_packet(self):
        response = self.__s.recv(1024)
        header = self.__read_header(response)
        message = self.__strip_header(response)
        print("HEADER: {}".format(header))
        print(message)


    # Packet formatting

    def __add_header(self, packet_type, message):
        return packet_type + message

    def __strip_header(self, packet):
        return packet[3:-1]

    def __read_header(self, packet):
        return packet[0:3]


    # File I/O

    # Returns file contents
    def __read_file(self, filename):
        with open(os.path.join(self.__files_path, filename), 'r') as open_file:
            contents = open_file.read()
        return contents

    # Returns certificate contents
    def __read_certificate(self, filename):
        with open(os.path.join(self.__certificate_path, filename), 'r') as open_file:
            contents = open_file.read()
        return contents
