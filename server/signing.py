from OpenSSL import crypto

def sign_data_with_pubkey(data, pubkey):
    signed = crypto.sign(pubkey, data, 'sha1')


    return signed
