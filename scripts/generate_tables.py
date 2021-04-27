from sqlite3 import Error

# Create a table from the create_table_sql statement
# @param {SQLite3 Connection Object} conn: The database to create tables in.
# @param {SQL Statement} create_table_sql: a CREATE TABLE statement.
# @return none
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

# Generate SQL statements for each of the required tables and create table using create_table function.
# @param {SQLite3 Connection Object} conn: The database to create tables in.
# @return none
def generate_all_tables(conn):
    # Users
    sql_create_users_table =  """ CREATE TABLE IF NOT EXISTS Users ( 
        id INTEGER PRIMARY KEY,
        password TEXT,
        username TEXT NOT NULL UNIQUE,
        email TEXT UNIQUE,
        role TEXT DEFAULT 'default'
    );"""
    create_table(conn, sql_create_users_table)

    sql_create_trusts_table = """ CREATE TABLE IF NOT EXISTS Trusts (
        user_id INTEGER,
        trusts INTEGER,
        value INTEGER CHECK (value = -1 OR value = 1),
        PRIMARY KEY (user_id, trusts)
    );
    """
    create_table(conn, sql_create_trusts_table)
    
    sql_create_customers_table = """ CREATE TABLE IF NOT EXISTS Customers (
        user_id INTEGER,
        phone INTEGER NOT NULL,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        PRIMARY KEY (user_id)
    );
    """
    create_table(conn, sql_create_customers_table)
    # Books
    sql_create_books_table = """ CREATE TABLE IF NOT EXISTS Books (
        id INTEGER,
        title text NOT NULL,
        isbn INTEGER,
        isbn13 INTEGER NOT NULL,
        language TEXT NOT NULL,
        num_pages INTEGER,
        pub_date DATETIME NOT NULL,
        publisher TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        price NUMBER NOT NULL,
        stock INTEGER NOT NULL,
        CHECK (price >= 0 AND num_pages >= 0),
        PRIMARY KEY (id)
    );
    """
    create_table(conn, sql_create_books_table)

    sql_create_authors_table = """ CREATE TABLE IF NOT EXISTS Authors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    """
    create_table(conn, sql_create_authors_table)

    sql_create_authorWrites_table = """ CREATE TABLE IF NOT EXISTS AuthorWrites (
        author_id INTEGER,
        book_id INTEGER,
        PRIMARY KEY (author_id, book_id)
    );
    """
    create_table(conn, sql_create_authorWrites_table)
    
    sql_create_keywords_table = """ CREATE TABLE IF NOT EXISTS Keywords
    (
        id INTEGER PRIMARY KEY,
        keyword TEXT NOT NULL
    );
    """
    create_table(conn, sql_create_keywords_table)

    sql_create_bookRelatesTo_table = """ CREATE TABLE IF NOT EXISTS BookRelatesTo
    (
        keyword_id INTEGER,
        book_id INTEGER,
        PRIMARY KEY (keyword_id, book_id),
        FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE
    );
    """
    create_table(conn, sql_create_bookRelatesTo_table)

    sql_create_subjects_table = """ CREATE TABLE IF NOT EXISTS Subjects
    (
        id INTEGER PRIMARY KEY,
        subject TEXT NOT NULL
    );
    """
    create_table(conn, sql_create_subjects_table)

    sql_create_bookHasSubject_table = """ CREATE TABLE IF NOT EXISTS BookHasSubject
    (
        subject_id INTEGER,
        book_id INTEGER,
        PRIMARY KEY (subject_id, book_id),
        FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE
    );
    """
    create_table(conn, sql_create_bookHasSubject_table)

    sql_create_images_table = """ CREATE TABLE IF NOT EXISTS Images
    (
        image_id INTEGER, 
        book_id INTEGER,
        image BLOB NOT NULL,
        FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE
    );
    """
    create_table(conn, sql_create_images_table)
    sql_create_sales_table = """ CREATE TABLE IF NOT EXISTS Sales
    (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        discount REAL NOT NULL CHECK (discount >= 0 AND discount <= 1),
        date_start DATETIME NOT NULL,
        date_end DATETIME NOT NULL
    );
    """
    create_table(conn, sql_create_sales_table)
    sql_create_salesDiscounts_table = """ CREATE TABLE IF NOT EXISTS SalesDiscounts
    (
        sale_id INTEGER,
        book_id INTEGER,
        PRIMARY KEY (sale_id, book_id)
    );
    """
    create_table(conn, sql_create_salesDiscounts_table)
    # Comment Module
    sql_create_comments_table = """ CREATE TABLE IF NOT EXISTS Comments
    (
        id INTEGER PRIMARY KEY,
        content TEXT,
        score INTEGER NOT NULL CHECK (score >= 0 and score <= 10),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        book_id INTEGER,
        user_id INTEGER
    );
    """
    create_table(conn, sql_create_comments_table)
    sql_create_ratings_table = """ CREATE TABLE IF NOT EXISTS Ratings
    (
        user_id INTEGER,
        comment_id INTEGER,
        value INTEGER NOT NULL CHECK (value >= -1 AND value <= 1),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, comment_id)
    );
    """
    create_table(conn, sql_create_ratings_table)
    # Ordering Module
    sql_create_addresses_table = """ CREATE TABLE IF NOT EXISTS Addresses
    (
        id INTEGER PRIMARY KEY,
        street_number INTEGER,
        street_name TEXT NOT NULL,
        apt_number INTEGER,
        city TEXT NOT NULL,
        zip_code INTEGER,
        region TEXT,
        country TEXT NOT NULL,
        user_id INTEGER
    );
    """
    create_table(conn, sql_create_addresses_table)
    sql_create_orders_table = """ CREATE TABLE IF NOT EXISTS Orders
    (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        total,
        order_quarter INTEGER,
        time_fulfilled DATETIME DEFAULT NULL,
        fulfilled_by INTEGER DEFAULT NULL,
        ships_to INTEGER,
        placed_by INTEGER
    );
    """
    create_table(conn, sql_create_orders_table)
    sql_create_orderItems_table = """ CREATE TABLE IF NOT EXISTS OrderItems
    (
        id INTEGER PRIMARY KEY,
        quantity INTEGER DEFAULT 1 NOT NULL,
        book_id INTEGER,
        order_id INTEGER,
        FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE
    );
    """
    create_table(conn, sql_create_orderItems_table)
    

    sql_create_cart_table = """ CREATE TABLE IF NOT EXISTS Cart
    (
        id INTEGER PRIMARY KEY,
        book_id INTEGER,
        user_id INTEGER,
        quantity INTEGER
    );
    """
    create_table(conn, sql_create_cart_table)

    # VIEWS
    sql_create_bookStats_view = """ CREATE VIEW IF NOT EXISTS BookStats AS 
        SELECT Books.id, isbn13, Books.price, sum(quantity) as copies_sold, publisher, order_quarter FROM OrderItems, Orders, Books WHERE OrderItems.book_id = Books.id AND OrderItems.order_id = Orders.id GROUP BY Books.id
    """
    create_table(conn, sql_create_bookStats_view)

    sql_create_trustRating_view = """ CREATE VIEW IF NOT EXISTS CommentRating AS
        SELECT Comments.user_id, Comments.id AS comment_id, AVG(value) AS avg_rating FROM Comments INNER JOIN Ratings ON Comments.id = Ratings.comment_id;
    """
    create_table(conn, sql_create_trustRating_view  )

    sql_create_commentRating_view = """ CREATE VIEW IF NOT EXISTS TrustRating AS
        SELECT trusts as user_id, SUM(value) as score FROM Trusts GROUP BY trusts;
    """
    create_table(conn, sql_create_commentRating_view)

    sql_create_addressOrderStats_view = """ CREATE VIEW IF NOT EXISTS AddressOrderStats AS 
        SELECT city, region, country, order_quarter, SUM(total) AS order_total FROM
        (
            SELECT order_id, ships_to AS address_id, order_quarter, total FROM Orders
        )
        INNER JOIN Addresses ON Addresses.id = address_id GROUP BY address_id
    """
    create_table(conn, sql_create_addressOrderStats_view)

    sql_create_bookRatings_view = """ CREATE VIEW IF NOT EXISTS BookRatings AS 
        SELECT Books.id as book_id, AVG(score) FROM Comments INNER JOIN Books ON book_id = Books.id GROUP BY Books.id
    """
    create_table(conn, sql_create_bookRatings_view)

    sql_create_oneDegreeAuthors_view = """ CREATE VIEW IF NOT EXISTS OneDegreeAuthors AS
        SELECT A.author_id, B.author_id AS co_author_id FROM AuthorWrites AS A INNER JOIN AuthorWrites AS B ON A.book_id=B.book_id and A.author_id!=B.author_id GROUP BY A.author_id, B.author_id ORDER BY A.author_id;
    """
    create_table(conn, sql_create_oneDegreeAuthors_view)
    
    sql_create_twoDegreeAuthors_view = """ CREATE VIEW IF NOT EXISTS TwoDegreeAuthors AS
        SELECT A.author_id, B.co_author_id FROM OneDegreeAuthors AS A INNER JOIN OneDegreeAuthors AS B ON A.co_author_id=B.author_id WHERE A.author_id!=B.co_author_id AND B.co_author_id NOT IN (SELECT co_author_id FROM OneDegreeAuthors AS C WHERE C.author_id=A.author_id);
    """
    create_table(conn, sql_create_twoDegreeAuthors_view)

    sql_create_trustedUsers_view = """ CREATE VIEW IF NOT EXISTS TrustedUsers AS SELECT user_id FROM TrustRating WHERE score >= 0;
    """
    create_table(conn, sql_create_trustedUsers_view)     

    sql_create_realPrice_view = """ CREATE VIEW IF NOT EXISTS RealPrice AS
        SELECT book_id, discount, (1-discount)*price AS realPrice FROM (SELECT book_id, SUM(discount) AS discount FROM SalesDiscounts INNER JOIN Sales ON SalesDiscounts.sale_id=Sales.id WHERE date_start<=date('now') and date_end>=date('now') GROUP BY book_id) INNER JOIN Books ON Books.id=book_id;
    """
    create_table(conn, sql_create_realPrice_view) 
        