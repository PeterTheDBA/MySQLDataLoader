import time
import datetime
import random

class GenerateTemporal:

	def get_value_range(self):
		if self.data_type in ["datetime","date","time"]:
			self.min_val = datetime.datetime(1000,1,1,0,0,0)
			self.max_val = datetime.datetime(9999,12,31,23,59,59)
		elif self.data_type == "timestamp":
			self.min_val = datetime.datetime(1970,1,1,0,0,1)
			self.max_val = datetime.datetime(2038,1,19,3,14,07)
	
	def __init__(self, data_type, is_unique):
		self.data_type = data_type
		self.is_unique = is_unique
		self.value = None
		self.get_value_range()

		
	def set_first_value(self):
		self.value = self.min_val
	
	def set_next_value(self):
		if self.data_type == "date":
			self.value = self.value + datetime.timedelta(1)
		else:
			self.value = self.value + datetime.timedelta(0,1)
	
	def set_random_value(self):
		secondstoadvance = random.randrange((self.max_val - self.min_val).days * 86400 + (self.max_val - self.min_val).seconds)
		self.value = self.min_val + datetime.timedelta(seconds=secondstoadvance)
	
	def generate_data(self):
		if self.is_unique == False:
			self.set_random_value()
		else:
			if self.value == None:
				self.set_first_value()
			else:
				self.set_next_value()
		if self.data_type == "date":
			return self.value.date()
		elif self.data_type == "time":
			return self.value.time()
		else:
			return self.value