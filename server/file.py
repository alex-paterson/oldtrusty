
class File:
	def __init__(self):
		self.__vouchIDList = []

	def addVouch(self, ID):
		if ID not in self.__vouchIDList:
			self.__vouchIDList.append(ID)

	def getVouches(self):
		return self.__vouchIDList
