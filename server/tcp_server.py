import os
import sys
import subprocess
import socket
import ssl

from .vouch_handler import VouchHandler
from .helpers import ascii_to_length, length_in_binary, buffer_name, unbuffer_name
from .exceptions import *
from .packet import Packet


INITIAL_RECV_LENGTH = 2048


class TCPServer:

    def __init__(self, host='127.0.0.1', port=3002):
        self.__host = host
        self.__port = port
        self.__certfile_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'server.crt')
        self.__keyfile_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'server.key')
        self.__certificate_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db/certificates/')
        self.__files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db/files/')
        self.__vouch_handler = VouchHandler(self.__files_path, self.__certificate_path)
        print("$ Ready to serve.")

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

            ssl_soc = ssl.wrap_socket(c, server_side=True, certfile=self.__certfile_path, keyfile=self.__keyfile_path)

            self.__receive_first_packet_from_connection(ssl_soc, addr)

    # Connections and basic communication

    def __receive_first_packet_from_connection(self, c, addr):
        data = c.recv(INITIAL_RECV_LENGTH)
        while data:
            if not data:
                print("$ Connection from {} closed (no data)\n".format(addr))
                c.close()
                return

            packet_type = self.__read_header(data)
            message = self.__strip_header(data)
            print("- RECEIVING PACKET {}".format(packet_type))
            print("{}\n".format(message))

            # Act on the data and retrieve response
            # send_packet_type, send_message = self.__perform_action(c, packet_type, message)
            self.__handle_first_packet(c, addr, packet_type, message)

            data = c.recv(INITIAL_RECV_LENGTH)
        print("$ Connection from {} closed\n".format(addr))



    ''' ------------------------------------------------------------------------
    This is the home of the good stuff: initial
    incoming packets pass through here
    -------------------------------------------------------------------------'''
    # We pass addr in for future logging
    def __handle_first_packet(self, c, addr, packet_type, message):

        # START_OF_FILE
        if packet_type == Packet.START_OF_FILE:
            length, filename = self.__interpret_start_of_file(message)
            print("$ ENTER INTERNAL LOOP __start_receiving_file\n")
            self.__start_receiving_file(c, addr, int(length), filename)
            print("$ LEAVE INTERNAL LOOP __start_receiving_file\n\n")

        # START_OF_CERTIFICATE
        elif packet_type == Packet.START_OF_CERTIFICATE:
            filename = unbuffer_name(message)
            print("$ ENTER INTERNAL LOOP __start_receiving_certificate\n")
            self.__start_receiving_certificate(c, addr, filename)
            print("$ LEAVE INTERNAL LOOP __start_receiving_certificate\n\n")

        # REQUEST_FILE
        elif packet_type == Packet.REQUEST_FILE:
            print("$ ENTER INTERNAL LOOP __send_file\n")
            self.__send_file(c, addr, message)
            print("$ LEAVE INTERNAL LOOP __send_file\n\n")

        # REQUEST_FILE_LIST
        elif packet_type == Packet.REQUEST_FILE_LIST:
            self.__send_file_list(c, addr)

        # VOUCH_FOR_FILE
        elif packet_type == Packet.VOUCH_FOR_FILE:
            filename, certname = self.__interpret_vouch_for_file(message)
            self.__handle_vouch(c, addr, filename, certname)

        # Other headers should only arrive after entering an internal loop
        # or should only be received by client.
        else:
            self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected header {}".format(packet_type), addr)
            print("Received unexpected header {}.\n".format(packet_type))
    ''' ------------------------------------------------------------------------
    -------------------------------------------------------------------------'''




    # Internal Loops

    def __start_receiving_file(self, c, addr, length, filename):
        # Calls __create_file which returns a status and message
        resp_packet_type, resp_message = self.__create_file(filename)
        # sends status and message back
        self.__send_packet(c, resp_packet_type, resp_message, addr)
        # if status is ready, then enter loop
        if resp_packet_type == Packet.READY_TO_RECEIVE:
            # we start waiting HERE for new packets from the connection
            recv_packet_type, recv_message = self.__receive_packet(c)
            # recv_packet_type, recv_message = self.__receive_packet_with_content_of_length(c, length)
            # if file, append
            if recv_packet_type == Packet.FILE_CONTENT:
                # calls __append_file which returns a status and message
                resp_packet_type, resp_message = self.__append_file(filename, recv_message)
                # sends status and message back
                self.__send_packet(c, resp_packet_type, resp_message, addr)
            else:
                self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected {}".format(recv_packet_type), addr)

    def __start_receiving_certificate(self, c, addr, filename):
        # Calls __create_file which returns a status and message
        resp_packet_type, resp_message = self.__create_certificate(filename)
        # sends status and message back
        print "WHYY", resp_packet_type, resp_message
        self.__send_packet(c, resp_packet_type, resp_message, addr)
        # if status is ready, then enter loop
        if resp_packet_type == Packet.READY_TO_RECEIVE_CERTIFICATE:
            # we start waiting HERE for new packets from the connection
            recv_packet_type, recv_message = self.__receive_packet(c)
            # if file part, append
            if recv_packet_type == Packet.CERTIFICATE_CONTENT:
                # calls __append_file which returns a status and message
                resp_packet_type, resp_message = self.__append_certificate(filename, recv_message)
                # sends status and message back
                self.__send_packet(c, resp_packet_type, resp_message, addr)
            else:
                self.__send_packet(c, Packet.UNEXPECTED_HEADER, "Unexpected {}".format(recv_packet_type), addr)

    def __send_file(self, c, addr, message):
        desired_circumference, name, filename = self.__interpret_file_request(message)

        if not self.__vouch_handler.does_file_exist(filename):
            res_message = "File not found: {}".format(repr(filename))
            self.__send_packet(c, Packet.FILE_DOESNT_EXIST, res_message, addr)
            return

        circum = self.__vouch_handler.get_circle_length(filename, name)

        if desired_circumference > circum:
            self.__send_packet(c, Packet.FILE_NOT_VOUCHED,
                               "Only {} people have vouched for this file.".format(circum), addr)
        else:
            file_content = open(os.path.join(self.__files_path, filename), 'r').read()
            file_content_length = length_in_binary(file_content)
            # file_content_length = chr(len(file_content))

            # Send START_OF_FILE
            self.__send_packet(c, Packet.START_OF_FILE, file_content_length, addr)
            # Receive READY_TO_RECEIVE
            recv_packet_type, recv_message = self.__receive_packet(c)
            if recv_packet_type == Packet.READY_TO_RECEIVE:
                # Send FILE_CONTENT
                self.__send_packet(c, Packet.FILE_CONTENT, file_content, addr)

    def __send_file_list(self, c, addr):
        listDir = os.listdir(self.__files_path)
        # Assume list is less than one packet
        out = "Files:\n"

        for filename in listDir:
            out = out + "Filename: \n" + filename
            out = out + "\nVouched by: \n" + self.__vouch_handler.list_vouches(filename)
            out = out + "Length of: " + str(self.__vouch_handler.get_circle_length(filename, ""))

        self.__send_packet(c, Packet.FILE_LIST, out, addr)


    def __handle_vouch(self, c, addr, filename, certname):

        try:
            self.__vouch_handler.add_vouch(filename, certname)
        except NoFileError as e:
            self.__send_packet(c, Packet.FILE_DOESNT_EXIST, "File does not exist {}".format(filename), addr)
            return
        except NoCertificateError as e:
            self.__send_packet(c, Packet.CERTIFICATE_DOESNT_EXIST, "Certificate does not exist {}".format(certname), addr)
            return

        self.__send_packet(c, Packet.FILE_SUCCESSFULLY_VOUCHED, "Successfully vouched for {} with {}".format(filename, certname), addr)


    # We pass addr in for future logging
    def __send_packet(self, c, packet_type, message, addr):
        print "+ SENDING PACKET {}".format(repr(packet_type))
        print "{}".format(repr(message)), "\n"
        c.send(self.__add_header(packet_type, message))

    def __receive_packet(self, c):
        packet = c.recv(INITIAL_RECV_LENGTH)
        recv_header, recv_message =  self.__split_packet(packet)
        print "- RECEIVING PACKET {}".format(repr(recv_header))
        print "{}".format(repr(recv_message)), "\n"
        return recv_header, recv_message

    def __receive_packet_with_content_of_length(self, c, length):
        packet = c.recv(length+3)
        recv_header, recv_message =  self.__split_packet(packet)
        print "- RECEIVING PACKET {}".format(repr(recv_header))
        print "{}".format(repr(recv_message)), "\n"
        return recv_header, recv_message

    # Packet formatting

    def __split_packet(self, packet):
        return self.__read_header(packet), self.__strip_header(packet)

    # decrypts the request file header
    def __interpret_file_request(self, message):
        desired_circumference = ord(message[0])
        name = "" if ord(message[1]) == 0 else message[ 2 : 2+Packet.MAX_NAME_LENGTH ]
        filename = message[2+Packet.MAX_NAME_LENGTH:] if name else message[2:]

        name = unbuffer_name(name)
        filename = unbuffer_name(filename)

        return desired_circumference, name, filename

    # decrypts the request file header
    def __interpret_start_of_file(self, message):
        length_ascii = message[0:4]
        filename = unbuffer_name(message[4:])
        length = ascii_to_length(length_ascii)
        return length, filename

    def __interpret_vouch_for_file(self, message):
        filename = unbuffer_name(message[0:Packet.MAX_NAME_LENGTH])
        certname = unbuffer_name(message[Packet.MAX_NAME_LENGTH:2*Packet.MAX_NAME_LENGTH])
        return filename, certname

    def __add_header(self, packet_type, message):
        if not message:
            return packet_type
        else:
            return packet_type + message

    def __strip_header(self, packet):
        return packet[3:]

    def __read_header(self, packet):
        return packet[0:3]

    # Actions. All of these must return (PacketHeader, Message)

    # Creates the file
    def __create_file(self, filename):
        filepath = os.path.join(self.__files_path, filename)
        with open(filepath, 'w+') as open_file:
            self.__vouch_handler.add_file(filename)
            return Packet.READY_TO_RECEIVE, "File successfully created"

    # Creates the file
    def __append_file(self, filename, contents):
        filepath = os.path.join(self.__files_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'a') as open_file:
                open_file.write(contents)
                self.__vouch_handler.add_file(filename)
                return Packet.SUCCESSFULLY_ADDED, "File successfully appended"
        else:
            return Packet.FILE_DOESNT_EXIST, "File doesn't exist"

    # Creates the cert
    def __create_certificate(self, filename):
        filepath = os.path.join(self.__certificate_path, filename)
        if not os.path.isfile(filepath):
            with open(filepath, 'w+') as open_file:
                return Packet.READY_TO_RECEIVE_CERTIFICATE, "Certificate successfully created"
        else:
            return Packet.CERTIFICATE_ALREADY_EXISTS, "Certificate already exists"

    # Creates the cert
    def __append_certificate(self, filename, contents):
        filepath = os.path.join(self.__certificate_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'a') as open_file:
                open_file.write(contents)
                return Packet.SUCCESSFULLY_ADDED, "Certificate successfully appended"
        else:
            return Packet.CERTIFICATE_DOESNT_EXIST, "Certificate doesn't exist"

    # Networks

    def __attempt_to_bind(self):
        host = self.__host
        port = self.__port
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
