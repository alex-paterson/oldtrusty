import sys, shlex, socket, subprocess, atexit, os


class Packet:
    READY_TO_RECEIVE_FILE = '001'
    FILE = '101'
    CERTIFICATE = '102'
    SUCCESSFULLY_SAVED_FILE = '201'
    SUCCESSFULLY_SAVED_CERTIFICATE = '202'
    FILE_ALREADY_EXISTS = '401'
    UNRECOGNIZED_HEADER = '999'


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
        print("Listening on {}:{}".format(self.host, self.port))
        self.__enter_loop()

    def __enter_loop(self):
        while True:
            c, addr = self.s.accept()
            print("Connection from {} accepted.".format(addr))
            self.__receive_packet_from_connection(c, addr)



    # Connections and basic communication

    def __connect(self):
        self.__s.connect((self.__host, self.__port))

    def __receive_packet_from_connection(self, c, addr):
        # Receive new data
        data = c.recv(1024)
        if not data:
            c.close()
            print("Connection from {} closed.".format(addr))
        print("From {}: {}".format(addr, data))
        packet_type = self.__read_header(data)
        message = self.__strip_header(data)

        # Act on the data and retrieve response
        send_packet_type, send_message = self.__perform_action(packet_type, message)

        # Second response
        self.__respond_with_packet(c, send_packet_type, send_message, addr)

    def __respond_with_packet(self, c, packet_type, message, addr):
        c.send(self.__add_header(packet_type, message))
        print("To {}: {}: {}".format(addr, packet_type, message))

    def __perform_action(self, packet_type, message):
        if packet_type == Packet.FILE:
            return self.__create_file("noname.txt", message)
        else:
            return Packet.UNRECOGNIZED_HEADER, "Unrecognized header {}".format(packet_type)


    # Packet formatting

    def __add_header(self, packet_type, message):
        return packet_type + message

    def __strip_header(self, packet):
        return packet[3:-1]

    def __read_header(self, packet):
        return packet[0:3]


    # ACTIONS. ALL OF THESE MUST RETURN (PacketHeader, Message)

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

    # Creates the file
    def __create_file(self, filename, contents):
        filepath = os.path.join(self.files_path, filename)
        if not os.path.isfile(filepath):
            with open(filepath, 'w+') as open_file:
                open_file.write(contents)
                return Packet.SUCCESSFULLY_SAVED_FILE, "File {} successfully saved".format(filename)
        else:
            return Packet.FILE_ALREADY_EXISTS, "File {} already exists".format(filename)


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
