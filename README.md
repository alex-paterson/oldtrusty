# Notes

## To Do

Right now files are send in packets of 1024 bytes. This is unnecessary, the packets can be as large as they need to be.

It's still good that the client/server send SOF and EOF packets which communicate whether or not the transfer *will* be valid, then whether or not the transfer *was* successful.

## Signing

to sign a CSR with specified private key, certificate

'''
openssl x509 -CAkey test.key -CA test.cert -in 1.csr -req -out 1.crt -CAcreateserial
'''

to generate new private key, certificate:

'''
openssl req -new -newkey rsa:1024 -days 365 -nodes -x509 -keyout test.key -out test.cert
'''

To generate CSR:

'''
openssl req -new -sha256 -key test.key -out 2.csr
'''

to display who signed the certificate:

openssl x509 -text -noout -in 1.crt

ie server will loop through all certificates, see who signed whos

# Client

## Notes

java client is compiled in ubuntu. see signing.txt for signing commands.

Note the the Identification being used to id a client is simply the 'common name' in the certificate, so this must be unique when creating your keys.

So far what is working:

create two seperate 'clients' (lets call them A and B) by creating 2 different private key pairs.

Create CSR's for both clients, get each other to sign them. Upload these signed certificates to the server using the client.

The server now knows A trusts B, B trusts A.

now upload a file, get both B to vouch for it using any certificate with its own common name. Get A to do the same.

Now when someone tries to fetch the file, it will find the circle length ( ie 2 ), and only respond if the length is great enough.

note server must start fresh (ie no existing files)
note client commands are fickly at the moment

to upload:

'''
java -jar oldTrustyClient.jar -a meme.txt -h 127.0.0.1:3002 -c 2
'''

vouch for meme.txt, using test.cert:

'''
java -jar ../../oldTrustyClient/dist/oldTrustyClient.jar -v meme.txt test.cert -h 127.0.0.1:3002 -c 2
'''

# Server

## Setup

First install pip with `sudo easy_install pip` on OSX or `sudo apt-get install python-pip python-dev build-essential` on Linux.

The install virtualenv with `sudo pip install --upgrade virtualenv`.

Then create a virtual environment in the project directory with `virtualenv venv`.

Then activate it with `source venv/bin/activate`.

Now run `python` to make sure it's python2.7. If it's not, start again, but create the virtualenv env with `virtualenv -p $PYTHON2PATH venv`. Where $PYTHON2PATH is the path to a Python2.7 installation.

If `python` outside of virtualenv if python2.7, you can run `which python` to get the path. python2.7 is probably fine also.

Then with the virtualenv activated install dependencies with `pip install -r requirements.txt`

Now you can run `python server.py` and `python client.py` without any missing dependencies.

To deactivate the virtualenv run `deactivate`.

## Usage

Run server:

```python
import socket
from oldtrusty import TCPServer

server = TCPServer()
server.serve_forever()
```
