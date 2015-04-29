import argparse
import getpass
import MySQLdb
from Schema import Schema
import string

def set_mysql_session_variables(cnx):
	cursor = cnx.cursor()
	query = "SET time_zone = '+00:00';"
	cursor.execute(query)
	cursor.close()
	
def get_schema_list(cnx):
    schema_list = []
    query = ("SELECT schema_name FROM information_schema.SCHEMATA"
    " WHERE schema_name NOT IN ('mysql', 'performance_schema', 'information_schema') "
	"ORDER BY schema_name")
    cursor = cnx.cursor()
    cursor.execute(query)
    for schema in cursor:
        schema_list.append(schema[0])
    return schema_list
	
def menu_picker(menu_list):
    menu_number = 1
    for schema in menu_list:
        print "%s) %s" % (menu_number, schema)
        menu_number += 1
	#TODO: Add range specification to input prompt
    user_selection = int(raw_input("Please enter selection: "))
	#TODO: input validation
    return user_selection
	
def validate_schema_name(schema_name, schema_list):
	if schema_name not in schema_list:
		if schema_name == None:
			print "No schema specified.  Please select one from the following list"
		else:
			print "Schema not found.  Please select one from the following list"
		return schema_list[menu_picker(schema_list)-1]
	else:
		return schema_name

def validate_table_rows_created(table_index):
	limiting_referenced_tables = []
	for i in mysql_schema.tables[table_index].table_references:
		if i['LIMITING_REFERNCE']:
			limiting_referenced_tables.append(i)
	if len(limiting_referenced_tables) > 0:
		lowest_limiting_reference_row_count = None
		for i in limiting_referenced_tables:
			limiting_referenced_table_index = mysql_schema.get_table_index_from_name(i['REFERENCED_TABLE'])
			limiting_reference_row_count = mysql_schema.tables[limiting_referenced_table_index].rows_exists_in_table + mysql_schema.tables[limiting_referenced_table_index].rows_to_generate
			if limiting_reference_row_count < lowest_limiting_reference_row_count or lowest_limiting_reference_row_count == None:
				lowest_limiting_reference_row_count = limiting_reference_row_count
		resulting_rows_validated_table = mysql_schema.tables[table_index].rows_exists_in_table + mysql_schema.tables[table_index].rows_to_generate	
		if lowest_limiting_reference_row_count < resulting_rows_validated_table:
			mysql_schema.tables[table_index].rows_to_generate = lowest_limiting_reference_row_count - mysql_schema.tables[table_index].rows_exists_in_table
			print "Due to limiting references on %s, number of rows in this table cannot exceed %s.  The number of rows to be created has been reduced to %s" % (mysql_schema.tables[table_index].table_name, lowest_limiting_reference_row_count, mysql_schema.tables[table_index].rows_to_generate)

def validate_all_tables_rows_created():
	for i in range(0, len(mysql_schema.tables)):
		validate_table_rows_created(i)

def menu_adjust_creation_properties():
	table_menu_option = ["Adjust rows to be created", "Done"]
	print "The following will apply in the data creation."
	print "Rows to be created per table: " + str(args.rowcount)
	table_menu_continue = raw_input("Would you like to change any of these properties for any table or column? [y/n]: ")
	#TODO: input validation
	#TODO: create y_n picker function so to not dup code
	#validate that there are any tables to use before loading prompt
	while table_menu_continue in ['Y', 'y']:
		print "Please select what table you would like to adjust."
		table_index = menu_picker(mysql_schema.table_list)-1
		print "What value would you like to adjust?"
		table_menu_selection_index = menu_picker(table_menu_option)-1
		if table_menu_selection_index == 0:
			print "The number of records to be create in table %s is %s" % (mysql_schema.tables[table_index].table_name, mysql_schema.tables[table_index].rows_to_generate)
			mysql_schema.tables[table_index].rows_to_generate = int(raw_input("How many records should be created in this table? "))
			validate_table_rows_created(table_index)
			table_menu_continue = raw_input("Would you like to adjust the properties of any other tables? [y/n]: ")
		else:
			table_menu_continue = 0

argparser = argparse.ArgumentParser()
argparser.add_argument("-H", "--host", default="localhost", help="Connect to the MySQL server on the given host.")
argparser.add_argument("-d", "--database", help="Database that you would like to load random data into.")
argparser.add_argument("-p", "--password", help="Connect to the MySQL server on the given host.")
argparser.add_argument("-P", "--port", default=3306, type=int, help="The TCP/IP port number to use for the MySQL connection.")
argparser.add_argument("-S", "--socket", help="For connections to localhost, the Unix socket file to use.")
argparser.add_argument("-u", "--user", default=getpass.getuser(), help="The MySQL user name to use when connecting to the server.")
argparser.add_argument("-r", "--rowcount", default=10000, type=int, help="The default number of rows to create per table.")
argparser.add_argument("-i", "--rows_per_insert", default=500, type=int, help="The default number of rows to create per insert statement.")
args = argparser.parse_args()

if args.password == None:
	args.password = getpass.getpass("Enter password: ")

if args.socket != None:
	cnx = MySQLdb.connect(user=args.user, passwd=args.password, unix_socket=args.socket)
else:
	cnx = MySQLdb.connect(host=args.host, user=args.user, passwd=args.password, port=args.port)

mysql_schema_name = validate_schema_name(args.database, get_schema_list(cnx))
set_mysql_session_variables(cnx)
print "Loading information about %s schema.  Please wait." % (mysql_schema_name)
mysql_schema = Schema(cnx, mysql_schema_name)
mysql_schema.set_tabkle_defaults(args.rowcount, args.rows_per_insert)
menu_adjust_creation_properties()
validate_all_tables_rows_created()

final_check = raw_input("Are you sure you would like to write random data to the %s schema? [y/n]: " % mysql_schema_name)
if final_check in ['Y', 'y']:
	print "Creating Data.  Please wait."
	mysql_schema.generate_data()
else:	
	print "Bye!"