def length_in_binary(the_file):
    length = len(the_file)

    length_rep = [chr(0)] * 4
    for i in range(4):
        length_rep[i] = chr(length % 256)
        length = int(length / 256)
        if length == 0:
            break

    return ''.join(length_rep)

def read_in_file(filepath):
    with open(filepath) as f:
        return f.read()
