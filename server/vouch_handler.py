import os
from .certificate_handler import CertificateHandler
from .exceptions import *


class VouchHandler:
    def __init__(self, file_path, certificate_path):
        self.__certHandler = CertificateHandler(certificate_path)
        self.__files_path = file_path
        self.__fileList = {}
        self.__add_existing_files()

    def __add_existing_files(self):
        listDir = os.listdir(self.__files_path)

        for filename in listDir:
            print "Adding file: ", filename
            self.add_file(filename.strip())

    def add_file(self, filename):
        self.__fileList[filename] = []

    def add_vouch(self, filename, certname):
        if self.does_cert_exist(certname):
            if self.does_file_exist(filename):
                # name = self.__certHandler.get_certificate_subject(certname)
                name = certname
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
            print("22222222 __fileList", self.__fileList)
            return self.__certHandler.get_max_circle_length_including(vouches, cert_to_include)
        else:
            raise NoFileError("File does not exist {}".format(filename))

    def list_vouches(self, filename):
        if filename in self.__fileList:
            print "list: ", self.__fileList[filename]
            return '\n'.join(self.__fileList[filename])
        else:
            return "not found"
