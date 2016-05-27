import os
from M2Crypto import X509


from .certificate_handler import CertificateHandler
from .exceptions import *

class VouchHandler:
    def __init__(self, file_path, certificate_path):
        self.__certHandler = CertificateHandler(certificate_path)
        self.__files_path = file_path
        self.__certificates_path = certificate_path
        self.__fileList = { x.strip() : [] for x in os.listdir(self.__files_path)}

    def add_file(self, filename):
        self.__fileList[filename] = []

    def add_vouch(self, filename, certname):
        if self.does_cert_exist(certname):
            if self.does_file_exist(filename):
                name = self.__certHandler.get_certificate_subject(certname)
                self.__fileList[filename].append(name)
            else:
                raise NoFileError("No such filename: " + filename)
        else:
            raise NoCertificateError("No such certificate: " + certname)

    def get_pubkey_from_certname(self, certname):
        if not self.does_cert_exist(certname):
            raise NoCertificateError("No such certificate: " + certname)
        else:
            try:
                with open(os.path.join(self.__certificates_path, certname)) as certf:
                    data = certf.read()
                    cert = X509.load_cert_string(data, X509.FORMAT_PEM)
                    pub_key = cert.get_pubkey()
                    return pub_key.get_rsa()
            except IOError as err:
                raise NoCertificateError("Could not open certificate: " + certname)

    def does_file_exist(self, filename):
        return os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           'db/files/',
                                           filename))

    def does_cert_exist(self, filename):
        return os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           'db/certificates/',
                                           filename))

    def get_circle_length(self, filename, cert_to_include):
        if self.does_file_exist(filename):
            vouches = self.__fileList[filename]
            return self.__certHandler.get_max_circle_length_including(vouches, cert_to_include)
        else:
            raise NoFileError("File does not exist {}".format(filename))

    def list_vouches(self, filename):
        if filename in self.__fileList:
            return '\n'.join(str(self.__fileList[filename]))
        else:
            return "not found"

    def reload_certificates(self):
        self.__certHandler.reload_certificates()
