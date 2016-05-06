import os, socket

FRAME_LENGTH = 1024


class Packet:

    START_OF_FILE = '000'
    START_OF_CERTIFICATE = '001'

    FILE_PART = '010'
    CERTIFICATE_PART = '011'

    END_OF_FILE = '020'
    END_OF_CERTIFICATE = '021'

    REQUEST_FILE = '030'

    READY_TO_RECEIVE_PART = '200'

    FILE_ALREADY_EXISTS = '401'
    FILE_DOESNT_EXIST = '411'
    CERTIFICATE_ALREADY_EXISTS = '402'
    CERTIFICATE_DOESNT_EXIST = '412'

    UNRECOGNIZED_HEADER = '500'
    UNEXPECTED_HEADER = '501'


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

    def request_file(self, filename):
        self.__connect()
        self.__send_packet(Packet.REQUEST_FILE, filename)
        resp_packet_type, resp_message = self.__receive_packet()
        if resp_packet_type == Packet.START_OF_FILE:
            self.__start_receiving_file(filename)
        else:
            print("Received unexpected header {}.\n".format(resp_packet_type))
            # self.__send_packet(Packet.UNRECOGNIZED_HEADER, "Unrecognized header {}".format(packet_type))

    def send_certificate(self, filename):
        self.__connect()
        self.__start_sending_certificate(filename)


    # Internal Loops

    def __start_sending_file(self, filename):
        f = open(os.path.join(self.__files_path, filename), 'r')
        self.__send_packet(Packet.START_OF_FILE, filename)
        resp_packet_type, resp_message = self.__receive_packet()
        message = f.read(FRAME_LENGTH/8)
        while resp_packet_type == Packet.READY_TO_RECEIVE_PART and message:
            self.__send_packet(Packet.FILE_PART, message)
            resp_packet_type, resp_message = self.__receive_packet()
            message = f.read(FRAME_LENGTH/8)
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            self.__send_packet(Packet.END_OF_FILE, "End of file.")

    def __start_receiving_file(self, filename):
        print("$ ENTER INTERNAL LOOP __start_receiving_file\n")
        # Calls __create_file which returns a status and message
        resp_packet_type, resp_message = self.__create_file(filename)
        # sends status and message back
        self.__send_packet(resp_packet_type, resp_message)
        # if status is ready, then enter loop
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            while resp_packet_type == Packet.READY_TO_RECEIVE_PART:
                # we start waiting HERE for new packets from the connection
                recv_packet_type, recv_message = self.__receive_packet()
                # if file part, append
                if recv_packet_type == Packet.FILE_PART:
                    # calls __append_file which returns a status and message
                    resp_packet_type, resp_message = self.__append_file(filename, recv_message)
                    # sends status and message back
                    self.__send_packet(resp_packet_type, resp_message)
                elif recv_packet_type == Packet.END_OF_FILE:
                    print("$ LEAVE INTERNAL LOOP __start_receiving_file\n")
                    break
                else:
                    self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected {}".format(recv_packet_type), addr)
                    print("$ LEAVE INTERNAL LOOP __start_receiving_file\n")
                    break
        else:
            print("$ LEAVE INTERNAL LOOP __start_receiving_file\n")

    def __start_sending_certificate(self, filename):
        f = open(os.path.join(self.__certificate_path, filename), 'r')
        self.__send_packet(Packet.START_OF_CERTIFICATE, filename)
        resp_packet_type, resp_message = self.__receive_packet()
        message = f.read(FRAME_LENGTH/8)
        while resp_packet_type == Packet.READY_TO_RECEIVE_PART and message:
            self.__send_packet(Packet.CERTIFICATE_PART, message)
            resp_packet_type, resp_message = self.__receive_packet()
            message = f.read(FRAME_LENGTH/8)
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            self.__send_packet(Packet.END_OF_CERTIFICATE, "End of certificate.")


    # File I/O

    # Creates the file
    def __create_file(self, filename):
        filepath = os.path.join(self.__files_path, filename)
        if not os.path.isfile(filepath):
            with open(filepath, 'w+') as open_file:
                return Packet.READY_TO_RECEIVE_PART, "File successfully created"
        else:
            return Packet.FILE_ALREADY_EXISTS, "File already exists"

    # Creates the file
    def __append_file(self, filename, contents):
        filepath = os.path.join(self.__files_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'a') as open_file:
                open_file.write(contents)
                return Packet.READY_TO_RECEIVE_PART, "File successfully appended"
        else:
            return Packet.FILE_DOESNT_EXIST, "File doesn't exist"


    # Connections and basic communication

    def __connect(self):
        self.__s.connect((self.__host, self.__port))

    def __send_packet(self, packet_type, message=""):
        print("- SENDING PACKET {}".format(packet_type))
        print("{}\n".format(message))
        self.__s.send(self.__add_header(packet_type, message))
        # return self.__receive_packet()

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
