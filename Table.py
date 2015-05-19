from Column import Column
import time

class Table:

	def generate_insert_statement_prefix(self):
		if self.insert_statement_prefix == "":
			self.insert_statement_prefix = "INSERT INTO `%s` (" % self.table_name
			for column in self.columns:
				if column.column_name != self.columns[0].column_name:
					self.insert_statement_prefix += ", "
				self.insert_statement_prefix += "`%s`" % column.column_name
			self.insert_statement_prefix += ") VALUES "
		return self.insert_statement_prefix
		
	def generate_columns(self):
		self.columns = []
		for i in self.table_definition:
			self.columns.append(Column(self.cnx, i['COLUMN_NAME'], i['IS_NULLABLE'], i['DATA_TYPE'], i['CHARACTER_MAXIMUM_LENGTH'], 
			i['NUMERIC_PRECISION'], i['NUMERIC_SCALE'], i ['COLUMN_TYPE'], i['IS_AUTOINC'], i['IS_UNIQUE'],
			i['REFERENCED_SCHEMA'], i['REFERENCED_TABLE'], i['REFERENCED_COLUMN'], self.table_name))
	
	def set_table_references(self):
		self.table_references = []
		for i in self.columns:
			if i.referenced_table != None:
				table_reference = {'REFERENCED_SCHEMA': i.referenced_schema, 'REFERENCED_TABLE': i.referenced_table, 'LIMITING_REFERNCE': False}
				if i.is_unique and i.is_nullable == False:
					table_reference['LIMITING_REFERNCE'] = True
				if table_reference not in self.table_references:
					self.table_references.append(table_reference)
	
	def get_rows_exists_in_table(self):
		query = "SELECT COUNT(1) FROM `%s`" % self.table_name
		cursor = self.cnx.cursor()
		cursor.execute(query)
		self.rows_exists_in_table = cursor.fetchone()[0]
		cursor.close()
		
	def __init__(self, cnx, table_name, table_definition):
		self.cnx = cnx
		self.table_name = table_name
		self.table_definition = table_definition
		self.insert_statement_prefix = ""
		self.table_load_ordinal_group = None
		self.rows_to_generate = None
		self.rows_per_insert = None
		self.rows_generated = 0
		self.generate_columns()
		self.set_table_references()
		self.get_rows_exists_in_table()

	def generate_insert_values(self):
		values_statement = "("
		for column in self.columns:
			values_statement += str(column.generate_data(self.rows_to_generate)) + ","
		values_statement = values_statement[:-1] + ")"
		return values_statement
		
	def generate_insert_statement(self, record_count):
		insert_statement = self.generate_insert_statement_prefix()
		for i in range(record_count):
			insert_statement += self.generate_insert_values()
			if i != record_count - 1:
				insert_statement += ","
		return insert_statement
	
	def validate_unique_not_null_referential_rows_to_create(self):
		original_rows_to_generate = self.rows_to_generate
		cursor = self.cnx.cursor()
		for column in self.columns:
			if column.referenced_table != None and column.is_unique and column.is_nullable == False:
				query = "SELECT COUNT(distinct `%s`) FROM `%s`.`%s` where `%s` is not null" % (column.referenced_column, column.referenced_schema, column.referenced_table, column.referenced_column)
				cursor.execute(query)
				values_available = cursor.fetchone()[0]
				if values_available < self.rows_to_generate:
					self.rows_to_generate = values_available
		if self.rows_to_generate != original_rows_to_generate:
			print "WARENING: Rows to be created in table %s reduced to %s due to unique, not nullable constraints and lack of available referential resources" % (self.table_name, self.rows_to_generate)
		cursor.close()
	
	def get_column_referential_values(self):
		for column in self.columns:
			if column.referenced_table != None and column.data_generator.values_generated == 0:
				column.get_referential_values(self.rows_to_generate)
		
	def insert_data(self, seconds_between_inserts):
		itr_rows_to_generate = 0
		cursor = self.cnx.cursor()
		while self.rows_generated < self.rows_to_generate:
			if seconds_between_inserts > 0:
				time.sleep(seconds_between_inserts)
			if self.rows_generated + self.rows_per_insert <= self.rows_to_generate:
				itr_rows_to_generate = self.rows_per_insert
			else:
				itr_rows_to_generate = self.rows_to_generate - self.rows_generated
			cursor.execute(self.generate_insert_statement(itr_rows_to_generate))
			self.rows_generated += itr_rows_to_generate
			self.cnx.commit()
		cursor.close()
		