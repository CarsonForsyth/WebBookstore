from sqlite3 import Error

# create a table from the create_table_sql statement
# @param {SQLite3 Connection Object} conn: The database to create tables in.
# @param {SQL Statement} create_table_sql: a CREATE TABLE statement.
# @return none
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def generate_all_tables(conn):
    if conn is None:
        print("Error! cannot create the database connection.")
    else:
        # Users
        sql_create_users_table =  """ CREATE TABLE IF NOT EXISTS Users ( 
            id INTEGER PRIMARY KEY,
            password BLOB,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            role TEXT CHECK (role IN ('manager', 'employee', 'default')) NOT NULL DEFAULT 'default'
        );"""
        create_table(conn, sql_create_users_table)
        sql_create_trusts_table = """ CREATE TABLE IF NOT EXISTS Trusts (
            user_id INTEGER,
            trusts INTEGER,
            value INTEGER CHECK (value = -1 OR value = 1),
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (trusts) REFERENCES Users(id)
        );
        """
        create_table(conn, sql_create_trusts_table)
        
        sql_create_customers_table = """ CREATE TABLE IF NOT EXISTS Customers (
            user_id INTEGER,
            phone INTEGER NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        );
        """
        create_table(conn, sql_create_customers_table)
        # Books
        sql_create_books_table = """ CREATE TABLE IF NOT EXISTS Books (
            id INTEGER PRIMARY KEY,
            title text NOT NULL,
            isbn INTEGER NOT NULL,
            isbn13 INTEGER NOT NULL,
            language TEXT NOT NULL,
            num_pages INTEGER NOT NULL,
            pub_date INTEGER NOT NULL,
            publisher TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            price NUMBER NOT NULL,
            stock INTEGER NOT NULL,
            CHECK (price >= 0 AND num_pages >= 0)
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
            FOREIGN KEY (author_id) REFERENCES Authors(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE
        );
        """
        create_table(conn, sql_create_authorWrites_table)
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
            FOREIGN KEY (subject_id) REFERENCES Subjects(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE
        );
        """
        create_table(conn, sql_create_bookHasSubject_table)
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
            FOREIGN KEY (keyword_id) REFERENCES Keywords(id) ON DELETE CASCADE
            FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE
        );
        """
        create_table(conn, sql_create_bookRelatesTo_table)
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
            discount REAL NOT NULL CHECK (discount > 0 AND discount <= 1),
            date_start INTEGER NOT NULL,
            date_end INTEGER NOT NULL
        );
        """
        create_table(conn, sql_create_sales_table)
        sql_create_salesDiscounts_table = """ CREATE TABLE IF NOT EXISTS SalesDiscounts
        (
            sale_id INTEGER,
            book_id INTEGER,
            FOREIGN KEY (sale_id) REFERENCES Sales(id),
            FOREIGN KEY (book_id) REFERENCES Books(id)
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
            user_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES Customers(id) ON DELETE CASCADE
        );
        """
        create_table(conn, sql_create_comments_table)
        sql_create_ratings_table = """ CREATE TABLE IF NOT EXISTS Ratings
        (
            comment_id INTEGER,
            value INTEGER NOT NULL CHECK (value >= 0 AND value <= 2),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comment_id) REFERENCES Comments(id) ON DELETE CASCADE
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
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Customers(id) ON DELETE NO ACTION
        );
        """
        create_table(conn, sql_create_addresses_table)
        sql_create_orders_table = """ CREATE TABLE IF NOT EXISTS Orders
        (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            order_quarter INTEGER,
            time_fulfilled DATETIME DEFAULT NULL,
            ships_to INTEGER,
            placed_by INTEGER,
            FOREIGN KEY (ships_to) REFERENCES Addresses(id)
            FOREIGN KEY (placed_by) REFERENCES Customers(id)
        );
        """
        create_table(conn, sql_create_orders_table)
        sql_create_orderItems_table = """ CREATE TABLE IF NOT EXISTS OrderItems
        (
            id INTEGER PRIMARY KEY,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 1 NOT NULL,
            book_id INTEGER,
            order_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES Books(id),
            FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE
        );
        """
        create_table(conn, sql_create_orderItems_table)
        sql_create_coupons_table = """ CREATE TABLE IF NOT EXISTS Coupons
        (
            id INTEGER PRIMARY KEY,
            discount REAL NOT NULL CHECK (discount > 0 and discount <= 1),
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            date_start INTEGER NOT NULL,
            date_end INTEGER NOT NULL
        );
        """
        create_table(conn, sql_create_coupons_table)
        sql_create_couponDiscounts_table = """ CREATE TABLE IF NOT EXISTS CouponDiscounts
        (
            order_id INTEGER,
            coupon_id INTEGER,
            FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (coupon_id) REFERENCES Coupons(coupon_id)
        );
        """
        create_table(conn, sql_create_couponDiscounts_table)

        # VIEWS
        sql_create_bookStats_view = """ CREATE VIEW IF NOT EXISTS BookStats AS SELECT * FROM 
            (
            SELECT Books.isbn13 AS isbn, SUM(quantity) AS copies_sold, publisher, order_quarter FROM Books INNER JOIN OrderItems INNER JOIN Orders GROUP BY Books.isbn13
            );
        """
        create_table(conn, sql_create_bookStats_view)

        sql_create_commentRating_view = """ CREATE VIEW IF NOT EXISTS CommentRating AS SELECT * FROM 
            (
            SELECT user_id, Comments.comment_id, AVG(value) AS avg_rating FROM Comments INNER JOIN Ratings GROUP BY user_id
            );
        """
        create_table(conn, sql_create_commentRating_view)

        sql_create_userStats_view = """ CREATE VIEW IF NOT EXISTS UserStats AS SELECT * FROM 
            (  
            (SELECT Users.user_id, SUM(Trusts.value) AS trust_rating 
            FROM Users INNER JOIN Trusts)
            INNER JOIN
            (SELECT CommentRating.user_id, AVG(avg_rating) AS usefulness 
            FROM CommentRating GROUP BY CommentRating.user_id)
            );
        """
        create_table(conn, sql_create_userStats_view)

        sql_create_addressOrderStats_view = """ CREATE VIEW IF NOT EXISTS AddressOrderStats AS SELECT * FROM (
            SELECT city, region, country, quarter, SUM(total) AS order_total FROM
            (
                SELECT order_id, address_id, quantity*SUM(price) AS total 
                FROM Orders INNER JOIN OrderItems 
                GROUP BY order_id
            ) 
            INNER JOIN Addresses
            );
        """
        create_table(conn, sql_create_addressOrderStats_view)
        
