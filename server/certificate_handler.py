import os
from OpenSSL import crypto

from .exceptions import *

class CertificateHandler:
    def __init__(self, certificate_path):
        self.__certificate_path = certificate_path
        self.__trust_list = {}
        self.__pubkey_list = {}
        self.__load_certificates()

    def __load_certificates(self):
        for f in os.listdir(self.__certificate_path):
            print "CERTIFICATE:", f
            filename = os.path.join(self.__certificate_path, f)
            with open(filename, 'rt') as cf:
                c = cf.read()
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, c)

                subject = self.__ID(cert.get_subject())
                issuer = self.__ID(cert.get_issuer())

                self.__add_trust(subject, issuer)

    def reload_certificates(self):
        print "Reloading certificates"
        self.__trust_list = {}
        self.__load_certificates()

    def __add_trust(self, subject, trustedBy):
        print subject, "trusted by", trustedBy

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

        print "Checking vouches, including - ", name, "- starting at", start

        length, visited = self.__check_who_trusts(start, start, [], vouchList, name, named, 0, 0)

        print "length ", length
        return length

    def __check_who_trusts(self, start, current, visited_list, vouchList, name_to_include, if_named_already, counter, max_length_so_far):
        new_counter = counter + 1
        visited_list.append(current)

        print "visiting: ", current, max_length_so_far

        print "had: ", if_named_already
        if not if_named_already:
            if_named_already = current == name_to_include
            print "got:", current, name_to_include, if_named_already

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
