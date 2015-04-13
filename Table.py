from Column import Column

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
			i['REFERENCED_SCHEMA'], i['REFERENCED_TABLE'], i['REFERENCED_COLUMN']))
	
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
		query = "SELECT COUNT(1) FROM %s" % self.table_name
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
		self.generate_columns()
		self.set_table_references()
		self.get_rows_exists_in_table()

		
	def generate_insert_values(self):
		values_statement = "("
		for column in self.columns:
			values_statement += str(column.generate_data()) + ","
		values_statement = values_statement[:-1] + ")"
		return values_statement
		
	def generate_insert_statement(self, record_count):
		insert_statement = self.generate_insert_statement_prefix()
		for i in range(record_count):
			insert_statement += self.generate_insert_values()
			if i != record_count - 1:
				insert_statement += ","
		return insert_statement
		
	def insert_data(self):
		cursor = self.cnx.cursor()
		cursor.execute(self.generate_insert_statement(self.rows_to_generate))
		self.cnx.commit()