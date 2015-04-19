from GenerateInteger import GenerateInteger
from GenerateDecimal import GenerateDecimal
from GenerateString import GenerateString
from GenerateTemporal import GenerateTemporal
from GenerateList import GenerateList
from GenerateReferential import GenerateReferential

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
		#revise code to pass db connection to any class that doesn't already take it
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
		
	def __init__(self, cnx, column_name, is_nullable, data_type, character_maximum_length, numeric_precision, numeric_scale, column_type, is_auto_inc, is_unique, referenced_schema, referenced_table, referenced_column):
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
		self.cnx = cnx
		self.set_base_data_type()
		self.set_is_unsigned()
		self.set_data_generator()
		self.set_is_data_quoted()
		
	def generate_data(self):
		if self.is_auto_inc == True:
			return "NULL"
		elif self.is_data_quoted == False:
			return self.data_generator.generate_data()
		elif self.is_data_quoted == True:
			return "'%s'" % (self.data_generator.generate_data()) 
		
