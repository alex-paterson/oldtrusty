import struct
from .packet import Packet

def ascii_to_length(length_ascii):
    length = 1
    for c in length_ascii:
        if c == chr(0):
            break
        length *= ord(c)
    return length

def length_in_binary(the_file):
    length = len(the_file)

    length_rep = [chr(0)] * 4
    length_rep[0:4] = struct.pack(">i", length)

    return ''.join(length_rep)

def buffer_name(name):
    name_length = len(name)
    buffer_length = Packet.MAX_NAME_LENGTH - name_length
    return name + buffer_length * chr(0)

def unbuffer_name(name):
    try:
        name_length = name.index(chr(0))
    except ValueError as e:
        name_length = Packet.MAX_NAME_LENGTH
    return name[0:name_length]
