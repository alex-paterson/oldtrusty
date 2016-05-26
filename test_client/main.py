import socket

from test import test
from tests import *


s = socket.socket()
s.connect(('127.0.0.1',3002))

test(test_add_new_file, s)

test(test_add_existing_file, s)

test(test_get_file_plain, s)
