import sys

class Menu:

	def __init__(self, schema):
		self.schema = schema
		self.table_menu_option = ["Adjust rows to be created", "Adjust column properties"]

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
	
	def int_picker(self, prompt):
		user_input = raw_input(prompt)
		while user_input.isdigit() == False:
			print "Selection must be a positive integer."
			user_input = raw_input(prompt)
		return int(user_input)
	
	def table_column_menu(self, table_index):
		print "Please select what column you would like to adjust."
		column_index = self.list_picker(self.schema.tables[table_index].column_list)
		while column_index <= len(self.schema.tables[table_index].column_list) - 1:
			print "Please select what column you would like to adjust."
			column_index = self.list_picker(self.schema.tables[table_index].column_list)		
		
	def table_menu(self, table_index):
		print "TABLE: " + self.schema.tables[table_index].table_name
		print "What table value would you like to adjust?"
		user_selection_index = self.list_picker(self.table_menu_option)
		while user_selection_index <= len(self.table_menu_option) - 1:
			if self.table_menu_option[user_selection_index] == "Adjust rows to be created":
				self.schema.tables[table_index].rows_to_generate = self.int_picker("How many records should be created in this table?: ")
				print "Set to " + str(self.schema.tables[table_index].rows_to_generate)
			elif self.table_menu_option[user_selection_index] == "Adjust column properties":
				self.table_column_menu(table_index)
			print "TABLE: " + self.schema.tables[table_index].table_name
			print "What table value would you like to adjust?"
			user_selection_index = self.list_picker(self.table_menu_option)
			
	
	def main_menu(self):
		print "Please select what table you would like to adjust."
		table_index = self.list_picker(self.schema.table_list)
		while table_index <= len(self.schema.table_list) - 1:
			self.table_menu(table_index)
			print "Please select what table you would like to adjust."
			table_index = self.list_picker(self.schema.table_list)			
		print "Menu Complete"
		

	#def main_menu(self):
		#user_selection_index = None
		#table_menu_continue = raw_input("Would you like to change any of these properties for any table or column? [y/n]: ")
		#TODO: input validation
		#TODO: create y_n picker function so to not dup code
		#validate that there are any tables to use before loading prompt
		#table_menu_continue = 'y'
		#while table_menu_continue in ['Y', 'y']:

		#print "What value would you like to adjust?"
		#table_menu_selection_index = self.menu_picker(self.table_menu_option)-1
		#if table_menu_selection_index == 0:
		#	print "The number of records to be create in table %s is %s" % (self.schema.tables[table_index].table_name, self.schema.tables[table_index].rows_to_generate)
		#	self.schema.tables[table_index].rows_to_generate = int(raw_input("How many records should be created in this table? "))
		#	self.validate_all_tables_rows_to_be_created()
		#	table_menu_continue = raw_input("Would you like to adjust the properties of any other tables? [y/n]: ")
		#else:
		#	table_menu_continue = 0
				
