from packet import Packet
from helpers import length_in_binary, ascii_to_length, \
                    read_in_file, buffer_name, unbuffer_name, \
                    random_name
from test import check_packet_header, check_packet_body

file_one_content = "I'm a file full of good stuff."
filename_one = "{}.txt".format(random_name())

certificate_one_content = read_in_file('files/A/A.cert')
certificate_two_content = read_in_file('files/B/B.cert')
certificate_three_content = read_in_file('files/C/C.cert')
certificate_one_name = "{}.cert".format(random_name())
certificate_two_name = "{}.cert".format(random_name())
certificate_three_name = "{}.cert".format(random_name())

certificate_AB = read_in_file('files/A/AsignedbyB.crt')
certificate_BA = read_in_file('files/B/BsignedbyA.crt')
certificate_CA = read_in_file('files/C/CsignedbyA.crt')
certificate_AC = read_in_file('files/A/AsignedbyC.crt')
certificate_CB = read_in_file('files/C/CsignedbyB.crt')
certificate_AB_name = "{}.crt".format(random_name())
certificate_BA_name = "{}.crt".format(random_name())
certificate_CA_name = "{}.crt".format(random_name())
certificate_AC_name = "{}.crt".format(random_name())
certificate_CB_name = "{}.crt".format(random_name())

def test_add_new_file(s):

    # First we send a START_OF_FILE
    packet = Packet.START_OF_FILE + length_in_binary(file_one_content) + buffer_name(filename_one)
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(1, res, Packet.READY_TO_RECEIVE)


    # Granted we get READY_TO_RECEIVE, we sent the content
    packet = Packet.FILE_CONTENT + file_one_content
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)


def test_add_existing_file(s):

    # First we send a START_OF_FILE
    packet = Packet.START_OF_FILE + length_in_binary(file_one_content) + buffer_name(filename_one)
    s.send(packet)
    res = s.recv(2048)
    # Confirm we got READY_TO_RECEIVE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE)


    # Granted we get READY_TO_RECEIVE, we sent the content
    packet = Packet.FILE_CONTENT + file_one_content
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)


def test_get_file_plain(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(0) + chr(0) + buffer_name(filename_one)
    s.send(packet)
    res = s.recv(2048)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.START_OF_FILE)

    # Send READY_TO_RECEIVE
    packet = Packet.READY_TO_RECEIVE
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(2, res, Packet.FILE_CONTENT)
    check_packet_body(2, res, file_one_content)


def test_get_nonexistent_file(s):

    # First we send a START_OF_FILE
    packet = Packet.REQUEST_FILE + chr(0) + chr(0) + buffer_name("i_do_not_exist.txt")
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(1, res, Packet.FILE_DOESNT_EXIST)


def test_get_unvouched_file_with_trust_circle_diameter_one(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(1) + chr(0) + buffer_name(filename_one)
    s.send(packet)
    res = s.recv(2048)
    # Confirm we got FILE_NOT_VOUCHED
    check_packet_header(1, res, Packet.FILE_NOT_VOUCHED)


def test_vouch_for_unvouched_file_with_non_extistent_certificate(s):

    # First we send a VOUCH_FOR_FILE
    packet = Packet.VOUCH_FOR_FILE + buffer_name(filename_one) + buffer_name("i_do_not_exist.cert")
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    check_packet_header(1, res, Packet.CERTIFICATE_DOESNT_EXIST)


def test_add_new_certificate(s):

    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_one_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE_CERTIFICATE)

    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_one_content
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)


def test_add_existing_certificate(s):

    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_one_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got CERTIFICATE_ALREADY_EXISTS
    check_packet_header(1, res, Packet.CERTIFICATE_ALREADY_EXISTS)


