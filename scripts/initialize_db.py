
from generate_tables import *
#from populate_tables import *
from initialize_connection import *


DB_Pathname = r".\..\SQLite_bookstore.db"



# check if db
try:
    conn = create_connection(DB_Pathname)
except:
    raise Exception('Establishing connection to database ' + DB_Pathname + ' failed')

generate_all_tables(conn)
#populate(conn)





