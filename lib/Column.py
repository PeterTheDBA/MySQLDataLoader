from GenerateInteger import GenerateInteger
from GenerateDecimal import GenerateDecimal
from GenerateString import GenerateString
from GenerateTemporal import GenerateTemporal
from GenerateList import GenerateList
from GenerateReferential import GenerateReferential
import random
import math

class Column:
		
	def set_base_data_type(self):
		int_type = ["tinyint", "smallint", "mediumint", "int", "bigint", "year", "bit"]
		dec_type = ["decimal", "float", "double"]
		str_type = ["char", "longtext", "mediumtext", "text", "tinytext", "varchar", "binary", "blob", "longblob", "mediumblob", "tinyblob", "varbinary"]
		tmp_type = ["datetime", "timestamp", "date", "time"]
		lst_type = ["enum", "set"]
		spa_type = ["geometry", "geometrycollection", "linestring", "multilinestring", "multipoint", "multipolygon", "point", "polygon"]
		if self.data_type in int_type:
			self.base_data_type = "integer"
		if self.data_type in dec_type:
			self.base_data_type = "decimal"
		if self.data_type in str_type:
			self.base_data_type = "string"
		if self.data_type in tmp_type:
			self.base_data_type = "temporal"
		if self.data_type in lst_type:
			self.base_data_type = "list"
		if self.data_type in spa_type:
			self.base_data_type = "spatial"
			
	def set_is_unsigned(self):
		if self.column_type.find("unsigned") > 0:
			self.is_unsigned = True
		else:
			self.is_unsigned = False
	
	def set_data_generator(self):
		if self.is_auto_inc == False:
			if self.referenced_table != None:
				self.data_generator = GenerateReferential(self.cnx, self.referenced_schema, self.referenced_table, self.referenced_column, self.is_unique)
			elif self.base_data_type == "integer":
				self.data_generator = GenerateInteger(self.data_type, self.is_unsigned, self.is_unique)
			elif self.base_data_type == "decimal":
				self.data_generator = GenerateDecimal(self.data_type, self.numeric_precision, self.numeric_scale, self.is_unsigned, self.is_unique)
			elif self.base_data_type == "string":
				self.data_generator = GenerateString(self.data_type, self.character_maximum_length, self.is_unique)
			elif self.base_data_type == "temporal":
				self.data_generator = GenerateTemporal(self.data_type, self.is_unique)
			elif self.base_data_type == "list":
				self.data_generator = GenerateList(self.data_type, self.column_type, self.is_unique)
			#TODO: Create spatial generator
	
	def set_is_data_quoted(self):
		if self.base_data_type in ["string", "temporal", "list"]:
			self.is_data_quoted = True
		else:
			self.is_data_quoted = False
			
	def set_max_unique_values(self):
		if self.referenced_table != None or self.is_auto_inc:
			self.max_unique_values = None
		else:
			self.max_unique_values = self.data_generator.possible_value_count

	def get_existing_values(self):
		cursor = self.cnx.cursor()
		query = ("SELECT UPPER(CAST(`%s` as CHAR)) "
		"FROM `%s` "
		"WHERE `%s` IS NOT NULL"
		% (self.column_name, self.table_name, self.column_name))
		cursor.execute(query)
		query_result = cursor.fetchall()
		for row in query_result:
			self.existing_values.append(row[0])
		cursor.close()
		self.existing_unique_value_count = len(self.existing_values)
			
	def __init__(self, cnx, column_name, is_nullable, data_type, character_maximum_length, numeric_precision, numeric_scale, column_type, is_auto_inc, is_unique, 
	referenced_schema, referenced_table, referenced_column, table_name):
		self.last_generated_value = None
		self.column_name = column_name
		self.is_nullable = is_nullable
		self.data_type = data_type
		self.character_maximum_length = character_maximum_length
		self.numeric_precision = numeric_precision
		self.numeric_scale = numeric_scale
		self.column_type = column_type
		self.is_auto_inc = is_auto_inc
		self.is_unique = is_unique
		self.referenced_schema = referenced_schema
		self.referenced_table = referenced_table
		self.referenced_column = referenced_column
		self.referential_sample_size = None
		self.cnx = cnx
		self.table_name = table_name
		self.cardinality = None
		self.cardinality_rows_per_value_generated = None
		self.cardinality_values_with_extra_row = None
		self.cardinality_iterative = 0
		self.existing_values = []
		self.set_base_data_type()
		self.set_is_unsigned()
		self.set_data_generator()
		self.set_is_data_quoted()
		self.set_max_unique_values()
		self.null_percentage_chance = 0
		if self.is_unique:
			self.get_existing_values()
	
	def get_referential_values(self, rows_to_generate):
		referential_sample_size = self.referential_sample_size
		if self.is_unique:
			referential_sample_size = rows_to_generate
		elif self.cardinality != None:
			referential_sample_size = self.cardinality
		self.data_generator.get_referential_values(referential_sample_size)
			
	def generate_data(self, rows_to_generate):
		if self.is_auto_inc == True or (self.is_nullable and random.randrange(1,100) <= self.null_percentage_chance and self.cardinality == None):
			return "NULL"
		else:
			data_val = None
			if self.is_unique:
				while data_val == None and self.data_generator.values_generated < self.data_generator.possible_value_count:
					new_data_val = self.data_generator.generate_data()			
					if str(new_data_val) not in self.existing_values:
						data_val = new_data_val
			else:
				if self.cardinality != None:
					if self.cardinality_rows_per_value_generated == None:
						self.cardinality_rows_per_value_generated = rows_to_generate / self.cardinality
						self.cardinality_values_with_extra_row = rows_to_generate % self.cardinality			
					if self.cardinality_iterative == 0:
						data_val = self.data_generator.generate_data()
						self.cardinality_iterative += 1
					elif self.cardinality_iterative < self.cardinality_rows_per_value_generated or (self.cardinality_iterative == self.cardinality_rows_per_value_generated and self.cardinality_values_with_extra_row > 0):
						if self.is_nullable and random.randrange(1,100) <= self.null_percentage_chance:
							data_val = None
						else:
							data_val = self.last_generated_value
						if self.cardinality_iterative == self.cardinality_rows_per_value_generated:
							self.cardinality_values_with_extra_row -= 1
						self.cardinality_iterative += 1
					else:
						data_val = self.data_generator.generate_data()
						self.cardinality_iterative = 1
				else:
					data_val = self.data_generator.generate_data()
			self.last_generated_value = data_val
			if data_val == None:
				return "NULL"
			elif self.is_data_quoted == False:
				return data_val
			elif self.is_data_quoted == True:
				return "'%s'" % (data_val)