import string
import random

class GenerateString:

	def set_possible_values(self):
		#TODO: insert logic that, if unique uses this set of chars, if not, use full spectrum
		self.possible_values = string.ascii_uppercase + string.digits + string.punctuation.translate(None, "'\\#")
		self.possible_values_max_index = len(self.possible_values) - 1
		
	def set_possible_value_count(self):
		possible_values_length = len(self.possible_values)
		if self.character_maximum_length > 5:
			self.possible_value_count = 50000000000
		elif self.data_type in ["varchar", "tinytext", "tinyblob", "varbinary"]:
			self.possible_value_count = (possible_values_length * (possible_values_length ** self.character_maximum_length - 1)) / (possible_values_length - 1)
		elif self.data_type in ["char", "binary"]:	
			self.possible_value_count = possible_values_length ** self.character_maximum_length
	
	def __init__(self, data_type, character_maximum_length, is_unique):
		self.data_type = data_type
		self.character_maximum_length = character_maximum_length
		self.is_unique = is_unique
		self.set_possible_values()
		self.value = None
		self.values_generated = 0
		self.set_possible_value_count()
	
	def set_first_value(self):
		self.value = self.possible_values[0]
	
	def set_next_value(self):
		value_list = []
		eval_character_index = len(self.value)-1
		carry = None
		for i in range(len(self.value)):
			value_list.append(self.value[i])
		while carry != False:
			if eval_character_index == -1:
				value_list = [self.possible_values[0]] + value_list
				carry = False
			elif self.possible_values.index(value_list[eval_character_index]) == self.possible_values_max_index:
				value_list[eval_character_index] = self.possible_values[0]
				eval_character_index -= 1
				carry = True
			else:
				value_list[eval_character_index] = self.possible_values[(self.possible_values.index(value_list[eval_character_index]) + 1)]
				carry = False
		self.value = ''.join(value_list)
		
	def set_random_value(self):
		if self.data_type in ["varchar", "tinytext", "tinyblob", "varbinary"]:
			random_string_length = random.randint(1,self.character_maximum_length)
		elif self.data_type in ["char", "binary"]:
			random_string_length = self.character_maximum_length
		else:
			random_string_length = random.randrange(1000)
		self.value = ""
		for i in range(random_string_length):
			self.value += random.choice(self.possible_values)
			
	def generate_data(self):
		if self.is_unique == False:
			self.set_random_value()
		else:
			if self.value == None:
				self.set_first_value()
			else:
				self.set_next_value()
		self.values_generated += 1
		return self.value