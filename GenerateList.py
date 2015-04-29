import random
from itertools import combinations

class GenerateList:

	def set_possible_values(self):
		if self.data_type == "enum":
			column_type_start_index = 6
		elif self.data_type == "set":
			column_type_start_index = 5
		self.possible_values = (self.column_type[column_type_start_index:(len(self.column_type)-2)]).split("\',\'")
	
	def set_possible_value_count(self):
		if self.data_type == "enum":
			self.possible_value_count = len(self.possible_values)
		elif self.data_type == "set":
			self.possible_value_count = 2 ** len(self.possible_values) - 1
	
	def __init__(self, data_type, column_type, is_unique):
		self.data_type = data_type
		self.column_type = column_type
		self.is_unique = is_unique
		self.value = None
		self.set_possible_values()
		self.set_possible_value_count()
	
	def set_first_value(self):
		self.value_index = 0
		if self.data_type == "enum":
			self.value = self.possible_values[self.value_index]
		elif self.data_type == "set":
			self.set_combination_element_count = 1
			self.set_combinations = []
			for i in combinations(self.possible_values, self.set_combination_element_count):
				self.set_combinations.append(i[0])
			self.value = self.set_combinations[self.value_index]
	
	def set_next_value(self):
		if self.data_type == "enum":
			self.value_index += 1
			self.value = self.possible_values[self.value_index]
		elif self.data_type == "set":
			if self.value_index < len(self.set_combinations)-1:
				self.value_index += 1
			else:
				self.set_combination_element_count += 1
				self.value_index = 0
				self.set_combinations = []
				for i in combinations(self.possible_values, self.set_combination_element_count):
					self.set_combinations.append(i)
			self.value = ""
			for val in self.set_combinations[self.value_index]:
				self.value += val + ","
			self.value = (self.value[:-1])
		
	def set_random_value(self):
		if self.data_type == "enum":
			self.value = random.choice(self.possible_values)
		elif self.data_type == "set":
			self.value = ""
			for val in random.sample(self.possible_values,random.randrange(len(self.possible_values))+1):
				self.value += val + ","
			self.value = (self.value[:-1])
			
	def generate_data(self):
		if self.is_unique == False:
			self.set_random_value()
		else:
			if self.value == None:
				self.set_first_value()
			else:
				self.set_next_value()
		return self.value