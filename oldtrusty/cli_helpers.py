import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Secure file storage.')

    # DONE
    parser.add_argument('-a','--filename',
        help='(filename) - Add or replace a file on the server') # required=True)

    parser.add_argument('-c','--number',
        help='(number) - Provide the required circumference (length) of a circle of trust')

    # DONE
    parser.add_argument('-f','--fetch',
        help='(filename) - Fetch an existing file from the oldtrusty server (send to stdout)')

    # DONE
    parser.add_argument('-ho','--host',
        help='(hostname:port) - Provide the remote address hosting the oldtrusty server')

    parser.add_argument('-l','--l',
        help='List all stored files and how they are protected')

    parser.add_argument('-n','--name',
        help='(name) Require a circle of trust to involve the named person (i.e. their certificate)')

    # DONE
    parser.add_argument('-u','--certificate',
        help='(filename) Upload a certificate to the server')

    parser.add_argument('-v','--vouch',
        help='(filename certificate) Vouch for the authenticity of an existing file on the server using the indicated certificate')

    return parser.parse_args()
