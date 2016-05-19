import sys, shlex, socket, subprocess, atexit, os

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

    REQUEST_FILE_LIST = '502'
    LIST_PACKET = '510'


class TCPServer:

    def __init__(self, host='127.0.0.1', port=3002):
        self.__host = host
        self.__port = port
        self.__certificate_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certificates/')
        self.__files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files/')


    # Networking helpers

    def serve_forever(self):
        self.__attempt_to_bind()
        self.s.listen(1)
        print("$ Listening on {}:{}\n".format(self.__host, self.__port))
        self.__enter_loop()

    def __enter_loop(self):
        while True:
            c, addr = self.s.accept()
            print("\n\n\n$ Connection from {} accepted\n".format(addr))
            self.__receive_first_packet_from_connection(c, addr)


    # Connections and basic communication

    def __connect(self):
        self.__s.connect((self.__host, self.__port))

    def __receive_first_packet_from_connection(self, c, addr):
        # Receive new data
        data = c.recv(FRAME_LENGTH)
        if not data:
            print("$ Connection from {} closed\n".format(addr))
            c.close()

        packet_type = self.__read_header(data)
        message = self.__strip_header(data)
        print("- RECEIVING PACKET {}".format(packet_type))
        print("{}\n".format(message))

        # Act on the data and retrieve response
        # send_packet_type, send_message = self.__perform_action(c, packet_type, message)
        self.__handle_packet(c, addr, packet_type, message)

        # The first packet will make it obvious whether or not further packets
        # are coming. We'll enter an internal loop above if this is true. Hence
        # we close the connection if we make it down here
        c.close()
        print("$ Connection from {} closed\n".format(addr))


    # We pass addr in for future logging
    def __handle_packet(self, c, addr, packet_type, message):
        if packet_type == Packet.START_OF_FILE:
            filename = message
            self.__start_receiving_file(c, addr, filename)
        elif packet_type == Packet.START_OF_CERTIFICATE:
            filename = message
            self.__start_receiving_certificate(c, addr, filename)
        elif packet_type == Packet.REQUEST_FILE:
            filename = message
            self.__start_sending_file(c, addr, filename)
	elif packet_type == Packet.REQUEST_FILE_LIST:
            self.__send_file_list(c, addr)

            # Unexpected headers. These sould only arrive after entering an
            # internal loop.
        elif packet_type == Packet.FILE_PART:
            self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected header {}".format(packet_type), addr)
        elif packet_type == Packet.END_OF_FILE:
            self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected header {}".format(packet_type), addr)
        elif packet_type == Packet.CERTIFICATE_PART:
            self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected header {}".format(packet_type), addr)
        elif packet_type == Packet.END_OF_CERTIFICATE:
            self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected header {}".format(packet_type), addr)
        else:
            print("Received unexpected header {}.\n".format(packet_type))
            # self.__send_packet(c, Packet.UNRECOGNIZED_HEADER, "Unrecognized header {}".format(packet_type), addr)

    # Internal Loops

    def __start_receiving_file(self, c, addr, filename):
        print("$ ENTER INTERNAL LOOP __start_receiving_file\n")
        # Calls __create_file which returns a status and message
        resp_packet_type, resp_message = self.__create_file(filename)
        # sends status and message back
        self.__send_packet(c, resp_packet_type, resp_message, addr)
        # if status is ready, then enter loop
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            while resp_packet_type == Packet.READY_TO_RECEIVE_PART:
                # we start waiting HERE for new packets from the connection
                recv_packet_type, recv_message = self.__receive_packet(c)
                # if file part, append
                if recv_packet_type == Packet.FILE_PART:
                    # calls __append_file which returns a status and message
                    resp_packet_type, resp_message = self.__append_file(filename, recv_message)
                    # sends status and message back
                    self.__send_packet(c, resp_packet_type, resp_message, addr)
                elif recv_packet_type == Packet.END_OF_FILE:
                    print("$ LEAVE INTERNAL LOOP __start_receiving_file\n")
                    break
                else:
                    print("Received unexpected header {}.\n".format(recv_packet_type))
                    # self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected {}".format(recv_packet_type), addr)
                    print("$ LEAVE INTERNAL LOOP __start_receiving_file\n")
                    break
        else:
            print("$ LEAVE INTERNAL LOOP __start_receiving_file\n")

    def __start_receiving_certificate(self, c, addr, filename):
        print("$ ENTER INTERNAL LOOP __start_receiving_certificate\n")
        # Calls __create_file which returns a status and message
        resp_packet_type, resp_message = self.__create_certificate(filename)
        # sends status and message back
        self.__send_packet(c, resp_packet_type, resp_message, addr)
        # if status is ready, then enter loop
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            while resp_packet_type == Packet.READY_TO_RECEIVE_PART:
                # we start waiting HERE for new packets from the connection
                recv_packet_type, recv_message = self.__receive_packet(c)
                # if file part, append
                if recv_packet_type == Packet.CERTIFICATE_PART:
                    # calls __append_file which returns a status and message
                    resp_packet_type, resp_message = self.__append_certificate(filename, recv_message)
                    # sends status and message back
                    self.__send_packet(c, resp_packet_type, resp_message, addr)
                elif recv_packet_type == Packet.END_OF_CERTIFICATE:
                    print("$ LEAVE INTERNAL LOOP __start_receiving_certificate\n")
                    break
                else:
                    print("Received unexpected header {}.\n".format(recv_packet_type))
                    # self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected {}".format(recv_packet_type), addr)
                    print("$ LEAVE INTERNAL LOOP __start_receiving_certificate\n")
                    break
        else:
            print("$ LEAVE INTERNAL LOOP __start_receiving_certificate\n")

    def __start_sending_file(self, c, addr, filename):
        f = open(os.path.join(self.__files_path, filename), 'r')
        self.__send_packet(c, Packet.START_OF_FILE, filename, addr)
        resp_packet_type, resp_message = self.__receive_packet(c)
        message = f.read(FRAME_LENGTH/8)
        while resp_packet_type == Packet.READY_TO_RECEIVE_PART and message:
            self.__send_packet(c, Packet.FILE_PART, message, addr)
            resp_packet_type, resp_message = self.__receive_packet(c)
            message = f.read(FRAME_LENGTH/8)
        if resp_packet_type == Packet.READY_TO_RECEIVE_PART:
            self.__send_packet(c, Packet.END_OF_FILE, "End of file.", addr)

    def __send_file_list(self, c, addr):
	list = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files/'))
       
	# Assume list is less than one packet
	if len(list) < FRAME_LENGTH:
            self.__send_packet(c, Packet.LIST_PACKET, ',\n'.join(list), addr)

    # We pass addr in for future logging
    def __send_packet(self, c, packet_type, message, addr):
        print("+ SENDING PACKET {}".format(packet_type))
        print("{}\n".format(message))
        c.send(self.__add_header(packet_type, message))

    def __receive_packet(self, c):
        packet = c.recv(FRAME_LENGTH)
        recv_header, recv_message =  self.__split_packet(packet)
        print("- RECEIVING PACKET {}".format(recv_header))
        print("{}\n".format(recv_message))
        return recv_header, recv_message

    # Packet formatting

    def __split_packet(self, packet):
        return self.__read_header(packet), self.__strip_header(packet)

    def __add_header(self, packet_type, message):
        return packet_type + message

    def __strip_header(self, packet):
        return packet[3:]

    def __read_header(self, packet):
        return packet[0:3]


    # Actions. All of these must return (PacketHeader, Message)

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

    # Creates the cert
    def __create_certificate(self, filename):
        filepath = os.path.join(self.__certificate_path, filename)
        if not os.path.isfile(filepath):
            with open(filepath, 'w+') as open_file:
                return Packet.READY_TO_RECEIVE_PART, "Certificate successfully created"
        else:
            return Packet.CERTIFICATE_ALREADY_EXISTS, "Certificate already exists"

    # Creates the cert
    def __append_certificate(self, filename, contents):
        filepath = os.path.join(self.__certificate_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'a') as open_file:
                open_file.write(contents)
                return Packet.READY_TO_RECEIVE_PART, "Certificate successfully appended"
        else:
            return Packet.CERTIFICATE_DOESNT_EXIST, "Certificate doesn't exist"


    # Networks

    def __attempt_to_bind(self):
        host = self.__host
        port = self.__port
        self.s = socket.socket()
        try:
            self.s.bind((host, port))
        except socket.error as e:
            print(e)
            response = raw_input("Port already in use! Attempt to kill that process? (Y/n) ")
            if response == "Y":
                self.__force_open_port
            else:
                sys.exit("See you later, then!")
            self.s.bind((host, port))

    def __force_open_port(self):
        port = self.port
        print(subprocess.check_output(["lsof", "-i", ":{}".format(port)]))
        lsof = subprocess.Popen(["lsof", "-i", ":{}".format(port)], stdout=subprocess.PIPE)
        tail = subprocess.Popen(["tail", "-1"], stdin=lsof.stdout, stdout=subprocess.PIPE)
        tr = subprocess.Popen(["tr", "-s", "' '"], stdin=tail.stdout, stdout=subprocess.PIPE)
        PID = subprocess.check_output(["cut", "-d", " ", "-f", "2"], stdin=tr.stdout).strip()
        print("Killing process with PID: {}".format(PID))
        subprocess.call(["kill", "-9", "{}".format(PID)])


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
