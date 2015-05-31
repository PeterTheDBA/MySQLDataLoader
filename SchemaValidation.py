import sys

class SchemaValidation:

	def __init__(self, schema):
		self.schema = schema
	
	def validate_table_rows_to_be_created_referential(self, table_index):
		limiting_referenced_tables = []
		for i in self.schema.tables[table_index].table_references:
			if i['LIMITING_REFERNCE']:
				limiting_referenced_tables.append(i)
		if len(limiting_referenced_tables) > 0:
			lowest_limiting_reference_row_count = None
			for i in limiting_referenced_tables:
				limiting_referenced_table_index = self.schema.get_table_index_from_name(i['REFERENCED_TABLE'])
				limiting_reference_row_count = self.schema.tables[limiting_referenced_table_index].rows_exists_in_table + self.schema.tables[limiting_referenced_table_index].rows_to_generate
				if limiting_reference_row_count < lowest_limiting_reference_row_count or lowest_limiting_reference_row_count == None:
					lowest_limiting_reference_row_count = limiting_reference_row_count
			resulting_rows_validated_table = self.schema.tables[table_index].rows_exists_in_table + self.schema.tables[table_index].rows_to_generate	
			if lowest_limiting_reference_row_count < resulting_rows_validated_table:
				self.schema.tables[table_index].rows_to_generate = lowest_limiting_reference_row_count - self.schema.tables[table_index].rows_exists_in_table
				print "WARNING: Due to limited references, the number of rows to be created in table %s has been reduced to %s." % (self.schema.tables[table_index].table_name, lowest_limiting_reference_row_count)
				return 1
			else:
				return 0
		else:
			return 0
				
	def validate_table_rows_to_be_created_unique_not_null(self, table_index):
		max_rows_to_create = None
		for column in self.schema.tables[table_index].columns:
			if column.is_unique and column.is_nullable == False and column.max_unique_values != None and (max_rows_to_create == None or column.max_unique_values - column.existing_unique_value_count < max_rows_to_create):
				max_rows_to_create = column.max_unique_values - column.existing_unique_value_count
		if max_rows_to_create != None and max_rows_to_create < self.schema.tables[table_index].rows_to_generate:
			self.schema.tables[table_index].rows_to_generate = max_rows_to_create
			print "WARNING: Due to unique, not nullable columns, the number of rows to be created in table %s has been reduced to %s" % (self.schema.tables[table_index].table_name, self.schema.tables[table_index].rows_to_generate)
			return 1
		else:
			return 0

	def validate_table_rows_to_be_created(self, table_index):
		if self.validate_table_rows_to_be_created_unique_not_null(table_index) == 1 or self.validate_table_rows_to_be_created_referential(table_index) == 1:
			return 1
		else:
			return 0
				
	def validate_all_tables_rows_to_be_created(self):
		validation_complete = False
		while validation_complete == False:
			validation_complete = True
			for table_index in range(0, len(self.schema.tables)):
				if self.validate_table_rows_to_be_created(table_index) == 1:
					validation_complete = False
			
	def validate_safety(self, safety_off):
		if safety_off == False:
			rows_found = False
			for table in self.schema.tables:
				if table.rows_exists_in_table > 0:
					rows_found = True
					break
			if rows_found:
				print "ERROR: In order to prevent writing to a production system, this tool cannot create data in a schema that contains data.  If you still wish to write data to this schema, please run the tool again using --safety_off"
				sys.exit(1)
				
	def validate_column_cardinality(self, table_index, column_index):
		if self.schema.tables[table_index].columns[column_index].cardinality > self.schema.tables[table_index].rows_to_generate:
			self.schema.tables[table_index].columns[column_index].cardinality = self.schema.tables[table_index].rows_to_generate
			print ("WARNING: Cardinality in column %s.%s is higher than the number of records to be generated for the table.  Cardinality for this column has been reduced to %s." 
			% (self.schema.tables[table_index].table_name, self.schema.tables[table_index].columns[column_index].column_name, str(self.schema.tables[table_index].columns[column_index].cardinality)))
			return 1
		else:
			return 0
	
	def validate_column_referential_sample_size(self, table_index, column_index):
		if (self.schema.tables[table_index].columns[column_index].referential_sample_size > self.schema.tables[table_index].rows_to_generate or
		(self.schema.tables[table_index].columns[column_index].referential_sample_size > self.schema.tables[table_index].columns[column_index].cardinality and self.schema.tables[table_index].columns[column_index].cardinality != None)):
			if self.schema.tables[table_index].columns[column_index].cardinality != None and self.schema.tables[table_index].columns[column_index].cardinality < self.schema.tables[table_index].rows_to_generate:
				self.schema.tables[table_index].columns[column_index].referential_sample_size = self.schema.tables[table_index].columns[column_index].cardinality
			else:
				self.schema.tables[table_index].columns[column_index].referential_sample_size = self.schema.tables[table_index].rows_to_generate
			print ("WARNING: Referential Sample size in column %s.%s cannot exceed the column's cardinality or number of rows to be created.  This has been reduced to %s" 
			% (self.schema.tables[table_index].table_name, self.schema.tables[table_index].columns[column_index].column_name, str(self.schema.tables[table_index].columns[column_index].referential_sample_size)))
			return 1
		else:
			return 0
			
	def validate_table_column_properties(self, table_index):
		for column_index in range(0, len(self.schema.tables[table_index].columns)):
			self.validate_column_cardinality(table_index, column_index)
			self.validate_column_referential_sample_size(table_index, column_index)
	
	def validate_all_table_column_properties(self):
		for table_index in range(0, len(self.schema.tables)):
			self.validate_table_column_properties(table_index)
			
	def validate_all_data_creation_properties(self):
		self.validate_all_tables_rows_to_be_created()
		self.validate_all_table_column_properties()