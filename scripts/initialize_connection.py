import sqlite3
from sqlite3 import Error

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