from pprint import pprint
from utils.args import get_args
from utils import sql
import pymysql

args = get_args()
db_name = args.database

connection = pymysql.connect(
    host=args.host, 
    user=args.user, 
    password=args.password, 
    database=args.database,
    cursorclass=pymysql.cursors.DictCursor);

with connection:
    with connection.cursor() as cursor:
        table_names = sql.get_tables_list(db_name, cursor)

        if args.auto:
            ()
        else:
            tables = sql.prepare_tables(db_name, table_names, cursor)
            pprint(tables)