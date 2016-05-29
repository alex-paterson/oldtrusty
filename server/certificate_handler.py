import os
from OpenSSL import crypto
from OpenSSL.crypto import X509, X509Store


from .exceptions import *

class CertificateHandler:
    def __init__(self, certificate_path):
        self.__certificate_path = certificate_path
        self.__trust_list = {}
        self.__cert_store = X509Store()
        self.__load_certificates()
        self.__verify_certs()

    def __load_certificates(self):
        for f in os.listdir(self.__certificate_path):
            filename = os.path.join(self.__certificate_path, f)
            with open(filename, 'rt') as cf:
                c = cf.read()
                try:
                    cert = crypto.load_certificate(crypto.FILETYPE_PEM, c)

                    self.__cert_store.add_cert(cert)

                    subject = self.__ID(cert.get_subject())
                    issuer = self.__ID(cert.get_issuer())
                    pubkey = cert.get_pubkey()

                    self.__add_trust(subject, issuer, pubkey)
                except Exception as e:
                    print "Found invalid cetificate", repr(f), e

    def __verify_certs(self):
        for f in os.listdir(self.__certificate_path):
            filename = os.path.join(self.__certificate_path, f)
            with open(filename, 'rt') as cf:
                c = cf.read()
                try:
                    cert = crypto.load_certificate(crypto.FILETYPE_PEM, c)
                    store_ctx = crypto.X509StoreContext(self.__cert_store, cert)
                    result = store_ctx.verify_certificate()

                    if result != None:
                        print result
                except Exception as e:
                    print "Could not validate certificate", repr(f), e

    def reload_certificates(self):
        self.__trust_list = {}
        self.__cert_store = X509Store()
        self.__load_certificates()
        self.__verify_certs()

    def __add_trust(self, subject, trustedBy, pubkey):
        #print subject, "trusted by", trustedBy

        if subject in self.__trust_list:
            self.__trust_list[subject].append(trustedBy)
        else:
            self.__trust_list[subject] = [trustedBy]

    def get_max_circle_length_including(self, vouchList, name_to_include):
        if len(vouchList) == 0:
            return 0
        start = vouchList[0]

        if not name_to_include or len(name_to_include) == 0:
            named = True
            name = ""
        else:
            named = False
            name = self.get_certificate_subject(name_to_include)

        length, visited = self.__check_who_trusts(start, start, [], vouchList, name, named, 0, 0)

        return length

    def __check_who_trusts(self, start, current, visited_list, vouchList, name_to_include, if_named_already, counter, max_length_so_far):
        new_counter = counter + 1
        visited_list.append(current)

        if not if_named_already:
            if_named_already = current == name_to_include

        if current in self.__trust_list:
            for user in self.__trust_list[current]:
                if user == start:
                    if new_counter > max_length_so_far and if_named_already:
                        max_length_so_far = new_counter
                elif user not in visited_list and user in vouchList:
                    max_length_so_far, visited_list = self.__check_who_trusts(start, user, visited_list, vouchList, name_to_include, if_named_already, new_counter, max_length_so_far)

        return max_length_so_far, visited_list

    def __ID(self, name):
        return name.hash()

    def get_certificate_subject(self, certname):
        if not os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           'db/certificates/',
                                           certname)):
            return ""

        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'db/certificates/',
                               certname)) as f:
            certificate = f.read()
        if not certificate:
            raise NoCertificateError("Could not find certificate {}".format(certname))

        cert = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        return self.__ID(cert.get_subject())
