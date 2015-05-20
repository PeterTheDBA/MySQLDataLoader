import argparse
import getpass
import MySQLdb
import string
import sys
from Schema import Schema
from Menu import Menu

def set_mysql_session_variables(cnx, no_bin_log):
	cursor = cnx.cursor()
	query = "SET time_zone = '+00:00';"
	if no_bin_log:
		query += " SET sql_log_bin = 0;"
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
	cursor.close()
    return schema_list
	
def validate_schema_name(schema_name, schema_list):
	if schema_name not in schema_list:
		if schema_name == None:
			print "No schema specified.  Please select one from the following list"
		else:
			print "Schema not found.  Please select one from the following list"
		return schema_list[menu_picker(schema_list)-1]
	else:
		return schema_name

argparser = argparse.ArgumentParser()
argparser.add_argument("-H", "--host", default="localhost", help="Connect to the MySQL server on the given host.")
argparser.add_argument("-d", "--database", help="Database that you would like to load random data into.")
argparser.add_argument("-p", "--password", help="Connect to the MySQL server on the given host.")
argparser.add_argument("-P", "--port", default=3306, type=int, help="The TCP/IP port number to use for the MySQL connection.")
argparser.add_argument("-S", "--socket", help="For connections to localhost, the Unix socket file to use.")
argparser.add_argument("-u", "--user", default=getpass.getuser(), help="The MySQL user name to use when connecting to the server.")
argparser.add_argument("-r", "--default_rows_to_create", default=10000, type=int, help="The default number of rows to create per table.")
argparser.add_argument("-m", "--menu", action='store_true', help="Use this if you would like the menu, which allows for configuration of table and column level properties.")
argparser.add_argument("--default_rows_per_insert", default=50, type=int, help="The default number of rows to create per insert statement.")
argparser.add_argument("--default_null_percentage_chance", default=5, type=int, help="The percentage likelihood of a null being passed into a nullable field")
argparser.add_argument("--default_cardinality", default=None, type=int, help="The percentage likelihood of a null being passed into a nullable field")
argparser.add_argument("--default_referential_sample_size", default=5000, type=int, help="This sets the number of values that will be retrieved from the databases when generating data from a referential source.  Reducing this number will reduce cardinality, but will also reduce the amount of memory used by the program.  Note that a cardinality property or a unique column will override referential sample size")
argparser.add_argument("--safety_off", action='store_true', help="Puts the tool in unsafe mode, which allows you generate data in schemas that already have data in them.  Please note that in some cases, this can use a lot of memory, use at your own risk")
argparser.add_argument("--no_bin_log", action='store_true', help="Disabled writing to the bin log for this session")
argparser.add_argument("--seconds_between_inserts", default=0, type=int, help="The number of seconds between each insert statement")

args = argparser.parse_args()

if args.password == None:
	args.password = getpass.getpass("Enter password: ")

if args.socket != None:
	cnx = MySQLdb.connect(user=args.user, passwd=args.password, unix_socket=args.socket)
else:
	cnx = MySQLdb.connect(host=args.host, user=args.user, passwd=args.password, port=args.port)

	
# TODO: Fix when working on menu / validation "mysql_schema_name = validate_schema_name(args.database, get_schema_list(cnx))
mysql_schema_name = args.database
#TODO: possible split validation into it's own class
set_mysql_session_variables(cnx, args.no_bin_log)
print "Loading information about %s schema.  Please wait." % (mysql_schema_name)
mysql_schema = Schema(cnx, mysql_schema_name)
mysql_schema.set_table_defaults(args.default_rows_to_create, args.default_rows_per_insert)
mysql_schema.set_column_defaults(args.default_null_percentage_chance, args.default_cardinality, args.default_referential_sample_size)

menu = Menu(mysql_schema)
menu.validate_all_tables_rows_to_be_created()
menu.validate_safety(args.safety_off)

if args.menu:
	menu.main_menu()
	menu.validate_all_tables_rows_to_be_created()
print "Creating Data.  Please wait."
mysql_schema.generate_data(args.seconds_between_inserts)
sys.exit(0)