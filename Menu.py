import sys

class Menu:

	def __init__(self, schema):
		self.schema = schema
		self.table_menu_option = ["Adjust rows to be created", "Done"]

	def menu_picker(self, menu_list):
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
				if user_selection in range(1, max_val+1):
					validation_required = False
				else:
					print "Selection much be in the appropriate range."
			else:
				print "Selection must be an integer."
			if validation_required:
				user_selection = raw_input("Please enter selection: [%s-%s] " % (min_val, max_val))
		return user_selection - 1
	
	def main_menu(self):
		user_selection_index = None
		#table_menu_continue = raw_input("Would you like to change any of these properties for any table or column? [y/n]: ")
		#TODO: input validation
		#TODO: create y_n picker function so to not dup code
		#validate that there are any tables to use before loading prompt
		#table_menu_continue = 'y'
		#while table_menu_continue in ['Y', 'y']:
		print "Please select what table you would like to adjust."
		table_index = self.menu_picker(self.schema.table_list)
		if table_index <= len(self.schema.table_list) - 1:
			print "What value would you like to adjust?"
		else:
			print "Menu Complete"
		#print "What value would you like to adjust?"
		#table_menu_selection_index = self.menu_picker(self.table_menu_option)-1
		#if table_menu_selection_index == 0:
		#	print "The number of records to be create in table %s is %s" % (self.schema.tables[table_index].table_name, self.schema.tables[table_index].rows_to_generate)
		#	self.schema.tables[table_index].rows_to_generate = int(raw_input("How many records should be created in this table? "))
		#	self.validate_all_tables_rows_to_be_created()
		#	table_menu_continue = raw_input("Would you like to adjust the properties of any other tables? [y/n]: ")
		#else:
		#	table_menu_continue = 0
				
