def length_in_binary(the_file):
    length = len(the_file)

    length_rep = [chr(0)] * 4
    for i in range(4):
        length_rep[i] = chr(length % 256)
        length = int(length / 256)
        if length == 0:
            break

    return ''.join(length_rep)


def check_packet_header(test_num, res, expected_header):
    res_code = res[0:3]
    if res_code != expected_header:
        raise ValueError("{}. expected response code of 200, got {}".format(test_num, repr(res_code)))
    else:
        print "PASS:", repr(res[3:])
