import random

class GenerateInteger:

	def get_value_range(self):
		if self.data_type == "year":
			self.min_val = 1901
			self.max_val = 2155
		elif self.data_type == "bit":
			self.min_val = 0
			self.max_val = 1			
		elif self.is_unsigned == True:
			self.min_val = 0
			if self.data_type == "tinyint":
				self.max_val = 255
			if self.data_type == "smallint":
				self.max_val = 65535
			if self.data_type == "mediumint":
				self.max_val = 16777215
			if self.data_type == "int":
				self.max_val = 4294967295
			if self.data_type == "bigint":
				self.max_val = 18446744073709551615
		elif self.is_unsigned == False:
			if self.data_type == "tinyint":
				self.min_val = -128
			if self.data_type == "smallint":
				self.min_val = -32768				
			if self.data_type == "mediumint":
				self.min_val = -8388608
			if self.data_type == "int":
				self.min_val = -2147483648
			if self.data_type == "bigint":
				self.min_val = -9223372036854775808
			self.max_val = abs(self.min_val + 1)
			
	def __init__(self, data_type, is_unsigned, is_unique):	
		self.data_type = data_type
		self.is_unsigned = is_unsigned
		self.is_unique = is_unique
		self.value = None
		self.get_value_range()
		
	def set_first_value(self):
		self.value = self.min_val
	
	def set_next_value(self):
		self.value += 1
		
	def set_random_value(self):
		self.value = random.randint(self.min_val,self.max_val)

	def generate_data(self):
		if self.is_unique == False:
			self.set_random_value()
		else:
			if self.value == None:
				self.set_first_value()
			else:
				self.set_next_value()
		return self.value