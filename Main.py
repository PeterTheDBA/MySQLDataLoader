import argparse
import getpass
import MySQLdb
import string
from Schema import Schema
from Menu import Menu

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

menu = Menu(mysql_schema)
menu.main_menu()

#validate_all_tables_rows_created()
#print "Creating Data.  Please wait."
#mysql_schema.generate_data()