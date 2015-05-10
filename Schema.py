import MySQLdb
from Table import Table

class Schema:
	
	def mysql_change_schema_focus(self):
		cursor = self.cnx.cursor()
		query = "USE %s" % self.schema_name
		cursor.execute(query)
		cursor.close()

	def set_schema_definition(self):
		self.schema_definition = []
		cursor = self.cnx.cursor(MySQLdb.cursors.DictCursor)
		query = ("SELECT c.TABLE_NAME, c.COLUMN_NAME, CASE c.IS_NULLABLE WHEN 'YES' THEN TRUE ELSE FALSE END as IS_NULLABLE, c.DATA_TYPE, "
			"c.CHARACTER_MAXIMUM_LENGTH, c.NUMERIC_PRECISION, c.NUMERIC_SCALE, c.COLUMN_TYPE, "
			"CASE c.extra WHEN 'auto_increment' THEN TRUE ELSE FALSE END as IS_AUTOINC, "
			"CASE WHEN COUNT(k.CONSTRAINT_NAME) <> 0 THEN TRUE ELSE FALSE END as IS_UNIQUE, "
			"ref.REFERENCED_TABLE_SCHEMA as REFERENCED_SCHEMA, ref.REFERENCED_TABLE_NAME as REFERENCED_TABLE, ref.REFERENCED_COLUMN_NAME as REFERENCED_COLUMN "
		"FROM information_schema.COLUMNS c "
		"LEFT OUTER JOIN information_schema.KEY_COLUMN_USAGE k ON k.COLUMN_NAME = c.COLUMN_NAME AND k.TABLE_SCHEMA = c.TABLE_SCHEMA AND k.TABLE_NAME = c.TABLE_NAME AND k.REFERENCED_TABLE_SCHEMA IS NULL "
		"LEFT OUTER JOIN information_schema.KEY_COLUMN_USAGE ref ON ref.COLUMN_NAME = c.COLUMN_NAME AND ref.TABLE_SCHEMA = ref.TABLE_SCHEMA AND ref.TABLE_NAME = c.TABLE_NAME AND ref.REFERENCED_TABLE_SCHEMA IS NOT NULL "
		"WHERE c.TABLE_SCHEMA = '%s' "
		"GROUP BY c.TABLE_SCHEMA, c.TABLE_NAME, c.COLUMN_NAME "
		"ORDER BY c.TABLE_NAME, c.COLUMN_NAME"
		% self.schema_name)
		cursor.execute(query)
		query_result = cursor.fetchall()
		for row in query_result:
			self.schema_definition.append(row)
		cursor.close()
		
	def set_table_list(self):
		self.table_list = []
		for i in self.schema_definition:
			if i['TABLE_NAME'] not in self.table_list:
				self.table_list.append(i['TABLE_NAME'])
	
	def generate_tables(self):
		self.tables = []
		for itr_table in self.table_list:
			table_definition = []
			for i in self.schema_definition:
				if i['TABLE_NAME'] == itr_table:
					table_definition.append(i)
			self.tables.append(Table(self.cnx, itr_table, table_definition))
		
	
	def set_tables_load_group_ordinal(self):
		tables_pending_ordinal_group_assignment = list(self.table_list)
		ordinal_group = 0
		while len(tables_pending_ordinal_group_assignment) != 0:
			tables_to_remove_from_pending_list = []
			ordinal_group += 1
			for table in self.tables:
				if table.table_name in tables_pending_ordinal_group_assignment:
					has_local_reference = 0
					for reference in table.table_references:				
						if reference['REFERENCED_SCHEMA'] == self.schema_name and reference['REFERENCED_TABLE'] in tables_pending_ordinal_group_assignment:
							has_local_reference = 1
					if has_local_reference == 0:
						table.table_load_ordinal_group = ordinal_group
						tables_to_remove_from_pending_list.append(table.table_name)
			for remove_table in tables_to_remove_from_pending_list:
				tables_pending_ordinal_group_assignment.remove(remove_table)
		self.max_ordinal_group = ordinal_group
	
	def __init__(self, cnx, schema_name):
		self.cnx = cnx
		self.schema_name = schema_name
		self.mysql_change_schema_focus()
		self.set_schema_definition()
		self.set_table_list()
		self.generate_tables()
		self.set_tables_load_group_ordinal()
		
	def set_table_defaults(self, rows_to_create, rows_per_insert):
		for table in self.tables:
			table.rows_to_generate = rows_to_create
			table.rows_per_insert = rows_per_insert
	
	def set_column_defaults(self, null_percentage_chance):
		for table in self.tables:
			for column in table.columns:
				column.null_percentage_chance = null_percentage_chance
			
	def generate_data(self):
		self.mysql_change_schema_focus()
		for ordinal_group in range(1, self.max_ordinal_group + 1):
			for table in self.tables:
				if table.table_load_ordinal_group == ordinal_group:
					table.validate_unique_not_null_referential_rows_to_create()
					table.get_column_referential_values()
					table.insert_data()
					
	def get_table_index_from_name(self, table_name):
		table_index = None
		for i in range(0, len(self.tables)):
			if self.tables[i].table_name == table_name:
				table_index = i
		return table_index;