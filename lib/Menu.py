import sys

class Menu:

	def __init__(self, schema):
		self.schema = schema
	
	def get_table_names(self):
		table_names = []
		for table in self.schema.tables:
			table_names.append(table.table_name)
		return table_names		
	
	def get_column_names(self, table_index):
		column_names = []
		for column in self.schema.tables[table_index].columns:
			column_names.append(column.column_name)
		return column_names

	def list_picker(self, menu_list):
		validation_required = True
		menu_number = 1
		for choice in menu_list:
			print "%s) %s" % (menu_number, choice)
			menu_number += 1
		print "%s) %s" % (menu_number, "[Back/Exit]")
		min_val = 1
		max_val = menu_number
		user_selection = raw_input("Please enter selection: [%s-%s] " % (min_val, max_val))
		while validation_required:
			if str(user_selection).isdigit():
				user_selection = int(user_selection)
				if user_selection >= min_val and user_selection <= max_val:
					validation_required = False
				else:
					print "Selection much be in the appropriate range."
			else:
				print "Selection must be a positive integer."
			if validation_required:
				user_selection = raw_input("Please enter selection [%s-%s]: " % (min_val, max_val))
		return user_selection - 1
	
	def int_picker(self, prompt, min_val, max_val, is_nullable):
		validation_required = True
		if min_val != None and max_val != None:
			prompt = "%s[%s - %s] " % (prompt, min_val, max_val)
		elif min_val != None and max_val == None:
			prompt = "%s[Min Value %s] " % (prompt, min_val)
		if is_nullable:
			prompt = prompt + "[C to clear] "
		user_input = raw_input(prompt)
		while validation_required:
			if str(user_input) in ['C', 'c']:
				user_input = None
				validation_required = False
			elif str(user_input).isdigit():	
				user_input = int(user_input)
				if (min_val == None or user_input >= min_val) and (max_val == None or user_input <= max_val):
					validation_required = False
				else:
					print "Selection much be in the appropriate range."
			else:
				print "Selection must be an integer."
			if validation_required:
				user_input = raw_input(prompt)
		return user_input
		
	def column_menu(self, table_index, column_index):
		column_menu_options = []
		if self.schema.tables[table_index].columns[column_index].is_nullable:
			column_menu_options.append("Set null percentage chance")
		if self.schema.tables[table_index].columns[column_index].is_unique == False:
			column_menu_options.append("Set cardinality")
			if self.schema.tables[table_index].columns[column_index].referenced_table != None:
				column_menu_options.append("Set referential sample size")
		if len(column_menu_options) > 0:
			print "COLUMN: " + self.schema.tables[table_index].columns[column_index].column_name
			print "What column value would you like to adjust?"
			user_selection_index = self.list_picker(column_menu_options)
			while user_selection_index <= len(column_menu_options) - 1:
				if column_menu_options[user_selection_index] == "Set null percentage chance":
					self.schema.tables[table_index].columns[column_index].null_percentage_chance = self.int_picker("Null percentage chance: ", 0, 100, False)
					print "Set to " + str(self.schema.tables[table_index].columns[column_index].null_percentage_chance)
				elif column_menu_options[user_selection_index] == "Set cardinality":
					self.schema.tables[table_index].columns[column_index].cardinality = self.int_picker("Cardinality: ", 1, None, True)
					if self.schema.validator.validate_column_cardinality(table_index, column_index) == 0:
						print "Set to " + str(self.schema.tables[table_index].columns[column_index].cardinality)
				elif column_menu_options[user_selection_index] == "Set referential sample size":
					self.schema.tables[table_index].columns[column_index].referential_sample_size = self.int_picker("Referential sample size: ", 1, None, False)
					if self.schema.validator.validate_column_referential_sample_size(table_index, column_index) == 0:
						print "Set to " + str(self.schema.tables[table_index].columns[column_index].referential_sample_size)
				print "What column value would you like to adjust?"
				user_selection_index = self.list_picker(column_menu_options)
		else:
			print "No configurable properties for this column"
			
	def table_column_menu(self, table_index):
		print "Please select what column you would like to adjust."
		column_names = self.get_column_names(table_index)
		column_index = self.list_picker(column_names)
		while column_index <= len(column_names) - 1:
			self.column_menu(table_index, column_index)
			print "Please select what column you would like to adjust."
			column_index = self.list_picker(column_names)		
		
	def table_menu(self, table_index):
		table_menu_options = ["Adjust rows to be created", "Adjust column properties"]
		print "TABLE: " + self.schema.tables[table_index].table_name
		print "What table value would you like to adjust?"
		user_selection_index = self.list_picker(table_menu_options)
		while user_selection_index <= len(table_menu_options) - 1:
			if table_menu_options[user_selection_index] == "Adjust rows to be created":
				self.schema.tables[table_index].rows_to_generate = self.int_picker("How many records should be created in this table?: ", 1, None, False)
				if self.schema.validator.validate_table_rows_to_be_created == 0:
					print "Set to " + str(self.schema.tables[table_index].rows_to_generate)
			elif table_menu_options[user_selection_index] == "Adjust column properties":
				self.table_column_menu(table_index)
			print "What table value would you like to adjust?"
			user_selection_index = self.list_picker(table_menu_options)
			
	def main_menu(self):
		print "Please select what table you would like to adjust."
		table_names = self.get_table_names()
		table_index = self.list_picker(table_names)
		while table_index <= len(table_names) - 1:
			self.table_menu(table_index)
			print "Please select what table you would like to adjust."
			table_index = self.list_picker(table_names)			
		print "Menu Complete"
		
