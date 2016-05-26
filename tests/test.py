class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def test(function, s):
    print "\n{}*** Testing {} ***{}".format(bcolors.OKGREEN, function.__name__, bcolors.ENDC)
    try:
        function(s)
    except ValueError as e:
        print u"{}\u2717{} {} failed:".format(bcolors.FAIL, bcolors.ENDC, function.__name__), e
    raw_input("\nPress any key for next test")


def check_packet_header(test_num, res, expected_header):
    res_code = res[0:3]
    if res_code != expected_header:
        raise ValueError("{}. expected response code of {}, got {}".format(test_num, repr(expected_header), repr(res_code)))
    else:
        print u"{}\u2713{} PASS: HEADER:".format(bcolors.OKGREEN, bcolors.ENDC), repr(res[3:])


def check_packet_body(test_num, res, expected_body):
    body = res[3:]
    if body != expected_body:
        raise ValueError("{}. expected body of {}, got {}".format(test_num, repr(expected_body), repr(body)))
    else:
        print u"{}\u2713{} PASS: BODY:".format(bcolors.OKGREEN, bcolors.ENDC), repr(res[3:])
