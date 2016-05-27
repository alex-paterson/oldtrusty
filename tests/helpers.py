from packet import Packet


def length_in_binary(the_file):
    length = len(the_file)

    length_rep = [chr(0)] * 4
    for i in range(4):
        length_rep[i] = chr(length % 256)
        length = int(length / 256)
        if length == 0:
            break

    return ''.join(length_rep)

def ascii_to_length(length_ascii):
    length = 1
    for c in length_ascii:
        if c == chr(0):
            break
        length *= ord(c)
    return length

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
