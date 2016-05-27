import socket
import ssl

from test import test
from tests import *


s = socket.socket()
s = ssl.wrap_socket(s)
# s = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED)
s.connect(('127.0.0.1',3002))

test(test_add_new_file, s)

test(test_add_existing_file, s)

test(test_get_file_plain, s)

test(test_get_nonexistent_file, s)

test(test_get_unvouched_file_with_trust_circle_diameter_one, s)

test(test_vouch_for_unvouched_file_with_non_extistent_certificate, s)

test(test_add_new_certificate, s)

test(test_get_singly_vouched_file_with_trust_circle_diameter_one, s)
