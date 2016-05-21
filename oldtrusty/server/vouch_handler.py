
# server receivers vouch packet:
#	

class fileStructure:
	def __init__(self):
		self.__vouchIDList = []
	
	def addVouch(self, ID):
		self.__vouchIDList.append(ID)
		
	def getVouches(self):
		return self.__vouchIDList

class vouchHandler:
	def __init__(self):
		self.__fileList = {}
	
	def add_file(self, filename):
		self.__fileList[filename] = fileStructure()
	
	# For now just use addr as vouchID
	def add_vouch(self, filename, vouchID):
		if filename in self.__fileList:
			self.__fileList[filename].addVouch(''.join(str(vouchID)))
			print "addr: " + ''.join(str(vouchID)) + " vouched for" + filename
		else:
			print "no such file: " + filename
			
	def list_vouches(self, filename):
		if filename in self.__fileList:
			print "list: ", self.__fileList[filename].getVouches()
			return '\n'.join(self.__fileList[filename].getVouches())
		else:
			return "not found"
		
