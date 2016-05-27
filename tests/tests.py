import random

from packet import Packet
from helpers import length_in_binary, ascii_to_length, read_in_file, buffer_name, unbuffer_name
from test import check_packet_header, check_packet_body

file_one_content = "I'm a file full of good stuff."
filename_one = "{}.txt".format(''.join([random.choice('abcdefghijk123') for _ in range(10)]))

certificate_one_content = read_in_file('files/A/A.cert')
certificate_one_name = "{}.cert".format(''.join([random.choice('abcdefghijk123') for _ in range(10)]))

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

    # Send a REQUEST_FILE
    packet = Packet.READY_TO_RECEIVE
    print "Sending packet: ", repr(packet)
    print "File length: ", file_length
    s.send(packet)
    res = s.recv(file_length)
    print "Received packet: ", repr(res)
    # Confirm we got START_OF_FILE
    check_packet_header(2, res, Packet.FILE_CONTENT)
    check_packet_body(3, res, file_one_content)
