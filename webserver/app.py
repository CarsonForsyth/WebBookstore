from flask import *
from flask_bootstrap import Bootstrap
from jinja2 import Template
import sqlite3 as db
import os
import hashlib
from time import strftime
from sqlite3 import Error



DB_Pathname = r".\..\SQLite_bookstore.db"
# create a connection to the SQLite Database
# @param {Pathname} db_file: The filename to connect to or create.
# @return {SQLite3 Connection Object} conn: the database connection.
def create_connection():
    conn = None
    try:
        conn = db.connect(DB_Pathname)
        return conn
    except Error as e:
        print(e)
        return e

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    if not session.get('user_id'):
        return render_template("home.html")
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            return render_template("home.html")
        if row['role'] == "manager":
            flash("Welcome back Manager.")
            return render_template("home.html", manager=True)

@app.route("/signup", methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if not request.form.get('username') or not request.form.get('password') or not request.form.get('password'):
            flash("All fields are required.")
            return redirect(url_for('signup'))
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username=(?)", (username,))
        user = cur.fetchone()
        cur.execute("SELECT * FROM Users WHERE email=(?)", (email,))
        userEmail = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM Users")
        row = cur.fetchone()
        numUsers = int(row[0])
        if (not user and not userEmail):
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            store_pass = salt + key
            userID = numUsers + 1
            cur.execute("INSERT INTO Users (id, password, username, email, role) VALUES((?), (?), (?), (?), (?));", (userID, store_pass, username, email, 'default'))  
            conn.commit()
            resp = make_response(redirect(url_for('home')))
            session['user_id'] = userID
            resp.set_cookie('user_id', str(numUsers+1))
            return resp
        elif user:
            flash('That username was taken.')
            redirect(url_for('signup'))
        else:
            flash('That email was taken.')
            redirect(url_for('signup'))
    elif request.method == 'GET':
        return render_template("signup.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if not request.form.get('username') or not request.form.get('password') or not request.form.get('password'):
            flash("All fields are required.")
            return redirect(url_for('login'))
        username = request.form['username']
        password = request.form['password']
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username=(?)", (username,))
        user = cur.fetchone()
        if (user is None):
            flash('Login failed')
            return redirect(url_for('login'))
        else:
            store_pass = user[1]
            salt = store_pass[:32]
            key = store_pass[32:]
            check_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            if key == check_key:
                flash('You were successfully logged in')
                session['user_id'] = user[0]
                cur.execute("SELECT role FROM Users WHERE id=(?);", (user[0],))
                row = cur.fetchone()
                session['role'] = row[0]
                resp = make_response(redirect(url_for('home')))
                return resp
            else:
                flash('Login failed')
                return redirect(url_for('login'))
    elif request.method == 'GET':
        if request.args.get('logout'):
            flash("You were successfully logged out")
            resp = make_response(redirect(url_for('login')))
            session.pop('user_id', None)
            session.pop('role', None)
            return resp
        return render_template("login.html")

@app.route("/popular-books")
def viewPopularBooks():
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM (SELECT id as thisID FROM BookStats ORDER BY copies_sold LIMIT 100) INNER JOIN Books ON id = thisID;")
    rows = cur.fetchall()
    return render_template("view_popular.html", book_list=rows)


@app.route("/highly-rated-books")
def viewHighlyRatedBooks():
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM BookRatings INNER JOIN Books ON book_id = Books.id LIMIT 100")
    rows = cur.fetchall()
    return render_template("view_popular.html", book_list=rows)

@app.route("/view-user")
def viewUser():
    if not request.args.get('userID'):
        flash("No user selected.")
        return redirect(request.referrer)
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE id=(?);", (request.args['userID'],))
    row = cur.fetchone()
    if not row:
        flash("No user found.")
        return redirect(request.referrer)
    return render_template("view_user.html", user=row)

@app.route("/view-book")
def viewBook():
    if not request.args.get('bookID'):
        flash("Error getting book.")
        return redirect(request.referrer)
    bookID = int(request.args.get('bookID'))
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Books WHERE Books.id = (?)", (bookID,))
    row = cur.fetchone()
    if not row:
        flash("Book not found")
        return redirect(request.referrer)
    cur.execute("SELECT * FROM AuthorWrites INNER JOIN Authors ON Authors.id = author_id WHERE book_id = (?)", (bookID,))
    authors = cur.fetchall()
    comments = None
    if request.args.get('numRows'):
        cur.execute("SELECT id, first_name, last_name, score, content, Comments.timestamp, avg_rating, Comments.user_id FROM Comments INNER JOIN Customers ON Comments.user_id = Customers.user_id LEFT JOIN (SELECT AVG(Ratings.value) as avg_rating, comment_id FROM Ratings GROUP BY comment_id) ON Comments.id = comment_id WHERE book_id=(?) ORDER BY avg_rating DESC", (bookID,))
        comments = cur.fetchmany(int(request.args.get('numRows')))
    return render_template("view_book.html", book=row, comment_list = comments, author_list = authors)

@app.route("/view-author")
def viewAuthor():
    if not request.args.get('authorID'):
        flash("Error getting author.")
        return redirect(request.referrer)
    authorID = int(request.args.get('authorID'))
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Authors WHERE id = (?)", (authorID,))
    row = cur.fetchone()
    cur.execute("SELECT * FROM AuthorWrites INNER JOIN Books ON AuthorWrites.book_id = Books.id WHERE author_id = (?);", (authorID,))
    booksByAuthor = cur.fetchall()
    cur.execute("SELECT * FROM Books INNER JOIN (SELECT book_id FROM AuthorWrites INNER JOIN (SELECT co_author_id FROM OneDegreeAuthors WHERE author_id=(?)) AS C ON AuthorWrites.author_id = C.co_author_id WHERE book_id NOT IN (SELECT book_id FROM AuthorWrites WHERE author_id=(?))) ON Books.id = book_id;", (authorID,authorID))
    booksBy1DegreeAuthor = cur.fetchall()
    cur.execute("SELECT * FROM Books INNER JOIN AuthorWrites ON Books.id = book_id INNER JOIN (SELECT B.co_author_id FROM OneDegreeAuthors AS A INNER JOIN OneDegreeAuthors AS B ON A.co_author_id=B.author_id WHERE A.author_id=(?) AND B.co_author_id NOT IN (SELECT co_author_id FROM OneDegreeAuthors WHERE author_id=(?)) AND B.co_author_id!=(?) GROUP BY B.co_author_id) ON author_id=co_author_id;", (authorID, authorID, authorID))
    booksBy2DegreeAuthor = cur.fetchall()
    return render_template("view_author.html", author=row, book_list_author=booksByAuthor, book_list_1degree=booksBy1DegreeAuthor, book_list_2degree=booksBy2DegreeAuthor)

@app.route('/cart', methods = ['POST', 'GET'])
def cart():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        if request.method == 'POST':
            if request.form.get('addr_id'):
                addrID = request.form['addr_id']
                cur.execute("SELECT * FROM Addresses WHERE id = (?);", (addrID,))
                if not cur.fetchone():
                    flash("Address invalid.")
                    return redirect(url_for('cart'))
                cur.execute("SELECT * FROM Customers WHERE user_id = (?)", (userID,))
                if not cur.fetchone():
                    flash("Customer not registered.")
                    return redirect(url_for('updateCustomer'))
                else:
                    cur.execute("SELECT COUNT(*) as cnt FROM Orders")
                    row = cur.fetchone()
                    orderID = int(row['cnt']) + 1
                    cur.execute("INSERT INTO Orders (id, ships_to, placed_by) VALUES ((?), (?), (?));", (orderID, addrID, userID))
                    cur.execute("SELECT COUNT(*) as cnt FROM OrderItems")
                    row = cur.fetchone()
                    itemID = int(row['cnt']) + 1
                    cur.execute("SELECT * FROM Cart WHERE user_id = (?)", (userID,))
                    rows = cur.fetchall()
                    for row in rows:
                        cur.execute("INSERT INTO OrderItems (id, quantity, book_id, order_id) VALUES ((?), (?), (?), (?));", (itemID, row['quantity'], row['book_id'], orderID))
                        itemID += 1
                    conn.commit()
                    flash("Successfully placed order.")
                    return redirect(url_for('home'))
            else:
                flash("Select a valid address.")
                return redirect(request.referrer)
        else:
            cur.execute("SELECT * FROM Books INNER JOIN Cart ON Books.id = Cart.book_id WHERE Cart.user_id = (?)", (userID,))
            books = cur.fetchall()
            if not books:
                flash("No books found in cart.")
            cur.execute("SELECT * FROM Addresses WHERE user_id = (?)", (userID,))
            addr = cur.fetchall()
            return render_template('cart.html', book_list = books, addr_list = addr)

@app.route('/update-item', methods = ['POST'])
def updateItem():
    if request.method == 'POST':
        if not request.form.get('bookID') or not request.form.get('quantity'):
            flash("Error updating item.")
            return redirect(url_for('home'))
        bookID = request.form['bookID']
        quantity = int(request.form['quantity'])
        if not session.get('user_id'):
            return redirect(url_for('login'))
        userID = session['user_id']
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Cart WHERE book_id = (?) AND user_id = (?)", (bookID, userID))
        row = cur.fetchone()
        if row is None:
            if quantity == 0:
                return redirect(url_for('cart'))
            else:
                cur.execute("INSERT INTO Cart (book_id, user_id, quantity) VALUES ((?), (?), (?))", (bookID, userID, 1))
        else:
            if quantity == 0:
                cur.execute("DELETE FROM Cart WHERE book_id = (?) AND user_id = (?)", (bookID, userID))
            else:
                cur.execute("UPDATE Cart SET quantity = (?) WHERE book_id = (?) AND user_id = (?)", (quantity, bookID, userID))
        conn.commit()
        return redirect(url_for('cart'))

@app.route('/my-trusted-users', methods = ['POST', 'GET'])
def myTrustedUsers():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session.get('user_id')
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        if request.method == 'POST':
            if not request.form.get('value') or not request.form.get('user_id'):
                flash("Error trusting customer.")
                return redirect(request.referrer)
            else:
                trusts = request.form['user_id']
                cur.execute("SELECT * FROM Trusts WHERE user_id=(?) AND trusts=(?);", (userID, trusts))
                if not cur.fetchone():
                    cur.execute("INSERT INTO Trusts (user_id, trusts, value) VALUES ((?), (?), (?));", (userID, trusts, request.form['value']))
                else:
                    cur.execute("UPDATE Trusts SET value=(?) WHERE user_id=(?) AND trusts=(?);", (request.form['value'], userID, trusts))
                conn.commit()
                flash("Successfully modified trust.")
                return redirect(request.referrer)
        cur.execute("SELECT value, username FROM Trusts INNER JOIN Users ON Trusts.trusts = Users.id WHERE Trusts.user_id = (?)", (userID,))
        rows = cur.fetchall()
        return render_template("my_trusted_users.html", user_list = rows)

@app.route('/update-rating', methods = ['POST'])
def updateRating():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session.get('user_id')
        if not request.form.get('comment_id'):
            flash("Error rating comment.")
            return redirect(request.referrer)
        commentID = request.form['comment_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Comments WHERE id=(?)", (commentID,))
        row = cur.fetchone()
        if row['user_id'] == userID:
            flash("You cannot rate your own comment!")
            return redirect(request.referrer)
        cur.execute("SELECT * FROM Ratings WHERE user_id = (?) AND comment_id = (?);", (userID, commentID))
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO Ratings (user_id, comment_id, value) Values((?), (?), (?));", (userID, commentID, request.form['value']))
        else:
            cur.execute("UPDATE Ratings SET value = (?) WHERE user_id = (?) AND comment_id = (?);", (request.form['value'], userID, commentID))
        conn.commit()
        flash("Rating updated.")
        return redirect(request.referrer)

@app.route('/search', methods = ['GET'])
def search():
    if not request.args:
        return render_template("search.html")
    else:
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        title = "%%"; author = "%%"; publisher = "%%"; language = "%%"
        if not request.args.get('sort'):
            flash("Missing Sort.")
            return render_template("search.html")
        sort = int(request.args.get('sort'))
        if not request.args.get('numRows'):
            numRows = 20
        else:
            numRows = int(request.args.get('numRows'))
        if request.args.get('title'):
            title = "%" + request.args.get('title') + "%"
        if request.args.get('publisher'):
            publisher = "%" + request.args.get('publisher') + "%"
        if request.args.get('language'):
            language = "%" + request.args.get('language') + "%"
        if request.args.get('author'):
            author = "%" + request.args.get('author') + "%"
            if sort == 1:
                cur.execute("SELECT * FROM Books INNER JOIN AuthorWrites ON Books.id=AuthorWrites.book_id INNER JOIN Authors ON Authors.id=AuthorWrites.author_id WHERE name LIKE (?) AND title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id ORDER BY pub_date ASC;", (author, title, publisher, language))
            elif sort == 2:
                cur.execute("SELECT * FROM Books INNER JOIN AuthorWrites ON Books.id=AuthorWrites.book_id INNER JOIN Authors ON Authors.id=AuthorWrites.author_id WHERE name LIKE (?) AND title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id ORDER BY pub_date DESC;", (author, title, publisher, language))
            elif sort == 3:
                cur.execute("SELECT * FROM Books INNER JOIN AuthorWrites ON Books.id=AuthorWrites.book_id INNER JOIN Authors ON Authors.id=AuthorWrites.author_id INNER JOIN (SELECT book_id, AVG(score) AS avg_rating FROM Comments GROUP BY book_id) AS X ON X.book_id=Books.id WHERE name LIKE (?) AND title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id;", (author, title, publisher, language))
            elif sort == 4:
                cur.execute("SELECT * FROM Books INNER JOIN AuthorWrites ON Books.id=AuthorWrites.book_id INNER JOIN Authors ON Authors.id=AuthorWrites.author_id  INNER JOIN (SELECT book_id, AVG(score) AS avg_rating FROM Comments INNER JOIN TrustedUsers ON user_id GROUP BY book_id) AS X ON X.book_id=Books.id WHERE name LIKE (?) AND title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id;", (author, title, publisher, language))
            else:
                flash("Error Sorting.")
                return render_template("search.html")
        else:
            if sort == 1:
                cur.execute("SELECT * FROM Books WHERE title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id ORDER BY pub_date ASC;", (title, publisher, language))
            elif sort == 2:
                cur.execute("SELECT * FROM Books WHERE title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id ORDER BY pub_date DESC;", (title, publisher, language))
            elif sort == 3:
                cur.execute("SELECT * FROM Books INNER JOIN (SELECT book_id, AVG(score) AS avg_rating FROM Comments GROUP BY book_id) ON book_id=Books.id WHERE title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id ORDER BY avg_rating DESC;", (title, publisher, language))
            elif sort == 4:
                cur.execute("SELECT * FROM Books INNER JOIN (SELECT book_id, AVG(score) AS avg_rating FROM Comments INNER JOIN TrustedUsers ON Comments.user_id=TrustedUsers.user_id GROUP BY book_id) ON book_id=Books.id WHERE title LIKE (?) AND publisher LIKE (?) AND language LIKE (?) GROUP BY Books.id ORDER BY pub_date DESC;", (title, publisher, language))
            else:
                flash("Error Sorting.")
                return render_template("search.html")
        books = cur.fetchmany(numRows)
        return render_template("search.html", book_list = books)
    

@app.route('/my-orders', methods = ['POST', 'GET'])
def myOrders():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session.get('user_id')
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Orders INNER JOIN Addresses ON Orders.ships_to = Addresses.id INNER JOIN Customers ON Customers.user_id = Addresses.user_id INNER JOIN OrderItems ON OrderItems.order_id = Orders.id INNER JOIN Books ON OrderItems.book_id = Books.id WHERE Customers.user_id = (?);", (userID,))
        rows = cur.fetchall()
        if not rows:
            flash("No orders found.")
        for row in rows:
            print(row['title'])
        return render_template('orders.html', orders = rows)

@app.route('/my-addresses', methods = ['POST', 'GET'])
def myAddresses():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        if request.method == 'POST':
            if not request.form.get('street_number') or not request.form.get('street_name') or not request.form.get('city') or not request.form.get('zip_code') or not request.form.get('region') or not request.form.get('country'):
                flash("All fields but apartment number are required.")
                return redirect(url_for('myAddresses'))
            else:
                streetNo = request.form['street_number']
                streetName = request.form['street_name']
                city = request.form['city']
                zipCode = request.form['zip_code']
                region = request.form['region']
                country = request.form['country']
                if not request.form.get('apt_number'):
                    aptNo = None
                else:
                    aptNo = request.form['apt_number']
                cur.execute("SELECT COUNT(*) AS cnt FROM Addresses")
                row = cur.fetchone()
                numAddr = int(row['cnt'])
                cur.execute("INSERT INTO Addresses (id, street_number, street_name, apt_number, zip_code, city, region, country, user_id) VALUES((?),(?), (?), (?), (?), (?), (?), (?), (?))", (numAddr+1, streetNo, streetName, aptNo, zipCode, city, region, country, userID))
                conn.commit()
                flash("Successfull added new address.")
                return redirect(url_for('myAddresses'))
        else:
            cur.execute("SELECT * FROM Addresses WHERE user_id=(?)", (userID,))
            addr = cur.fetchall()
            return render_template('addresses.html', addr_list=addr)

@app.route('/my-comments', methods = ['GET'])
def myComments():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT id, first_name, last_name, score, content, Comments.timestamp, avg_rating, Comments.user_id FROM Comments INNER JOIN Customers ON Comments.user_id = Customers.user_id LEFT JOIN (SELECT AVG(Ratings.value) as avg_rating, comment_id FROM Ratings GROUP BY comment_id) ON Comments.id = comment_id WHERE Comments.user_id=(?) ORDER BY avg_rating", (userID,))
        comments = cur.fetchall()
        if not comments:
            flash("No comments found.")
        return render_template('my_comments.html', comment_list=comments)

@app.route('/update-comment', methods = ['GET', 'POST'])
def updateComment():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        if request.method == 'POST':
            if not request.form.get('score') or not request.form.get('book_id'):
                flash("Error recording comment.")
                return redirect(request.referrer)
            cur.execute("SELECT * FROM Customers WHERE user_id=(?);", (userID,))
            row = cur.fetchone()
            if not row:
                flash("You must be registered as a customer!")
                return redirect(url_for('updateCustomer'))
            score = request.form['score']
            bookID = request.form['book_id']
            if not request.form.get('comment_id'):
                cur.execute("SELECT * FROM Comments WHERE book_id=(?) AND user_id=(?)", (bookID, userID))
                if cur.fetchone():
                    flash("Comment has already been left on this book.")
                    return redirect(request.referrer)
                if not request.form['content']:
                    cur.execute("INSERT INTO Comments (score, book_id, user_id) VALUES ((?), (?), (?));", (score, bookID, userID))
                else:
                    cur.execute("INSERT INTO Comments (content, score, book_id, user_id) VALUES ((?), (?), (?), (?));", (request.form['content'], score, bookID, userID))
                conn.commit()
                return redirect(request.referrer)
            else:
                cur.execute("UPDATE Comments SET content=(?), score=(?) WHERE id=(?);", (request.form['content'], score, request.form['comment_id']))
                conn.commit()
                flash("Comment successfully updated.")
                return redirect(request.referrer)
        else:
            if not request.args.get('commentID'):
                flash("Error finding comment.")
                return redirect(url_for('myComments'))
            cur.execute("SELECT * FROM Comments WHERE id=(?);", (request.args.get('commentID'),))
            comment = cur.fetchone()
            cur.execute("SELECT title, id FROM Books WHERE id=(?);", (comment['book_id'],))
            book = cur.fetchone()
            return render_template('update_comment.html', comment = comment, book = book)

# ACCESS FOR EMPLOYEES ONLY
@app.route('/orders', methods = ['POST'])
def orders():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE id = (?)", (userID,))
        row = cur.fetchone()
        if row is None:
            flash("You must be logged in!")
            return redirect(url_for('login'))
        elif row['role'] == "default":
            flash("You do not have permission!")
            return redirect(url_for('login'))
        elif row['role'] == "employee" or row['role'] == "manager":
            cur.execute("SELECT * FROM Orders INNER JOIN Addresses ON Orders.ships_to = Addresses.id INNER JOIN Customers ON Customers.user_id = Addresses.user_id INNER JOIN OrderItems ON OrderItems.order_id = Orders.id INNER JOIN Books ON OrderItems.book_id = Books.id WHERE time_fulfilled IS NULL;")
            rows = cur.fetchall()
            flash("Viewing unfulfilled Orders")
            return render_template('orders.html', orders = rows)

# Access for managers only.
@app.route('/update-customer', methods = ['POST', 'GET'])
def updateCustomer():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE id = (?)", (userID,))
        row = cur.fetchone()
        if row is None:
            flash("You must be logged in!")
            return redirect(url_for('login'))
        if request.method == 'POST':
            if not request.form.get('phone') or not request.form.get('first_name') or not request.form.get('last_name'):
                flash("All fields required.")
                return redirect(url_for('update_customer'))
            cur.execute("SELECT * FROM Customers WHERE user_id = (?)", (userID,))
            row = cur.fetchone()
            if row is None:
                cur.execute("INSERT INTO Customers (user_id, phone, first_name, last_name) VALUES((?), (?), (?), (?))", (userID, request.form['phone'], request.form['first_name'], request.form['last_name']))
            else:
                cur.execute("UPDATE Customers SET phone=(?), first_name=(?), last_name=(?) WHERE user_id = (?)", (request.form['phone'], request.form['first_name'], request.form['last_name'], userID))
            conn.commit()
            cur.execute("SELECT * FROM Customers WHERE user_id = (?);", (userID,))
            row = cur.fetchone()
            flash("Successfully updated your information.")
            return render_template('update_customer.html', customer = row)
        else:
            cur.execute("SELECT * FROM Customers WHERE user_id = (?);", (userID,))
            row = cur.fetchone()
            return render_template('update_customer.html', customer = row)

# ACCESS FOR MANAGERS ONLY 
@app.route('/update-user', methods = ['POST', 'GET'])
def updateUser():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if request.method == 'POST':
            if not request.args.get('username') or not request.args.get('email') or not request.args.get('userID') or not request.args.get('role'):
                flash("Error updating user.")
                return redirect(request.referrer)
            cur.execute("UPDATE Users SET username=(?), email=(?), role=(?) WHERE id=(?);", (request.args.get('username'),request.args.get('email'),request.args.get('role'),request.args.get('userID')))
            conn.commit()
            return redirect(request.referrer)
        else:
            if not request.args.get('userID'):
                flash("Error updating user.")
                return redirect(request.referrer)
            cur.execute("SELECT * FROM Users WHERE id=(?)", (request.args.get('userID'),))
            row = cur.fetchone()
            return render_template("update_user.html", user=row)
            

@app.route('/update-book', methods = ['POST', 'GET'])
def updateBook():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if request.method == 'POST':
            if not request.form['title'] or not request.form['isbn13'] or not request.form['language'] or not request.form['pub_date'] or not request.form['publisher'] or not request.form['price'] or not request.form['stock']:
                flash("Required fields missing.")
                return redirect(url_for('updateBook'))
            if not request.form['id']:
                cur.execute("INSERT INTO Books (title, isbn, isbn13, language, num_pages, pub_date, publisher, price, stock) VALUES ((?), (?), (?), (?), (?), (?), (?), (?))", (request.form['title'], request.form['isbn'], request.form['isbn13'], request.form['language'], request.form['num_pages'], request.form['pub_date'], request.form['publisher'], request.form['price'], request.form['stock']))
            else:
                cur.execute("UPDATE Books SET title=(?), isbn=(?), isbn13=(?), language=(?), num_pages=(?), pub_date=(?), publisher=(?), price=(?), stock=(?) WHERE id=(?);", (request.form['title'], request.form['isbn'], request.form['isbn13'], request.form['language'], request.form['num_pages'], request.form['pub_date'], request.form['publisher'], request.form['price'], request.form['stock'], request.form['id']))
            conn.commit()
            return redirect(url_for('updateBook'))
        else:
            if request.args.get('bookID'):
                cur.execute("SELECT * FROM Books WHERE id=(?)", (request.args.get('bookID'),))
                row = cur.fetchone()
                return render_template('update_book.html', book = row)
            else:
                return render_template('update_book.html')
        
@app.route('/update-author', methods = ['POST', 'GET'])
def updateAuthor():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?);", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if request.method == 'POST':
            if not request.form['name']:
                flash("Name is a required field.")
                return redirect(request.referrer)
            name = request.form['name']
            if not request.form['id']:
                cur.execute("INSERT INTO Authors (name) VALUES ((?));", (name,))
            else:
                cur.execute("UPDATE Authors SET name=(?) WHERE id=(?);", (name, request.form['id']))
            conn.commit()
            return redirect(request.referrer)
        else:
            if request.args.get('authorID'):
                authorID = request.args.get('authorID')
                cur.execute("SELECT * FROM Authors WHERE id=(?)", (authorID,))
                row = cur.fetchone()
                cur.execute("SELECT * FROM Books INNER JOIN AuthorWrites ON Books.id=AuthorWrites.book_id WHERE AuthorWrites.author_id=(?);", (authorID,))
                books = cur.fetchall()
                return render_template('update_author.html', author = row, book_list = books)
            else:
                return render_template('update_author.html')

@app.route('/update-author-writes', methods = ['POST'])
def updateAuthorWrites():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if not request.form['isbn13'] or not request.form['author_id']:
            flash("Error updating author.")
            return redirect(request.referrer)
        cur.execute("SELECT * FROM Books WHERE isbn13=(?);", (request.form['isbn13'],))
        row = cur.fetchone()
        if not row:
            flash("Error updating author.")
            return redirect(request.referrer)
        bookID = row['id']
        cur.execute("INSERT INTO AuthorWrites (author_id, book_id) VALUES ((?), (?));", (request.form['author_id'], bookID))
        conn.commit()
        return redirect(url_for('viewBook', bookID=bookID))

@app.route('/get-top-useful', methods = ['GET'])
def getTopUseful():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if not request.args.get('num_rows'):
            numRows = 5
        else:
            numRows = int(request.args['num_rows'])
        cur.execute("SELECT * FROM CommentRating INNER JOIN Customers INNER JOIN Users ON Customers.user_id=Users.id GROUP BY CommentRating.user_id ORDER BY avg_rating DESC;")
        customers = cur.fetchmany(numRows)
        return render_template('get_top_useful.html', customer_list = customers)


@app.route('/get-top-trusted', methods = ['GET'])
def getTopTrusted():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if not request.args.get('num_rows'):
            numRows = 5
        else:
            numRows = int(request.args['num_rows'])
        cur.execute("SELECT * FROM TrustRating INNER JOIN Customers ON TrustRating.user_id=Customers.user_id INNER JOIN Users ON Customers.user_id=Users.id GROUP BY TrustRating.user_id ORDER BY score DESC;")
        customers = cur.fetchmany(numRows)
        return render_template('get_top_trusted.html', customer_list = customers)

@app.route('/get-popular-books', methods = ['GET'])
def getPopularBooks():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if not request.args.get('num_rows'):
            numRows = 10
        else:
            numRows = int(request.args['num_rows'])
        if not request.args.get('quarter'):
            quarter = 0
        else:
            quarter = int(request.args['quarter'])
        cur.execute("SELECT * FROM BookStats INNER JOIN Books ON BookStats.id=Books.id WHERE order_quarter=(?) ORDER BY copies_sold DESC", (quarter,))
        rows = cur.fetchmany(numRows)
        for row in rows:
            print(row['title'])
        return render_template('get_popular_books.html', book_list=rows)

@app.route('/get-popular-authors', methods = ['GET'])
def getPopularAuthors():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if not request.args.get('num_rows'):
            numRows = 10
        else:
            numRows = int(request.args['num_rows'])
        if not request.args.get('quarter'):
            quarter = 0
        else:
            quarter = int(request.args['quarter'])
        cur.execute("SELECT Authors.id, name, SUM(copies_sold) AS copies_sold, order_quarter FROM BookStats INNER JOIN Books ON BookStats.id=Books.id INNER JOIN AuthorWrites ON Books.id=AuthorWrites.book_id INNER JOIN Authors ON AuthorWrites.author_id=Authors.id WHERE order_quarter=(?) GROUP BY name ORDER BY SUM(copies_sold) DESC", (quarter,))
        rows = cur.fetchmany(numRows)
        return render_template('get_popular_authors.html', author_list=rows)


@app.route('/get-popular-publishers', methods = ['GET'])
def getPopularPublishers():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if not request.args.get('num_rows'):
            numRows = 10
        else:
            numRows = int(request.args['num_rows'])
        if not request.args.get('quarter'):
            quarter = 0
        else:
            quarter = int(request.args['quarter'])
        cur.execute("SELECT Books.publisher, SUM(copies_sold) AS copies_sold, order_quarter FROM BookStats INNER JOIN Books ON BookStats.id=Books.id WHERE order_quarter=(?) GROUP BY BookStats.publisher ORDER BY SUM(copies_sold) DESC", (quarter,))
        rows = cur.fetchmany(numRows)
        return render_template('get_popular_publishers.html', publisher_list=rows)


@app.route('/sales', methods = ['GET'])
def sales():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        if request.method == 'POST':
            if not request.args.get('username') or not request.args.get('email') or not request.args.get('userID') or not request.args.get('role'):
                flash("Error updating user.")
                return redirect(request.referrer)
            cur.execute("UPDATE Users SET username=(?), email=(?), role=(?) WHERE id=(?);", (request.args.get('username'),request.args.get('email'),request.args.get('role'),request.args.get('userID')))
            conn.commit()
            return redirect(request.referrer)
        else:
            if not request.args.get('saleID'):
                flash("Error updating user.")
                return redirect(request.referrer)
            cur.execute("SELECT * FROM Users WHERE id=(?)", (request.args.get('userID'),))
            row = cur.fetchone()
            return render_template("update_user.html", user=row)

@app.route('/discounts', methods = ['GET'])
def discounts():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))

@app.route('/manager-panel', methods = ['GET'])
def managerPanel():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT role FROM Users WHERE id=(?)", (userID,))
        row = cur.fetchone()
        if not row or row['role'] != "manager":
            flash("You do not have permission for this!")
            return redirect(url_for('login'))
        return render_template('manager_panel.html')

if __name__ == "__main__":
    app.secret_key = 'SECRETKEYDONTLOSE'
    app.run(debug=True)