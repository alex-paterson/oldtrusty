# Notes

✗ 

## To Do

### ✓ Add files

✓ test_add_new_file

✓ test_add_existing_file

### ✓ Add certificates

✓ test_add_new_certificate

✓ test_add_existing_certificate

### ✓ Vouching for files

✓ test_vouch_for_unvouched_file

✓ test_vouch_for_nonexistent_file

✓ test_vouch_for_unvouched_file_with_non_extistent_certificate

✓ test_vouch_for_singly_vouched_file

✓ test_vouch_for_doubly_vouched_file

### ✓ Get Files

✓ test_get_file_plain

✓ test_get_nonexistent_file

✓ test_get_unvouched_file_with_trust_circle_diameter_one (error)


✓ test_get_singly_vouched_file_with_trust_circle_diameter_one

✓ test_get_singly_vouched_file_with_trust_circle_diameter_one_and_nonexistent_name (error)

✓ test_get_singly_vouched_file_with_trust_circle_diameter_one_and_name

✓ test_get_singly_vouched_file_with_trust_circle_diameter_two (error)


✓ test_get_diameter_one_file_with_trust_circle_diameter_two (error)

✓ test_get_file_with_trust_circle_diameter_two_and_name

✓ test_get_diameter_two_file_with_trust_circle_diameter_three_and_name (error)


✓ test_get_incomplete_diameter_three_file_with_trust_circle_diameter_three (C<-A<->B) (error)

✓ test_get_incomplete_diameter_three_file_with_trust_circle_diameter_three_2 (C<->A<->B) (error)

✓ test_get_diameter_three_file_with_trust_circle_diameter_three (C<->A<->B->C)

✓ test_get_diameter_three_file_with_trust_circle_diameter_three_and_name

✓ test_get_diameter_three_file_with_trust_circle_diameter_four (error)



## Signing

To generate new private key and certificate:

```
openssl req -new -newkey rsa:1024 -days 365 -nodes -x509 -keyout test.key -out test.cert
```

To generate CSR:

```
openssl req -new -sha256 -key test.key -out 2.csr
```

To sign a CSR with specified private key and certificate:

```
openssl x509 -CAkey test.key -CA test.cert -in 1.csr -req -out 1.crt -CAcreateserial
```

To display who signed the certificate:

```
openssl x509 -text -noout -in 1.crt
```

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

```
java -jar oldTrustyClient.jar -a meme.txt -h 127.0.0.1:3002 -c 2
```

vouch for meme.txt, using test.cert:

```
java -jar ../../oldTrustyClient/dist/oldTrustyClient.jar -v meme.txt test.cert -h 127.0.0.1:3002 -c 2
```

# Server

## Usage

Run server:

```python
import socket
from oldtrusty import TCPServer

server = TCPServer()
server.serve_forever()
```
