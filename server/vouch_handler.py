import os
from .certificate_handler import CertificateHandler
from .file import File


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
			self.add_file(filename)

	def add_file(self, filename):
		self.__fileList[filename] = File()

	# For now just use common name as ID
	def add_vouch(self, filename, certificate):
		if filename in self.__fileList:
			name = self.__certHandler.get_certificate_subject(certificate)

			print name

			self.__fileList[filename].addVouch(name)
			print str(name) + " vouched for" + filename
		else:
			print "no such file: " + filename

	def get_circle_length(self, filename):
		# Once certificates are working:
		if filename in self.__fileList:
			vouches = self.__fileList[filename].getVouches()
			return self.__certHandler.get_length_including(vouches)
		else:
			return 0;

	def list_vouches(self, filename):
		if filename in self.__fileList:
			print "list: ", self.__fileList[filename].getVouches()
			return '\n'.join(self.__fileList[filename].getVouches())
		else:
			return "not found"
