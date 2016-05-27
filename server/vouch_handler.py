import os
from .certificate_handler import CertificateHandler
from .exceptions import *
from .signing import sign_data_with_pubkey

class VouchHandler:
    def __init__(self, file_path, certificate_path):
        self.__certHandler = CertificateHandler(certificate_path)
        self.__files_path = file_path
        self.__fileList = {}
        self.__add_existing_files()

    def __add_existing_files(self):
        listDir = os.listdir(self.__files_path)

        for filename in listDir:
            self.add_file(filename.strip())

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

    def get_hashed_verification(self, certname):
        if self.does_file_exist(filename):
            random_number = 1
            pubkey = self.__certHandler.pubkey_from_certificate(certname)
            hashed_number = sign_data_with_pubkey(random_number, pubkey)
            return hashed_number, random_number
        else:
            raise NoFileError("File does not exist {}".format(filename))

    def verify_random_number(self, returned_number, original_number):
        if returned_number == original_number:
            return true
        return false
