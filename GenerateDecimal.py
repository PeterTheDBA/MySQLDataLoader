import decimal
import random

class GenerateDecimal:

	def set_scale_denom(self):
		self.scale_denominator = 10 ** self.numeric_scale

	def __init__(self, data_type, numeric_precision, numeric_scale, is_unsigned, is_unique):
		self.data_type = data_type
		self.numeric_precision = numeric_precision
		self.numeric_scale = numeric_scale
		self.is_unsigned = is_unsigned
		self.is_unique = is_unique
		self.value = None
		if self.data_type in ["float", "double"]:
			self.numeric_precision = 19
			self.numeric_scale = 5
		self.set_scale_denom()
		
	def set_first_value(self):
		if self.is_unsigned == True:
			self.value =  decimal.Decimal(1) / self.scale_denominator
		else:
			self.value = decimal.Decimal(-1) + (decimal.Decimal(1) / self.scale_denominator)
	
	def set_next_value(self):
		self.value = (self.value * self.scale_denominator + 1) / self.scale_denominator
		
	def set_random_value(self):
		rand_int = random.randrange(10 ** self.numeric_precision - 1)
		if self.is_unsigned == False and random.getrandbits(1):
			self.value =  decimal.Decimal(rand_int) / decimal.Decimal(self.scale_denominator) * -1
		else:
			self.value =  decimal.Decimal(rand_int) / decimal.Decimal(self.scale_denominator)
		
	def generate_data(self):
		if self.is_unique == False:
			self.set_random_value()
		else:
			if self.value == None:
				self.set_first_value()
			else:
				self.set_next_value()
		return self.value