import sys, shlex, socket, subprocess, atexit, os

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

    UNRECOGNIZED_HEADER = '500'
    UNEXPECTED_HEADER = '501'


class TCPServer:

    def __init__(self, host='127.0.0.1', port=3002):
        self.host = host
        self.port = port
        self.certificate_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certificates/')
        self.files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files/')


    # Networking helpers

    def serve_forever(self):
        self.__attempt_to_bind()
        self.s.listen(1)
        print("$ Listening on {}:{}\n".format(self.host, self.port))
        self.__enter_loop()

    def __enter_loop(self):
        while True:
            c, addr = self.s.accept()
            print("\n$ Connection from {} accepted\n".format(addr))
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
        elif packet_type == Packet.FILE_PART:
            self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected header {}".format(packet_type), addr)
        elif packet_type == Packet.END_OF_FILE:
            self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected header {}".format(packet_type), addr)
        else:
            self.__send_packet(c, Packet.UNRECOGNIZED_HEADER, "Unrecognized header {}".format(packet_type), addr)

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


    # Internal Loops

    def __start_receiving_file(self, c, addr, filename):
        print("$ ENTER INTERNAL LOOP\n")
        # Calls __create_file which returns a status and message
        resp_packet_type, resp_message = self.__create_file(filename)
        # sends status and message back
        self.__send_packet(c, resp_packet_type, resp_message, addr)
        # if status is ready, then enter loop
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
                # TODO: Send confirmation?
                print("File receiving completed. Perhaps do something here")
                print("LEAVE INTERNAL LOOOP")
                break
            else:
                self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected {}".format(recv_packet_type), addr)
                break


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
        filepath = os.path.join(self.files_path, filename)
        if not os.path.isfile(filepath):
            with open(filepath, 'w+') as open_file:
                return Packet.READY_TO_RECEIVE_PART, "File successfully created"
        else:
            return Packet.FILE_ALREADY_EXISTS, "File already exists"

    # Creates the file
    def __append_file(self, filename, contents):
        filepath = os.path.join(self.files_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'a') as open_file:
                open_file.write(contents)
                return Packet.READY_TO_RECEIVE_PART, "File successfully appended"
        else:
            return Packet.FILE_DOESNT_EXIST, "File doesn't exist"


    # Networks

    def __attempt_to_bind(self):
        host = self.host
        port = self.port
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