def test_vouch_for_nonexistent_file(s):

    # First we send a VOUCH_FOR_FILE
    packet = Packet.VOUCH_FOR_FILE + buffer_name("i_do_not_exist.txt") + buffer_name(certificate_one_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    check_packet_header(1, res, Packet.FILE_DOESNT_EXIST)


def test_vouch_for_unvouched_file(s):

    # First we send a VOUCH_FOR_FILE
    packet = Packet.VOUCH_FOR_FILE + buffer_name(filename_one) + buffer_name(certificate_one_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    check_packet_header(1, res, Packet.FILE_SUCCESSFULLY_VOUCHED)


def test_get_singly_vouched_file_with_trust_circle_diameter_one(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(1) + chr(0) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.START_OF_FILE)

    file_length = ascii_to_length(res[3:8])

    # Send a READY_TO_RECEIVE
    packet = Packet.READY_TO_RECEIVE
    print "Sending packet: ", repr(packet)
    print "File length: ", file_length
    s.send(packet)
    res = s.recv(file_length+3)
    print "Received packet: ", repr(res)
    # Confirm we got FILE_CONTENT
    check_packet_header(2, res, Packet.FILE_CONTENT)
    check_packet_body(3, res, file_one_content)


def test_get_singly_vouched_file_with_trust_circle_diameter_one_and_nonexistent_name(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(1) + chr(1) + buffer_name("idon'texist.cert") + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got CERTIFICATE_DOESNT_EXIST
    check_packet_header(1, res, Packet.FILE_NOT_VOUCHED)


def test_get_singly_vouched_file_with_trust_circle_diameter_two(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(2) + chr(0) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got CERTIFICATE_DOESNT_EXIST
    check_packet_header(1, res, Packet.FILE_NOT_VOUCHED)


def test_get_singly_vouched_file_with_trust_circle_diameter_one_and_name(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(1) + chr(1) + buffer_name(certificate_one_name) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.START_OF_FILE)

    file_length = ascii_to_length(res[3:8])

    # Send a READY_TO_RECEIVE
    packet = Packet.READY_TO_RECEIVE
    print "Sending packet: ", repr(packet)
    print "File length: ", file_length
    s.send(packet)
    res = s.recv(file_length+3)
    print "Received packet: ", repr(res)
    # Confirm we got FILE_CONTENT
    check_packet_header(2, res, Packet.FILE_CONTENT)
    check_packet_body(3, res, file_one_content)


def test_vouch_for_singly_vouched_file(s):

    # Need to upload another cert first:

    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_two_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE_CERTIFICATE)

    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_two_content
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)


    # First we send a VOUCH_FOR_FILE
    packet = Packet.VOUCH_FOR_FILE + buffer_name(filename_one) + buffer_name(certificate_two_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    check_packet_header(3, res, Packet.FILE_SUCCESSFULLY_VOUCHED)


def test_get_diameter_one_file_with_trust_circle_diameter_two(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(2) + chr(0) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got CERTIFICATE_DOESNT_EXIST
    check_packet_header(1, res, Packet.FILE_NOT_VOUCHED)


def test_vouch_for_doubly_vouched_file(s):

    # Need to upload another cert first:

    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_three_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE_CERTIFICATE)

    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_three_content
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)


    # First we send a VOUCH_FOR_FILE
    packet = Packet.VOUCH_FOR_FILE + buffer_name(filename_one) + buffer_name(certificate_three_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    check_packet_header(3, res, Packet.FILE_SUCCESSFULLY_VOUCHED)


def test_get_file_with_trust_circle_diameter_two_and_name(s):
    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_AB_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE_CERTIFICATE)
    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_AB
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)

    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_BA_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(3, res, Packet.READY_TO_RECEIVE_CERTIFICATE)
    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_BA
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(4, res, Packet.SUCCESSFULLY_ADDED)


    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(2) + chr(1) + buffer_name(certificate_one_name) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(5, res, Packet.START_OF_FILE)

    file_length = ascii_to_length(res[3:8])

    # Send a READY_TO_RECEIVE
    packet = Packet.READY_TO_RECEIVE
    print "Sending packet: ", repr(packet)
    print "File length: ", file_length
    s.send(packet)
    res = s.recv(file_length+3)
    print "Received packet: ", repr(res)
    # Confirm we got FILE_CONTENT
    check_packet_header(6, res, Packet.FILE_CONTENT)
    check_packet_body(7, res, file_one_content)

def test_get_diameter_two_file_with_trust_circle_diameter_three_and_name(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(3) + chr(1) + buffer_name(certificate_one_name) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(5, res, Packet.FILE_NOT_VOUCHED)

def test_get_incomplete_diameter_three_file_with_trust_circle_diameter_three(s):
    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_CA_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE_CERTIFICATE)
    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_CA
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(3) + chr(0) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(3, res, Packet.FILE_NOT_VOUCHED)

def test_get_incomplete_diameter_three_file_with_trust_circle_diameter_three_2(s):
    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_AC_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE_CERTIFICATE)
    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_AC
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(3) + chr(0) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(3, res, Packet.FILE_NOT_VOUCHED)

def test_get_diameter_three_file_with_trust_circle_diameter_three(s):
    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + buffer_name(certificate_CB_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(1, res, Packet.READY_TO_RECEIVE_CERTIFICATE)
    # Send a CERTIFICATE_CONTENT
    packet = Packet.CERTIFICATE_CONTENT + certificate_CB
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got SUCCESSFULLY_ADDED
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(3) + chr(0) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(3, res, Packet.START_OF_FILE)

    file_length = ascii_to_length(res[3:8])

    # Send a READY_TO_RECEIVE
    packet = Packet.READY_TO_RECEIVE
    print "Sending packet: ", repr(packet)
    print "File length: ", file_length
    s.send(packet)
    res = s.recv(file_length+3)
    print "Received packet: ", repr(res)
    # Confirm we got FILE_CONTENT
    check_packet_header(6, res, Packet.FILE_CONTENT)
    check_packet_body(7, res, file_one_content)

def test_get_diameter_three_file_with_trust_circle_diameter_three_and_name(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(3) + chr(1) + buffer_name(certificate_one_name) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(3, res, Packet.START_OF_FILE)

    file_length = ascii_to_length(res[3:8])

    # Send a READY_TO_RECEIVE
    packet = Packet.READY_TO_RECEIVE
    print "Sending packet: ", repr(packet)
    print "File length: ", file_length
    s.send(packet)
    res = s.recv(file_length+3)
    print "Received packet: ", repr(res)
    # Confirm we got FILE_CONTENT
    check_packet_header(6, res, Packet.FILE_CONTENT)
    check_packet_body(7, res, file_one_content)

def test_get_diameter_three_file_with_trust_circle_diameter_four(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(4) + chr(1) + buffer_name(certificate_one_name) + buffer_name(filename_one)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(3, res, Packet.FILE_NOT_VOUCHED)
