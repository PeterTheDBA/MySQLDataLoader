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

	def get_referential_values(self):
		cursor = self.cnx.cursor()
		query = ("SELECT DISTINCT %s "
			"FROM %s.%s "
			"WHERE %s IS NOT NULL "
			"LIMIT 10000" % (self.reference_column, self.reference_schema, self.reference_table, self.reference_column))
		cursor.execute(query)
		for row in cursor.fetchall():
			self.possible_values.append(row[0])
	
	def generate_data(self):
		if len(self.possible_values) == 0:
			self.get_referential_values()
		if self.is_unique == True:
			self.last_sequential_index += 1
			return  "'%s'" % (self.possible_values[self.last_sequential_index]) 
		else:
			return "'%s'" % (random.choice(self.possible_values))