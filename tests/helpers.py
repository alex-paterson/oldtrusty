import struct
import random

from packet import Packet


def ascii_to_length(length_ascii):
    return struct.unpack(">i", length_ascii)[0]

def length_in_binary(the_file):
    length_rep = [chr(0)] * 4
    length_rep[0:4] = struct.pack(">i", len(the_file))
    return ''.join(length_rep)

def read_in_file(filepath):
    with open(filepath) as f:
        return f.read()

def buffer_name(name):
    name_length = len(name)
    buffer_length = Packet.MAX_NAME_LENGTH - name_length
    return name + buffer_length * chr(0)

def unbuffer_name(name):
    name_length = name.index(chr(0)) or Packet.MAX_NAME_LENGTH
    return name[0:name_length]

def random_name():
    return ''.join([random.choice('abcdefghijk123') for _ in range(10)])
