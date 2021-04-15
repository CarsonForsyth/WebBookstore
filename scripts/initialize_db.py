
import sqlite3
from generate_tables import *
from populate_tables import *

# create a connection to the SQLite Database
# @param {Pathname} db_file: The filename to connect to or create.
# @return {SQLite3 Connection Object} conn: the database connection.
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        return e
DB_Pathname = r".\..\SQLite_bookstore.db"



# check if db
try:
    conn = create_connection(DB_Pathname)
except:
    raise Exception('Establishing connection to database ' + DB_Pathname + ' failed')

generate_all_tables(conn)
conn.execute("SELECT id FROM Books LIMIT 1")
populate(conn)





