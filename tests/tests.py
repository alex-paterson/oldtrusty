import random

from packet import Packet
from helpers import length_in_binary, read_in_file
from test import check_packet_header, check_packet_body

file_one_content = "I'm a file full of good stuff."
filename_one = "{}.txt".format(''.join([random.choice('abcdefghijk123') for _ in range(10)]))


certificate_one_content = read_in_file('files/1/test.cert')

def test_add_new_file(s):

    # First we send a START_OF_FILE
    packet = Packet.START_OF_FILE + length_in_binary(file_one_content) + filename_one
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
    packet = Packet.START_OF_FILE + length_in_binary(file_one_content) + filename_one
    s.send(packet)
    res = s.recv(2048)
    # Confirm we got FILE_ALREADY_EXISTS
    check_packet_header(1, res, Packet.FILE_ALREADY_EXISTS)


def test_get_file_plain(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(0) + chr(0) + filename_one
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
    packet = Packet.REQUEST_FILE + chr(0) + chr(0) + "i_do_not_exist"
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(1, res, Packet.FILE_DOESNT_EXIST)

def test_get_unvouched_file_with_trust_circle_diameter_one(s):

    # First we send a REQUEST_FILE
    packet = Packet.REQUEST_FILE + chr(1) + chr(0) + filename_one
    s.send(packet)
    res = s.recv(2048)
    # Confirm we got FILE_NOT_VOUCHED
    check_packet_header(1, res, Packet.FILE_NOT_VOUCHED)


def test_add_new_certificate(s):

    # First we send a START_OF_CERTIFICATE
    packet = Packet.START_OF_CERTIFICATE + length_in_binary(file_one_content) + filename_one
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(1, res, Packet.READY_TO_RECEIVE)


    # Granted we get READY_TO_RECEIVE, we sent the content
    packet = Packet.FILE_CONTENT + file_one_content
    s.send(packet)
    res = s.recv(2048)
    check_packet_header(2, res, Packet.SUCCESSFULLY_ADDED)
