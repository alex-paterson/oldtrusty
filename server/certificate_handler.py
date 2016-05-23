from OpenSSL import crypto
import os

class CertificateHandler:
	def __init__(self):
		self.__certificate_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certificates/')
		self.__trust_list = {}
		self.__load_certificates()

	def __load_certificates(self):
		for file in os.listdir(self.__certificate_path):
			print(file)
			self.__load(self.__certificate_path + file)

	def __load(self, filename):
		c = open(filename, 'rt').read()
		cert = crypto.load_certificate(crypto.FILETYPE_PEM, c)

		subject = self.__ID(cert.get_subject())
		issuer = self.__ID(cert.get_issuer())

		self.__add_trust(subject, issuer)

	def __add_trust(self, subject, trustedBy):
		print subject, "trusted by ", trustedBy

		if subject in self.__trust_list:
			self.__trust_list[subject].append(trustedBy)
		else:
			self.__trust_list[subject] = [trustedBy]

	def get_length_including(self, vouchList):
		start = vouchList[0]
		print "Checking vouches, starting at", start

		test = self.__check_who_trusts(start, start, [], vouchList, 0, 0)

		print "length ", test
		return test

	def __check_who_trusts(self, start, current, visited_list, vouchList, counter, max_length_so_far):
		new_counter = counter + 1
		visited_list.append(current)

		print "visiting: ", current, max_length_so_far

		if current in self.__trust_list:
			for user in self.__trust_list[current]:
				if user == start:
					if new_counter > max_length_so_far:
						max_length_so_far = new_counter
				elif (user not in visited_list) and (user in vouchList):
					max_length_so_far = self.__check_who_trusts(start, user, visited_list, vouchList, new_counter, max_length_so_far)

		return max_length_so_far

	def __ID(self, name):
		return name.CN

	def get_certificate_subject(self, certificate):
		cert = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)

		return self.__ID(cert.get_subject())
