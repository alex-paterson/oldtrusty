from OpenSSL import crypto
import os

class certificateHandler:
	def __init__(self):
		self.__certificate_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certificates/')
		self.__load_certificates()
		
	def __load_certificates(self):
		for file in os.listdir(self.__certificate_path):
			print(file)
			self.__load(self.__certificate_path + file)

	def __load(self, filename):
		c = open(filename, 'rt').read()
		#c = OpenSSL.crypto
		cert = crypto.load_certificate(crypto.FILETYPE_PEM, c)
		
		print cert.get_notAfter()

	def get_length_including(self, vouchList):
		return 2
