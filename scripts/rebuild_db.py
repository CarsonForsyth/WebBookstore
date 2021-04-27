
from generate_tables import generate_all_tables
from populate_tables import populate_tables
from initialize_connection import create_connection


DB_Pathname = r".\..\SQLite_bookstore.db"

# Try connect to database.
try:
    conn = create_connection(DB_Pathname)
except:
    raise Exception('Establishing connection to database ' + DB_Pathname + ' failed')

# Create the empty tables in the database.
generate_all_tables(conn)

# Populate each table using mock_users.csv, modified_books.csv, and some random data.
populate_tables(conn)





