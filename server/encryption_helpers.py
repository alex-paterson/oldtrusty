import base64
from Crypto.Cipher import AES
from M2Crypto import RSA
from .helpers import ascii_to_length

def encrypt_with_key(message, rsa_key):
    cipher = rsa_key.public_encrypt(message, RSA.pkcs1_padding)
    return base64.b64encode(cipher)

def check_solution(message, original_number, rsa_key):
    message = base64.b64decode(message)
    decrypt = rsa_key.public_decrypt(message, RSA.pkcs1_padding)

    #This is needed to allow use with both python/java client:
    if(len(decrypt) < 4):
        solution = int(decrypt)
    else:
        solution = ascii_to_length(decrypt)

    if solution == int(original_number) + 499:
        return True
    else:
        return False
