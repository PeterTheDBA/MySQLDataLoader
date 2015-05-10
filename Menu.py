
class Menu:

	def __init__(self, schema):
		self.schema = schema
		self.table_menu_option = ["Adjust rows to be created", "Done"]

	def menu_picker(self, menu_list):
		menu_number = 1
		for schema in menu_list:
			print "%s) %s" % (menu_number, schema)
			menu_number += 1
		#TODO: Add range specification to input prompt
		user_selection = int(raw_input("Please enter selection: "))
		#TODO: input validation
		return user_selection
		
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
				
	def validate_table_rows_to_be_created_unique_not_null(self, table_index):
		max_rows_to_create = None
		for column in self.schema.tables[table_index].columns:
			if column.is_unique and column.is_nullable == False and column.max_unique_values != None and (max_rows_to_create == None or column.max_unique_values - column.existing_unique_value_count < max_rows_to_create):
				max_rows_to_create = column.max_unique_values - column.existing_unique_value_count
		if max_rows_to_create != None and max_rows_to_create < self.schema.tables[table_index].rows_to_generate:
			self.schema.tables[table_index].rows_to_generate = max_rows_to_create
			print "WARNING: Due to unique, not nullable columns, the numer of rows to be created in table %s has been reduced to %s" % (self.schema.tables[table_index].table_name, self.schema.tables[table_index].rows_to_generate)				

	def validate_table_rows_to_be_created(self, table_index):
		self.validate_table_rows_to_be_created_unique_not_null(table_index)
		self.validate_table_rows_to_be_created_referential(table_index)
				
	def validate_all_tables_rows_to_be_created(self):
		for i in range(0, len(self.schema.tables)):
			self.validate_table_rows_to_be_created_unique_not_null(i)
		for i in range(0, len(self.schema.tables)):
			self.validate_table_rows_to_be_created_referential(i)
	
	def main_menu(self):
		#print "The following will apply in the data creation."
		#print "Rows to be created per table: " + str(args.rowcount)
		#table_menu_continue = raw_input("Would you like to change any of these properties for any table or column? [y/n]: ")
		#TODO: input validation
		#TODO: create y_n picker function so to not dup code
		#validate that there are any tables to use before loading prompt
		table_menu_continue = 'y'
		while table_menu_continue in ['Y', 'y']:
			print "Please select what table you would like to adjust."
			table_index = self.menu_picker(self.schema.table_list)-1
			print "What value would you like to adjust?"
			table_menu_selection_index = self.menu_picker(self.table_menu_option)-1
			if table_menu_selection_index == 0:
				print "The number of records to be create in table %s is %s" % (self.schema.tables[table_index].table_name, self.schema.tables[table_index].rows_to_generate)
				self.schema.tables[table_index].rows_to_generate = int(raw_input("How many records should be created in this table? "))
				self.validate_all_tables_rows_to_be_created()
				table_menu_continue = raw_input("Would you like to adjust the properties of any other tables? [y/n]: ")
			else:
				table_menu_continue = 0