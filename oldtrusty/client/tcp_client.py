import os, socket

FRAME_LENGTH = 1024


class Packet:
    READY_TO_RECEIVE_PART = '000'

    START_OF_FILE = '001'
    START_OF_CERTIFICATE = '002'

    FILE_PART = '101'
    CERTIFICATE_PART = '102'

    END_OF_FILE = '351'
    END_OF_CERTIFICATE = '352'

    FILE_ALREADY_EXISTS = '401'
    FILE_DOESNT_EXIST = '402'

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
        self.__start_sending_file(filename)

    def send_certificate(self, filename):
        self.__connect()
        contents = self.__read_certificate(filename)
        resp_header, resp_message = self.__send_packet(Packet.CERTIFICATE, contents)



    # Internal Loops

    def __start_sending_file(self, filename):
        f = open(os.path.join(self.__files_path, filename), 'r')
        resp_packet_type, resp_message = self.__send_packet(Packet.START_OF_FILE, filename)
        message = f.read(FRAME_LENGTH/8)
        while resp_packet_type == Packet.READY_TO_RECEIVE_PART and message:
            resp_packet_type, resp_message = self.__send_packet(Packet.FILE_PART, message)
            message = f.read(FRAME_LENGTH/8)
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            self.__send_packet(Packet.END_OF_FILE)

    def __start_sending_certificate(self, filename):
        f = open(os.path.join(self.__certificates_path, filename), 'r')
        resp_packet_type, resp_message = self.__send_packet(Packet.START_OF_CERTIFICATE, filename)
        message = f.read(FRAME_LENGTH/8)
        while resp_packet_type == Packet.READY_TO_RECEIVE_PART and message:
            resp_packet_type, resp_message = self.__send_packet(Packet.CERTIFICATE_PART, message)
            message = f.read(FRAME_LENGTH/8)
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            self.__send_packet(Packet.END_OF_CERTIFICATE)




    # Connections and basic communication

    def __connect(self):
        self.__s.connect((self.__host, self.__port))

    def __send_packet(self, packet_type, message=""):
        print("- SENDING PACKET {}".format(packet_type))
        print("{}\n".format(message))
        self.__s.send(self.__add_header(packet_type, message))
        return self.__receive_packet()

    def __receive_packet(self):
        recv = self.__s.recv(FRAME_LENGTH)
        header = self.__read_header(recv)
        message = self.__strip_header(recv)
        print("+ RECEIVING PACKET {}".format(header))
        print("{}\n".format(message))
        return header, message


    # Packet formatting

    def __split_packet(self, packet):
        return self.__read_header(packet), self.__strip_header(packet)

    def __add_header(self, packet_type, message):
        return packet_type + message

    def __strip_header(self, packet):
        return packet[3:]

    def __read_header(self, packet):
        return packet[0:3]
