import MySQLdb
import random

class GenerateReferential:
	
	def __init__(self, cnx, reference_schema, reference_table, reference_column, is_unique):
		self.cnx = cnx
		self.reference_schema = reference_schema
		self.reference_table = reference_table
		self.reference_column = reference_column
		self.is_unique = is_unique
		self.last_sequential_index = -1
		self.possible_values = []
		self.values_generated = 0

	def get_referential_values(self, referential_sample_size):
		cursor = self.cnx.cursor()
		query = ("SELECT DISTINCT `%s` "
			"FROM `%s`.`%s` "
			"WHERE `%s` IS NOT NULL "
			"LIMIT %s" % (self.reference_column, self.reference_schema, self.reference_table, self.reference_column, str(referential_sample_size)))
		cursor.execute(query)
		for row in cursor.fetchall():
			self.possible_values.append(row[0])
		self.possible_value_count = len(self.possible_values)
		cursor.close()
	
	def generate_data(self):
		self.values_generated += 1
		if self.is_unique == True:
			self.last_sequential_index += 1
			return  self.possible_values[self.last_sequential_index]
		else:
			return (random.choice(self.possible_values))