from packet import Packet
from helpers import length_in_binary, ascii_to_length, \
                    read_in_file, buffer_name, unbuffer_name, \
                    random_name, solve_challenge, encrypt_solution
from test import check_packet_header, check_packet_body


file_one_content = "I'm a file full of good stuff."
filename_one = "{}.txt".format(random_name())

certificate_one_content = read_in_file('files/A/A.cert')
certificate_one_name = "{}.cert".format(random_name())

private_key_string = open('files/A/A.key').read()

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


def test_vouch_for_unvouched_file(s):

    # First we send a VOUCH_FOR_FILE
    packet = Packet.VOUCH_FOR_FILE + buffer_name(filename_one) + buffer_name(certificate_one_name)
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    check_packet_header(1, res, Packet.PUBKEY_CHALLENGE)

    solution = str(solve_challenge(res[3:], private_key_string))
    encrypted_solution = encrypt_solution(solution, private_key_string)

    packet = Packet.PUBKEY_RESPONSE + encrypted_solution
    print "Sending packet: ", repr(packet)
    s.send(packet)
    res = s.recv(2048)
    print "Received packet: ", repr(res)
    # Confirm we got FILE_SUCCESSFULLY_VOUCHED
    check_packet_header(2, res, Packet.FILE_SUCCESSFULLY_VOUCHED)
