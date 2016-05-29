Simon de Sancha - 21503324
Alex Paterson - 21497839


Dependencies
----------

Python server requires dependencies listed in requirements.txt. `pip install -r requirements.txt`

pyOpenSSL required libffi-dev on Ubuntu: `sudo apt-get install libffi-dev`

M2Crypto required swig on OSX: `brew install swig` and openSSL (not included by default on OSX El Capitan): `brew install openssl`

If M2Crypto not installing on OSX, try scripts/install_m2crypto_osx.sh

Server:
----------

Server written in python.
Satisfies all project requirements.
Further features include:
	Random number public key challenge to verify the client's identity on vouch.

Certificates live in server/db/certificates/
Stored files live in server/db/files/
All users should have a self-signed certificate present to help with chain verification.
Server SSL certificate and private key lives in server/ssl/    (provided)

tests/server/main.py 	runs a series of tests on the server. server/db/certificates must be empty for them all to pass.

To run server:
	python runserver.py -ip <IP to listen>


Client:
--------

Client written in Java.
Satisfies all project requirements.

Deviation from project spec:
	Server/client certificates are needed in the working directory.
	See client/CLIENT-NOTES for full details.

To build client:
	cd client;
	./build.sh;
	java -jar oldTrustyClient ....args;
